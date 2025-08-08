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
    generic_safety_check=True,
    compliance_list=[],
    pii_list=[]
)
print(response)
```

Processes the text using Walled AI's protection mechanisms.

#### Parameters:
- **`text`** (*str* or *list of dict*, required): The input text to be processed. Can be a single string or a list of dicts (e.g., for multi-turn input).
- **`greetings_list`** (*list of str*, optional): A list of predefined greetings categories. ex: ["Casual & Friendly", "Formal", "Professional"]. Defaults to ["Casual & Friendly"]
- **`generic_safety_check`** (*bool*, optional): Whether to apply a general safety filter. Defaults to `True`.
- **`compliance_list`** (*list of str*, optional): A list of compliances.
- **`pii_list`** (*list of str*, optional): Must be empty or contain only the following values: `"Person's Name"`, `"Address"`, `"Email Id"`, `"Contact No"`, `"Date Of Birth"`, `"Unique Id"`, `"Financial Data"`.

#### Example Usage:
```python
response = client.guard(
    text="Hello, How are you", 
    greetings_list=["generalgreetings"], 
    generic_safety_check=True,
    pii_list=[],
    compliance_list=["Medical", "Finance"]
)
print(response)
```

#### Example: Multi-turn Input (Conversation)
You can also pass a list of dicts (e.g., for chat or multi-turn input):

```python
response = client.guard(
    text=[
        {"role": "user", "content": "Hi there, can you help me with some information?"},
        {"role": "assistant", "content": "Of course! What would you like to know?"},
        {"role": "user", "content": "Can you suggest some healthy habits for daily life?"}
    ],
    greetings_list=["Casual & Friendly"],
    generic_safety_check=True
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

Processes the text using Walled AI's PII detection and redaction mechanisms.

#### Parameters:
- **`text`** (*str* or *list of dict*, required): The input text to be processed. Can be a single string or a list of dicts (e.g., for multi-turn input).

#### Example Usage:
```python
response = redact_client.guard(
    text="Hello, How are you Henry", 
)
print(response)
```

#### Example: Multi-turn Input (Conversation)
You can also pass a list of dicts (e.g., for chat or multi-turn input):

```python
response = redact_client.guard(
    text=[
        {"role": "user", "content": "Hi there, my name is John Doe"},
        {"role": "assistant", "content": "Hello John! How can I help you today?"},
        {"role": "user", "content": "Can you help me with my email: john.doe@example.com"}
    ]
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
import asyncio
from walledai import WalledProtect

client = WalledProtect("your_api_key", retries=3)  # retries is optional
asyncio.run(client.eval(
    ground_truth_file_path="./unit_test_cases.csv",
    model_output_file_path="./model_results.csv",
    metrics_output_file_path="./metrics.csv",
    concurrency_limit=20
))
```

### Ground Truth CSV Format
The ground truth CSV file has flexible column requirements:

#### Required Columns (must be present in this order):
- `test_input`: The input text to be processed.
- `compliance_topic`: The compliance topic for the test case.
- `compliance_isOnTopic`: Whether the input is on the specified compliance topic (`TRUE` or `FALSE`).

#### Optional Columns (can be included as needed):
- `Person's Name`: Whether a person's name is present (`TRUE` or `FALSE`).
- `Address`: Whether an address is present (`TRUE` or `FALSE`).
- `Email Id`: Whether an email ID is present (`TRUE` or `FALSE`).
- `Contact No`: Whether a contact number is present (`TRUE` or `FALSE`).
- `Date Of Birth`: Whether a date of birth is present (`TRUE` or `FALSE`).
- `Unique Id`: Whether a unique ID is present (`TRUE` or `FALSE`).
- `Financial Data`: Whether financial data is present (`TRUE` or `FALSE`).
- `Casual & Friendly`: Whether the greeting is casual & friendly (`TRUE` or `FALSE`).
- `Professional & Polite`: Whether the greeting is professional & polite (`TRUE` or `FALSE`).

**Notes:**
- Only the first 3 columns are mandatory and must be present in the exact order specified above.
- Optional columns can be included in any order after the required columns.
- The values for boolean columns should be `TRUE` or `FALSE` (case-insensitive).
- Missing optional columns will not result in an error during evaluation.

#### Example of a valid ground truth file
See [`example_unit_test_file`](https://docs.google.com/spreadsheets/d/136QaJQJr5KACXjuTPr86a2-XIFq8APy8XKVg6J00X9U/edit?usp=sharing) for a sample ground_truth_file.

### Output Files
1. **Model Results CSV**: Contains the actual model predictions for each test case. This file will include:
   - All columns present in the ground truth file
   - An additional `is_safe` column with `TRUE` or `FALSE` values indicating whether the input passed the safety evaluation
   
2. **Metrics CSV**: Contains evaluation metrics including:
   - Accuracy scores
   - Precision and recall
   - F1 scores
   - Confusion matrices