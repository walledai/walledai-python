"""

importing  requests module
"""

import requests
import json
import time
from walledai.constants import base_url
from walledai.custom_types.guardrail import GuardRailResponse
from typing import List
from typing_extensions import Literal
class WalledProtect:
    ''' Walled Protect '''
    count=1
    url=f'{base_url}/guardrail/moderate'
    def __init__(self,api_key:str,retries:int=2,timeout:float=20.0):
        """
        Initialize the WalledProtect client.

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
    def guardrail(
        self,
        text: str,
        greetings_list: List[str]=["Casual & Friendly"],
        text_type: str = "prompt",
        generic_safety_check: bool = True,
        compliance: List[str] = [],
        pii: List[Literal["Person's Name", "Address", "Email Id", "Contact No", "Date Of Birth","Unique Id","Financial Data"]] = []
    ) -> GuardRailResponse:
        """
        Runs guardrails on the given input text to evaluate safety, PII, compliance, and greetings.

        This method sends a request to the Walled AI API and returns a structured response
        indicating whether the input passes various checks.

        Args:
            text (str): The input text to evaluate.
            greetings_list (list[str]): A list of greeting category strings to match against. ex : ["Casual & Friendly", "Formal", "Professional"]. Defaults to ["Casual & Friendly"].
            text_type (str, optional): The type of input text (e.g., "prompt", "completion"). Defaults to "prompt".
            generic_safety_check (bool, optional): Whether to enable general safety filters. Defaults to True.
            compliance_list (list[str], optional): A list of compliance categories to check against. Defaults to an empty list.
            pii_list (list[str], optional): A list of PII categories to check against. Defaults to an empty list.

        Returns:
            GuardRailResponse: An object containing the evaluation results, including safety scores,
            greeting matches, and compliance or PII flags.
        If the request fails, a dictionary is returned with:
            - `success` (bool): Always False
            - `error` (str): The error message explaining the failure

        Notes:
            - The method will retry on failure up to the number of retries configured in the client.
            - If all retries fail, the final response will contain an error message instead of throwing an exception.

        """
        # Allowed PII values
        allowed_pii = {
            "Person's Name", "Address", "Email Id", "Contact No", "Date Of Birth", "Unique Id", "Financial Data"
        }
        if pii and not all(item in allowed_pii for item in pii):
            raise ValueError(f"'pii' must be empty or contain only: {sorted(allowed_pii)}")
        try:
            request_body=json.dumps({
                "text":text,
                "text_type":text_type,
                "generic_safety_check": generic_safety_check,
	            "greetings_list": greetings_list,
                "compliance_list": compliance ,
                "pii_list": pii 
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
                return self.guardrail(text,greetings_list)
            else:
                print("Reached Maximum No of retries \n")
                return {"success":False,"error":e}