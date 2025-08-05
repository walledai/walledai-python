"""

importing aiohttp module
"""
import json
import asyncio
import aiohttp
import time
from walledai.constants import base_url
from walledai.custom_types.pii import PIIResponse
class WalledRedact:
    ''' Redact'''
    count=1
    url=f'{base_url}/pii/encrypt'
    def __init__(self,api_key:str,retries:int=2,timeout:float=20.0):
        """
        Initialize the PII client.

        This sets up the client with the required API key and optional configurations
        for request retry logic and timeout behavior.

        Args:
            api_key (str): The API key obtained from Walled AI.
            retries (int, optional): Number of retry attempts in case of request failure.
                If a request fails (e.g., due to a network error or server issue), the client
                will automatically retry the request up to the specified number of times.
                Defaults to 2.
            timeout (float, optional): Maximum time (in seconds) to wait for a response from the server
                before aborting the request. Applies to both connection and read timeouts.
                Defaults to 20.0 seconds.
        """
        
        self.api_key = api_key
        self.retries=retries  
        self.timeout=timeout
        
    async def _http_api_call(self, session, text):
        """Make HTTP API call"""
        url = f"{base_url}/pii/encrypt"
        payload = {
            "text": text
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            async with session.post(url, json=payload, headers=headers) as response:
                resp_json = await response.json()
                return resp_json
        except Exception as e:
            raise e
    def guard(self,text:str)->PIIResponse:
        """
        Runs pii on the given input text to evaluate safety.

        This method sends a request to the Walled AI API and returns a structured response
        indicating with PII formatted data.

        Args:
            text (str): The input text to evaluate.

        Returns:
            PIIResponse: An object containing the evaluation results, including safety scores,
            greeting matches, and compliance or PII flags.

        If the request fails, a dictionary is returned with:
            - `success` (bool): Always False
            - `error` (str): The error message explaining the failure

        Notes:
            - The method will retry on failure up to the number of retries configured in the client.
            - If all retries fail, the final response will contain an error message instead of throwing an exception.

        """
        
        async def _async_guard():
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                    response = await self._http_api_call(session, text)
                    return {"success": True, "data": response.get("data", {})}
            except Exception as e:
                raise e
        
        try:
            return asyncio.run(_async_guard())
        except Exception as e:
            print('Failed , error : ', e)
            print('\nRetrying ... \n')
            if self.count < self.retries:
                self.count += 1
                time.sleep(2)
                return self.guard(text)
            else:
                print("Reached Maximum No of retries \n")
                return {"success": False, "error": str(e)}
