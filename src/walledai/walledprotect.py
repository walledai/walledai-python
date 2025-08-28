"""

importing aiohttp module
"""

import asyncio
import csv
import os
import aiohttp
import time

from pandas import api
from walledai.constants import base_url
from walledai.custom_types.guardrail import GuardRailResponse, TextInput
from typing import List, Union
from typing_extensions import Literal


class WalledProtect:
    ''' Walled Protect '''
    count = 1

    # Define enums for allowed PII and greetings columns
    PII_ENUM = {
        "Person's Name": "Person's Name",
        "Address": "Address",
        "Email Id": "Email Id",
        "Contact No": "Contact No",
        "Date Of Birth": "Date Of Birth",
        "Unique Id": "Unique Id",
        "Financial Data": "Financial Data"
    }
    GREETINGS_ENUM = {
        "Casual & Friendly": "Casual & Friendly",
        "Professional & Polite": "Professional & Polite"
        # Add more greetings types here if needed
    }

    def __init__(self, api_key: str, retries: int = 3, timeout: float = 20.0):
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
        self.retries = retries
        self.timeout = timeout
        self.url = f'{base_url}/walled-protect'


    async def _http_api_call(
        self,
        session,
        text,
        greetings_list: List[str] = ["Casual & Friendly", "Professional & Polite"],
        generic_safety_check: bool = True,
        compliance_list: List[str] = [],
        pii_list: List[Literal["Person's Name", "Address", "Email Id", "Contact No", "Date Of Birth", "Unique Id", "Financial Data"]] = []
    ):
        """Make HTTP API call"""
        payload = {
            "text": text,
            "greetings_list": greetings_list,  # ["Casual & Friendly", "Professional & Polite"],
            "generic_safety_check": generic_safety_check,
            "compliance_list": compliance_list,
            "pii_list": pii_list
        }

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key # Adjust as needed for your API
        }

        async with session.post(self.url, json=payload, headers=headers) as response:
            resp_json = await response.json()
            if response.status != 200:
                raise Exception(resp_json)  # raise the JSON directly
            return resp_json
    # added guard
    def guard(
        self,
        text: Union[str, List[TextInput]],
        greetings_list: List[str] = ["Casual & Friendly"],
        generic_safety_check: bool = True,
        compliance_list: List[str] = [],
        pii_list: List[Literal["Person's Name", "Address", "Email Id", "Contact No", "Date Of Birth", "Unique Id", "Financial Data"]] = []
    ) -> GuardRailResponse:
        """
        Runs guardrails on the given input text(s) to evaluate safety, PII, compliance, and greetings.

        This method sends a request to the Walled AI HTTP API and returns a structured response.

        Args:
            text (str or list[TextInput]): The input text to evaluate. Can be a single string or a list of TextInput dicts for multi-turn or structured input.
            greetings_list (list[str], optional): A list of greeting category strings to match against. ex: ["Casual & Friendly", "Formal", "Professional"]. Defaults to ["Casual & Friendly"].
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
        if pii_list and not all(item in allowed_pii for item in pii_list):
            raise ValueError(f"'pii' must be empty or contain only: {sorted(allowed_pii)}")

        def run_async_guard():
            async def _async_guard():
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                    response = await self._http_api_call(
                        session,
                        text=text,
                        greetings_list=greetings_list,
                        generic_safety_check=generic_safety_check,
                        compliance_list=compliance_list,
                        pii_list=pii_list
                    )
                    return response#{"success": True, "data": response.get("data", {})}
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

    def _extract_dynamic_columns_from_response(self, response_data):
        """Extract unique PII and greeting types from a response."""
        data = response_data.get("data", {})
        pii_types = []
        greeting_types = []
        if "pii" in data and isinstance(data["pii"], list):
            for pii_item in data["pii"]:
                pii_type = pii_item.get("pii_type")
                if pii_type and pii_type not in pii_types:
                    pii_types.append(pii_type)
        if "greetings" in data and isinstance(data["greetings"], list):
            for greeting in data["greetings"]:
                greeting_type = greeting.get("greeting_type")
                if greeting_type and greeting_type not in greeting_types:
                    greeting_types.append(greeting_type)
        return pii_types, greeting_types

    def _validate_csv_headers(self, headers):
        """
        Validate that CSV headers are within the allowed set.

        Args:
            headers (list): List of column names from CSV header row

        Returns:
            tuple: (is_valid, error_message) where is_valid is boolean and error_message is string
        """
        # Define allowed columns
        required_columns = {"test_input", "compliance_topic", "compliance_isOnTopic"}
        optional_columns = {
            "Person's Name", "Address", "Email Id", "Contact No",
            "Date Of Birth", "Unique Id", "Financial Data",
            "Casual & Friendly", "Professional & Polite"
        }
        all_allowed_columns = required_columns.union(optional_columns)

        # Check for missing required columns
        missing_required = required_columns - set(headers)
        if missing_required:
            return False, f"Missing required columns: {sorted(missing_required)}"

        # Check for invalid columns
        invalid_columns = set(headers) - all_allowed_columns
        if invalid_columns:
            return False, f"Invalid columns found: {sorted(invalid_columns)}. Allowed columns are: {sorted(all_allowed_columns)}"

        return True, ""

    def _extract_dynamic_columns_from_csv(self, ground_truth_file_path):
        """Extract dynamic PII and greetings columns from CSV header by matching with enums."""
        with open(ground_truth_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            headers = next(reader)  # Get just the headers

            # Validate headers first
            is_valid, error_message = self._validate_csv_headers(headers)
            if not is_valid:
                raise ValueError(f"CSV validation failed: {error_message}")

            # Extract column names that match our PII and Greetings enums
            pii_types = []
            greeting_types = []

            for col in headers:
                if col in self.PII_ENUM:
                    pii_types.append(col)
                elif col in self.GREETINGS_ENUM:
                    greeting_types.append(col)

            return pii_types, greeting_types

    def _load_guardrail_casesv2(self, ground_truth_file_path: str = "./unit_test_cases.csv"):
        cases = []
        with open(ground_truth_file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                cases.append(row)
        return cases

    async def _process_case_http(self, session, row, pii_types, greeting_types):
        """Process a single test case using HTTP API, dynamically selecting PII/greetings."""
        try:
            text = row['test_input']
            compliance_list = row['compliance_topic']

            # Dynamically select PII/greetings to check for this row
            # pii_list = [pii for pii in pii_types if row.get(pii, '').strip().upper() == "TRUE"]
            # greetings_list = [greet for greet in greeting_types if row.get(greet, '').strip().upper() == "TRUE"]

            # If no greetings are marked TRUE, default to all greeting_types (to match old behavior)
            # if not greetings_list:
            #     greetings_list = greeting_types

            response = await self._http_api_call(
                session,
                text,
                greetings_list=greeting_types,
                generic_safety_check=True,
                compliance_list=[compliance_list] if compliance_list else [],
                pii_list=pii_types
            )
            if not response or not isinstance(response, dict) or "data" not in response:
                print(f"Invalid response for '{text[:50]}...': {response}")
                return None

            def parse_response(response_data, pii_types, greeting_types):
                """Parse API response and extract relevant data for dynamic columns."""
                data = response_data.get("data", {})

                # Compliance
                compliance_isOnTopic = "FALSE"
                if "compliance" in data and isinstance(data["compliance"], list) and data["compliance"]:
                    compliance_isOnTopic = "TRUE" if data["compliance"][0].get("isOnTopic") else "FALSE"
                # Dynamic PII
                pii_results = {pii: "FALSE" for pii in pii_types}
                if "pii" in data and isinstance(data["pii"], list):
                    for pii_item in data["pii"]:
                        pii_type = pii_item.get("pii_type")
                        is_present = pii_item.get("isPresent")
                        if pii_type in pii_results:
                            pii_results[pii_type] = "TRUE" if is_present else "FALSE"

                # Dynamic Greetings
                greetings_results = {greet: "FALSE" for greet in greeting_types}
                if "greetings" in data and isinstance(data["greetings"], list):
                    for greeting in data["greetings"]:
                        greeting_type = greeting.get("greeting_type")
                        is_present = greeting.get("isPresent")
                        if greeting_type in greetings_results:
                            greetings_results[greeting_type] = "TRUE" if is_present else "FALSE"
                #safety=data.get("safety")[0].get("isSafe")
                safety_list = data.get("safety")
                if isinstance(safety_list, list) and safety_list and isinstance(safety_list[0], dict):
                    safety = safety_list[0].get("isSafe")
                else:
                    safety = None
                return {
                    "compliance_isOnTopic": compliance_isOnTopic,
                    "pii_results": pii_results,
                    "greetings_results": greetings_results,
                    "isSafe": "TRUE" if safety else "FALSE"
                }

            parsed = parse_response(response, pii_types, greeting_types)
            row_out = [
                text,
                compliance_list,
                parsed["compliance_isOnTopic"],
            ]
            row_out += [parsed["pii_results"][pii] for pii in pii_types]
            row_out += [parsed["greetings_results"][greet] for greet in greeting_types]
            row_out.append(parsed["isSafe"])
            return row_out
        except Exception as e:
            print(f"HTTP Error for '{row.get('test_input', '')[:50]}...': {e}")
            return None

    def _write_results(self, model_output_file_path, results, pii_types, greeting_types):
        RESULTS_CSV_PATH = model_output_file_path

        header = ["test_input", "compliance_topic", "compliance_isOnTopic"]
        header += pii_types
        header += greeting_types
        header.append("isSafe")

        with open(RESULTS_CSV_PATH, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
            writer.writerows(results)

    def _write_column_metrics_csv(self, ground_truth_file_path, model_output_file_path, metrics_output_file_path, pii_types, greeting_types):
        import pandas as pd
        from sklearn.metrics import confusion_matrix, accuracy_score

        gt_path = ground_truth_file_path  # os.path.join(os.path.dirname(__file__), 'unit_test_cases.csv')
        pred_path = model_output_file_path  # os.path.join(os.path.dirname(__file__), f'{method_name}_test_results.csv')
        out_path = metrics_output_file_path  # os.path.join(os.path.dirname(__file__), f'{method_name}_column_metrics.csv')

        if not os.path.exists(pred_path):
            print(f"Results file {pred_path} not found, skipping metrics calculation")
            return

        gt_df = pd.read_csv(gt_path)
        pred_df = pd.read_csv(pred_path)
        columns = ["compliance_isOnTopic"] + pii_types + greeting_types

        metrics_rows = []
        for col in columns:
            if col not in pred_df.columns or col not in gt_df.columns:
                continue
            y_pred = pred_df[col].astype(str).str.upper()
            y_true = gt_df[col].astype(str).str.upper()
            cm = confusion_matrix(y_true, y_pred, labels=['TRUE', 'FALSE'])
            accuracy = accuracy_score(y_true, y_pred)
            tn, fp, fn, tp = cm.ravel()
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0
            f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            metrics_rows.append([
                col, round(accuracy, 3), round(precision, 3), round(recall, 3), round(f1, 3), round(tp, 3), round(tn, 3), round(fp, 3), round(fn, 3)
            ])

        with open(out_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'metrics', 'accuracy', 'precision', 'recall', 'f1', 'TP', 'TN', 'FP', 'FN'
            ])
            writer.writerows(metrics_rows)

        print(f"Metrics written to {out_path}")

    async def eval(self, ground_truth_file_path: str, model_output_file_path: str, metrics_output_file_path: str, concurrency_limit: int = 10):
        """
        Evaluates the model output against the ground truth file using only HTTP API.

        Args:
            ground_truth_file (str): Path to the ground truth file.
            model_output_file (str): Path to the model output file.
            metrics_output_file (str): Path to the metrics output file.
            concurrency_limit (int): Maximum number of concurrent HTTP requests. Defaults to 10.
        Raises:
            Exception: If there is an error during the evaluation process, it will retry up to the specified number of retries.
        Returns:
            dict: A dictionary containing the evaluation results.
        """
        for attempt in range(self.retries):
            try:
                # Extract dynamic columns from CSV using enums (this will validate headers)
                pii_types, greeting_types = self._extract_dynamic_columns_from_csv(ground_truth_file_path)

                cases = self._load_guardrail_casesv2(ground_truth_file_path)
                if not cases:
                    print("No test cases found in the ground truth file.")
                    return {"success": False, "error": "No test cases found."}

                semaphore = asyncio.Semaphore(concurrency_limit)

                async def limited_process_case(case_func, *args):
                    async with semaphore:
                        return await case_func(*args)

                results = []
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30), connector=aiohttp.TCPConnector(limit=concurrency_limit)) as session:
                    tasks = [
                        limited_process_case(self._process_case_http, session, row, pii_types, greeting_types)
                        for row in cases
                    ]
                    print("Starting concurrent HTTP processing...")
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                valid_results = []
                error_count = 0
                for result in results:
                    if isinstance(result, Exception):
                        error_count += 1
                        print(f"Task failed with exception: {result}")
                    elif result is not None:
                        valid_results.append(result)
                    else:
                        error_count += 1

                print(f"Completed processing: {len(valid_results)} successful, {error_count} failed")

                # Writing results to csv
                self._write_results(model_output_file_path, valid_results, pii_types, greeting_types)

                # Writing Metrics
                self._write_column_metrics_csv(ground_truth_file_path, model_output_file_path, metrics_output_file_path, pii_types, greeting_types)
                print(f"Results written to {model_output_file_path}")
                print(f"Metrics written to {metrics_output_file_path}")
                return {"success": True}
            except ValueError as e:
                # Handle CSV validation errors specifically
                print(f"CSV validation error: {e}")
                return {"success": False, "error": str(e)}
            except Exception as e:
                print('Failed , error : ', e)
                print('\nRetrying ... \n')
                if attempt < self.retries - 1:
                    time.sleep(2)
                else:
                    print("Reached Maximum No of retries \n")
                    return {"success": False, "error": str(e)}