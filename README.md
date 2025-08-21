# Walled AI SDK (Python)

A Python SDK for interacting with Walled AI's Guardrail and PII Redaction APIs.

## Installation

```sh
pip install walledai
```

## Quick Start

### Import and Initialize

```python
from walledai import WalledProtect, WalledRedact

# Initialize WalledProtect for content moderation and safety checks
client = WalledProtect("your_api_key", retries=3)  # retries is optional

# Initialize WalledRedact for PII detection and masking
redact_client = WalledRedact("your_api_key", retries=3)  # retries is optional
```

## WalledProtect - Content Moderation & Safety

The `WalledProtect` class provides comprehensive content moderation capabilities including safety checks, compliance validation, PII detection, and greeting analysis.

### Basic Content Analysis

```python
response = client.guard(
    text="Hello, How are you",
    greetings_list=["Casual & Friendly"],
    generic_safety_check=True,
    compliance_list=[],
    pii_list=[]
)
print(response)
```

### Multi-turn Conversation Analysis

```python
conversation = [
    {"role": "user", "content": "Hi, my name is John Doe. I live at 123 Maple Street and my email is john.doe@example.com."},
    {"role": "assistant", "content": "Hello John, thanks for sharing. How can I assist you today?"},
]

response = client.guard(
    text=conversation,
    greetings_list=[
       "Casual & Friendly",
       "Professional & Polite"
    ],
    generic_safety_check=True,
    compliance_list=["Medical", "Finance", "Legal"],
    pii_list=[
        "Person's Name",
        "Address",
        "Email Id",
        "Contact No",
        "Date Of Birth",
        "Unique Id",
        "Financial Data"
    ]
)
print(response)
```

### Parameters

#### Guard Method Parameters

| Parameter             | Type                    | Required | Default                      | Description |
|-----------------------|-------------------------|----------|------------------------------|-------------|
| `text`                | `str \| list[dict]`     | Yes      | -                            | Input text or conversation array |
| `greetings_list`      | `list[str]`             | No       | `["Casual & Friendly"]`      | Greeting types to check |
| `generic_safety_check`| `bool`                  | No       | `True`                       | Enable safety filtering |
| `compliance_list`     | `list[str]`             | No       | `[]`                         | Compliance categories to check |
| `pii_list`            | `list[str]`             | No       | `[]`                         | PII categories to detect |

#### Allowed PII Types

| PII Type          | Description |
|-------------------|-------------|
| `"Person's Name"` | Individual's full or partial name |
| `"Address"`       | Physical or mailing addresses |
| `"Email Id"`      | Email addresses |
| `"Contact No"`    | Phone numbers and contact information |
| `"Date Of Birth"` | Birth dates and age-related information |
| `"Unique Id"`     | Social security numbers, IDs, licenses |
| `"Financial Data"`| Credit cards, bank accounts, financial info |

#### Allowed Greeting Types

| Greeting Type            | Description |
|--------------------------|-------------|
| `"Casual & Friendly"`    | Informal, warm greetings |
| `"Professional & Polite"`| Formal, business-appropriate greetings |

### Response Format

#### Successful Response Structure

| Field      | Type   | Description |
|------------|--------|-------------|
| `success`  | `bool` | Indicates if the request was processed successfully |
|`statusCode`|  `int` | Http Status Code
| `data`     | `dict` | Contains the analysis results |

#### Data Object Structure

**Safety Section:**

| Field             | Type    | Description |
|-------------------|---------|-------------|
| `safety`          | `str`   | Type of safety check performed |
| `isSafe`          | `bool`  | Whether the content passed safety checks |
| `score`           | `float` | Safety confidence score (if available) |
| `method`          | `str`   | Safety detection method used |
| `processing_time` | `float` | Time taken for safety analysis in seconds |
| `models_used`     | `list`  | List of AI models used for safety evaluation |

**Compliance Section:**

| Field       | Type   | Description |
|-------------|--------|-------------|
| `topic`     | `str`  | The compliance topic being checked |
| `isOnTopic` | `bool` | Whether the content relates to the compliance topic |
| `error`     | `str`  | Any error encountered during compliance check |

**PII Section:**

| Field       | Type   | Description |
|-------------|--------|-------------|
| `pii_type`  | `str`  | Type of PII being detected |
| `isPresent` | `bool` | Whether this PII type was found in the content |
| `error`     | `str`  | Any error encountered during PII detection |

**Greetings Section:**

| Field           | Type   | Description |
|-----------------|--------|-------------|
| `greeting_type` | `str`  | Type of greeting being analyzed |
| `isPresent`     | `bool` | Whether this greeting type was detected |
| `error`         | `int`  | Any error encountered during greeting analysis |

#### Example Response

```python
{
    "success": true,
    "statusCode": 200,
    "data": {
        "safety": [
            {
                "safety": "generic",
                "isSafe": false,
                "score": null,
                "method": "en-safety",
                "processing_time": 0.41751790046691895,
                "models_used": [
                    "walled_e_guard_a"
                ]
            }
        ],
        "compliance": [
            {
                "topic": "sdfsdf",
                "isOnTopic": false,
                "error": null
            }
        ],
        "pii": [
            {
                "pii_type": "Person's Name",
                "isPresent": true,
                "error": null
            },
            {
                "pii_type": "Address",
                "isPresent": true,
                "error": null
            },
            {
                "pii_type": "Email Id",
                "isPresent": true,
                "error": null
            },
            {
                "pii_type": "Contact No",
                "isPresent": false,
                "error": null
            },
            {
                "pii_type": "Date Of Birth",
                "isPresent": false,
                "error": null
            },
            {
                "pii_type": "Unique Id",
                "isPresent": false,
                "error": null
            },
            {
                "pii_type": "Financial Data",
                "isPresent": false,
                "error": null
            }
        ],
        "greetings": [
            {
                "greeting_type": "Casual & Friendly",
                "isPresent": true,
                "error": null
            },
            {
                "greeting_type": "Professional & Polite",
                "isPresent": true,
                "error": null
            }
        ]
    }
}
```

#### Error Response

| Field     | Type   | Description |
|-----------|--------|-------------|
| `success` | `bool` | Always `False` for error responses |
| `statusCode`| `int`  | Http Status Code for errors |
| `errorCode`| `str`| Main Model Error Code (for guardrail/pii)|
| `message`|`str`| Description of Error|
| `details`| `dict`| Details of Error|

```python
{
    "success": false,
    "statusCode": 400,
    "errorCode": "INVALID_GREETING_TYPE",
    "message": "Invalid greeting types: ['Casual & Friendlyy']. Must be one of: ['Casual & Friendly', 'Professional & Polite']",
    "details": {
        "invalid_greetings": [
            "Casual"
        ],
        "valid_greetings": [
            "Casual & Friendly",
            "Professional & Polite"
        ]
    }
}
```
> Checkout [documentation](https://docs.walled.ai/error-codes-1302667m0) for understanding of error codes 
### Evaluation

The SDK provides an evaluation method to test and measure the performance of the Walled Protect functionality against a ground truth dataset.

#### Batch Evaluation with CSV

```python
import asyncio
from walledai import WalledProtect

client = WalledProtect("your_api_key", retries=3)

# Run evaluation
asyncio.run(client.eval(
    ground_truth_file_path="./unit_test_cases.csv",
    model_output_file_path="./model_results.csv",
    metrics_output_file_path="./metrics.csv",
    concurrency_limit=20
))
```

#### Eval Method Parameters

| Parameter                | Type  | Required | Default | Description |
|--------------------------|-------|----------|---------|-------------|
| `ground_truth_file_path` | `str` | Yes      | -       | Path to CSV with test cases |
| `model_output_file_path` | `str` | Yes      | -       | Path to save results |
| `metrics_output_file_path`| `str` | Yes      | -       | Path to save metrics |
| `concurrency_limit`      | `int` | No       | `20`    | Max concurrent requests |

#### Ground Truth CSV Format

**Required Columns (must be present in this order):**

| Column Name          | Type   | Description |
|----------------------|--------|-------------|
| `test_input`         | `str`  | The input text to be processed |
| `compliance_topic`   | `str`  | The compliance topic for the test case |
| `compliance_isOnTopic` | `bool` | Whether the input is on the specified compliance topic (`TRUE` or `FALSE`) |

**Optional Columns (can be included as needed):**

| Column Name            | Type   | Description |
|------------------------|--------|-------------|
| `Person's Name`        | `bool` | Whether a person's name is present (`TRUE` or `FALSE`) |
| `Address`              | `bool` | Whether an address is present (`TRUE` or `FALSE`) |
| `Email Id`             | `bool` | Whether an email ID is present (`TRUE` or `FALSE`) |
| `Contact No`           | `bool` | Whether a contact number is present (`TRUE` or `FALSE`) |
| `Date Of Birth`        | `bool` | Whether a date of birth is present (`TRUE` or `FALSE`) |
| `Unique Id`            | `bool` | Whether a unique ID is present (`TRUE` or `FALSE`) |
| `Financial Data`       | `bool` | Whether financial data is present (`TRUE` or `FALSE`) |
| `Casual & Friendly`    | `bool` | Whether the greeting is casual & friendly (`TRUE` or `FALSE`) |
| `Professional & Polite`| `bool` | Whether the greeting is professional & polite (`TRUE` or `FALSE`) |

See [example unit test file](https://docs.google.com/spreadsheets/d/136QaJQJr5KACXjuTPr86a2-XIFq8APy8XKVg6J00X9U/edit?usp=sharing) for a sample ground truth file.

#### Evaluation Features

- **CSV-based testing**: Load test cases from CSV files
- **Concurrent processing**: Configurable concurrency limits
- **Automatic retries**: Built-in retry logic with delays
- **Metrics generation**: Accuracy, precision, recall, and F1 scores
- **Dynamic column support**: Automatically detects PII and greeting columns

#### Output Files

1. **Model Results CSV**: Contains the actual model predictions for each test case, including:
   - All columns present in the ground truth file
   - An additional `is_safe` column with `TRUE` or `FALSE` values indicating whether the input passed the safety evaluation

2. **Metrics CSV**: Contains evaluation metrics including:
   - Accuracy scores
   - Precision and recall
   - F1 scores
   - Confusion matrices

## WalledRedact - PII Detection & Masking

The `WalledRedact` class detects and masks personally identifiable information (PII) in text, replacing sensitive data with placeholders.

### Basic PII Masking

```python
response = redact_client.guard(
    text="Hello, How are you Henry",
)
print(response)
```

### Multi-turn Conversation PII Masking

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

### Parameters

| Parameter | Type                | Required | Description |
|-----------|---------------------|----------|-------------|
| `text`    | `str \| list[dict]` | Yes      | Text or conversation to process |

### Response Format

#### Successful Response Structure
| Field      | Type   | Description |
|------------|--------|-------------|
| `success`  | `bool` | Indicates if the request was processed successfully |
|`statusCode`|  `int` | Http Status Code
| `data`     | `dict` | Contains the analysis results |

#### Data Object Structure

| Field         | Type   | Description |
|---------------|--------|-------------|
| `status`      | `str`  | Response status ("success" or "error") |
| `success`     | `bool` | Whether the redaction was successful |
| `statusCode`  | `int`  | Status code of the operation |
| `remark`      | `str`  | Additional remarks about the operation |
| `input`       | `list` | Original input text/conversation |
| `masked_text` | `list` | Text with PII replaced by placeholders |
| `mapping`     | `dict` | Mapping of placeholders to original PII values |
| `error`       | `str`  | Any error encountered during processing |

#### Example Response

```python
{
    "success": true,
    "statusCode": 200,
    "data": {
        "success": true,
        "statusCode": 2001,
        "remark": "guardrails success type 21",
        "input": [
            {
                "role": "user",
                "content": "Hi, I'm John Doe. I live at 123 Maple Street and my email is john.doe@example.com"
            },
            {
                "role": "assistant",
                "content": "Hello John, how can I assist you today?"
            }
        ],
        "masked_text": [
            {
                "role": "user",
                "content": "Hi, I’m [Person_1]. I live at [Address_1] and my email is [Email_1]"
            },
            {
                "role": "assistant",
                "content": "Hello [Person_1], how can I assist you today?"
            }
        ],
        "mapping": {
            "[Person_1]": "John Doe",
            "[Address_1]": "123 Maple Street",
            "[Email_1]": "john.doe@example.com"
        },
        "error": null
    }
}
```

#### Error Response

| Field     | Type   | Description |
|-----------|--------|-------------|
| `success` | `bool` | Always `False` for error responses |
| `statusCode`| `int`  | Http Status Code for errors |
| `errorCode`| `str`| Main Model Error Code (for guardrail/pii)|
| `message`|`str`| Description of Error|
| `details`| `dict`| Details of Error|

```python
{
    "success": false,
    "statusCode": 400,
    "errorCode": "VALIDATION_ERROR",
    "message": "",
    "details": [
        {
            "type": "missing",
            "loc": [
                "text"
            ],
            "msg": "Field required",
            "input": {},
            "url": "https://errors.pydantic.dev/2.10/v/missing"
        }
    ]
}
```
> Checkout [documentation](https://docs.walled.ai/error-codes-1302667m0) for understanding of error codes 

## Configuration Options

### WalledProtect Configuration

| Parameter | Type  | Required | Default | Description |
|-----------|-------|----------|---------|-------------|
| `api_key` | `str` | Yes      | -       | Your Walled AI API key |
| `retries` | `int` | No       | `3`     | Number of retry attempts |

```python
client = WalledProtect("your_api_key", retries=3)
```

### WalledRedact Configuration

| Parameter | Type  | Required | Default | Description |
|-----------|-------|----------|---------|-------------|
| `api_key` | `str` | Yes      | -       | Your Walled AI API key |
| `retries` | `int` | No       | `3`     | Number of retry attempts |

```python
redact_client = WalledRedact("your_api