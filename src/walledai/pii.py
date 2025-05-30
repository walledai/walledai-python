"""

importing  requests module
"""
import requests
import json
import time
from walledai.constants import base_url
from walledai.custom_types.pii import PIIResponse
class PII:
    ''' PII'''
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
    def pii(self,text:str)->PIIResponse:
        """
        Runs pii on the given input text to evaluate safety.

        This method sends a request to the Walled AI API and returns a structured response
        indicating with PII formated data.

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
        try:
            request_body=json.dumps({
                "text":text
            })
            headers={"Authorization": f"Bearer {self.api_key}", 'Content-Type': 'application/json'}
            response = requests.request("POST", self.url, headers=headers, data=request_body,timeout=self.timeout)
            #response=requests.post(self.url,data=request_body,,headers=headers)
            response.raise_for_status()
            return {"success":True,"data":dict(response.json())["data"]}
        except  Exception as e:
            print('Failed , error : ', e)
            print('\nRetrying ... \n')
            if self.count<self.retries:
                self.count+=1
                time.sleep(2)
                return self.pii(text)
            else:
                print("Reached Maximum No of retries \n")
                return {"success":False,"error":e}
