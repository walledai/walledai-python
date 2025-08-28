"""

importing aiohttp module
"""
import json
import asyncio
import aiohttp
import time
from walledai.constants import base_url
from walledai.custom_types.pii import PIIResponse
from walledai.custom_types.guardrail import TextInput
from typing import List, Union

class WalledRedact:
    ''' Redact'''
    count=1
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
        self.url=f'{base_url}/walled-redact'

        
    async def _http_api_call(self, session, text):
        """Make HTTP API call"""
        payload = {
            "text": text
        }
        
        headers = {
            "Content-Type": "application/json",
            "x-api-key":  self.api_key
        }
        async with session.post(self.url, json=payload, headers=headers) as response:
            resp_json = await response.json()
            if response.status != 200:
                raise Exception(resp_json)
            return resp_json
    def guard(self,text: Union[str, List[TextInput]])->PIIResponse:
        """
        Runs PII detection on the given input text to identify and format personal identifiable information.

        This method sends a request to the Walled AI API and returns a structured response
        containing PII formatted data.

        Args:
            text (str or list[TextInput]): The input text to evaluate. Can be a single string or a list of TextInput dicts for multi-turn or structured input.
                TextInput format: {"role": str, "content": str}

        Returns:
            PIIResponse: An object containing the evaluation results, including PII detection and formatting.

        If the request fails, a dictionary is returned with:
            - `success` (bool): Always False
            - `error` (str): The error message explaining the failure

        Notes:
            - The method will retry on failure up to the number of retries configured in the client.
            - If all retries fail, the final response will contain an error message instead of throwing an exception.

        """
        
        def run_async_guard():
            async def _async_guard():
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                    response = await self._http_api_call(session, text)
                    return response
            return asyncio.run(_async_guard())

        for attempt in range(self.retries):
            try:
                return run_async_guard()
            except Exception as e:
                print('Failed , error : ', e)
                print('\nRetrying ... \n')
                if attempt < self.retries - 1:
                    time.sleep(2)
                else:
                    print("Reached Maximum No of retries \n")
                    return e    