# Walled AI SDK

A Python SDK for interacting with Walled AI.

## Installation
```sh
pip install walledai
```

## Usage

```python
from walledai import WalledProtect, WalledRedact
# Initialize the client 
client = WalledProtect("your_api_key", retries=3)  # retries is optional
redact_client = WalledRedact("your_api_key", retries=3)  # for redaction
```

## Walled Protect

```python
response = client.guard(
    text="Hello, How are you", 
    greetings_list=["generalgreetings"], 
    text_type="prompt", 
    generic_safety_check=True,
    compliance_list=[],
    pii_list=[]
)
print(response)
```

Processes the text using Walled AI's protection mechanisms.

#### Parameters:
- **`text`** (*str*, required): The input text to be processed.
- **`greetings_list`** (*list of str*, optional): A list of predefined greetings categories. ex: ["Casual & Friendly", "Formal", "Professional"]. Defaults to ["Casual & Friendly"]
- **`text_type`** (*str*, optional): Type of text being processed. Defaults to `"prompt"`.
- **`generic_safety_check`** (*bool*, optional): Whether to apply a general safety filter. Defaults to `True`.
- **`compliance_list`** (*list of str*, optional): A list of compliances.
- **`pii_list`** (*list of str*, optional): Must be empty or contain only the following values: `"Person's Name"`, `"Address"`, `"Email Id"`, `"Contact No"`, `"Date Of Birth"`, `"Unique Id"`, `"Financial Data"`.

#### Example Usage:
```python
response = client.guard(
    text="Hello, How are you", 
    greetings_list=["generalgreetings"], 
    text_type="prompt", 
    generic_safety_check=True,
    pii_list=[],
    compliance_list=["Medical", "Finance"]
)
print(response)
```

### Example Responses
The response returned by the `guard` method is a dictionary.

#### Successful Response
```python
{
    "success": true,
    "data": {
        "safety": [{ "safety": "generic", "isSafe": true, "score": 5 }],
        "compliance": [],
        "pii": [],
        "greetings": [{ "greeting_type": "generalgreetings", "isPresent": true }]
    }
}
```

#### Error Response
If an error occurs, the SDK will retry the request up to the specified number of retries (`retries` parameter in `WalledProtect`) or default retry number. If the retries are exhausted, it will return an error response.
```python
{
    "success": false,
    "error": "Invalid API key provided."
}
```

## Walled Redact

Processes the text using Walled AI's redaction mechanisms.

#### Parameters:
- **`text`** (*str*, required): The input text to be processed.

#### Example Usage:
```python
response = redact_client.guard(
    text="Hello, How are you Henry", 
)
print(response)
```

### Example Responses
The response returned by the `guard` method is a dictionary.

#### Successful Response
```python
{
    "success": true,
    "data": {
        "success": true,
        "remark": "Success! one attempt",
        "input": "Hi my name is Henry",
        "masked_text": "Hello my name is PN1",
        "mapping": {
            "PNA1": "indranil"
        }
    }
}
```

#### Error Response
If an error occurs, the SDK will retry the request up to the specified number of retries (`retries` parameter in `WalledRedact`) or default retry number. If the retries are exhausted, it will return an error response.
```python
{
    "success": false,
    "error": "Invalid API key provided."
}
```

## Evaluation

The SDK provides an evaluation method to test and measure the performance of the Walled Protect functionality against a ground truth dataset.

#### Parameters:
- **`ground_truth_file_path`** (*str*, required): Path to the CSV file containing test cases with expected results.
- **`model_output_file_path`** (*str*, required): Path where the model's output results will be saved.
- **`metrics_output_file_path`** (*str*, required): Path where the evaluation metrics will be saved.
- **`concurrency_limit`** (*int*, optional): Maximum number of concurrent requests. Defaults to 20.

#### Example Usage:
```python
# Run evaluation
await client.eval(
    ground_truth_file_path="./unit_test_cases.csv",
    model_output_file_path="./model_results.csv",
    metrics_output_file_path="./metrics.csv",
    concurrency_limit=20
)
```

### Ground Truth CSV Format
The ground truth CSV should contain the following columns:
- `text`: Input text to be processed
- `expected_safety`: Expected safety result (true/false)
- `expected_compliance`: Expected compliance result (true/false)
- `expected_pii`: Expected PII detection result (true/false)
- `expected_greetings`: Expected greetings detection result (true/false)

### Output Files
1. **Model Results CSV**: Contains the actual model predictions for each test case
2. **Metrics CSV**: Contains evaluation metrics including:
   - Accuracy scores
   - Precision and recall
   - F1 scores
   - Confusion matrices