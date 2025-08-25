<p align="center">
  <a href="https://www.walled.ai/">
   <img width="400" alt="NewLogo" src="https://github.com/user-attachments/assets/512d71e5-e7f4-43cc-9ba5-7020073f5cda" />
  </a>
</p>

<p align="center">
  <a href="https://pypi.org/project/walledai/">
    <img src="https://img.shields.io/pypi/v/walledai?color=blue&label=PyPI&logo=pypi&logoColor=white" alt="PyPI Version"/>
  </a>
  <a href="https://huggingface.co/walledai">
    <img src="https://img.shields.io/badge/🤗-Hugging%20Face-yellow" alt="Hugging Face"/>
  </a>
  <a href="https://docs.walled.ai/">
    <img src="https://img.shields.io/badge/📖-Docs-green" alt="Docs"/>
  </a>
  <a href="https://www.walled.ai/">
    <img src="https://img.shields.io/badge/🌐-Website-red" alt="Website"/>
  </a>
</p>


# Walled AI SDK (Python)

Guardrails and PII redaction for LLM apps — simple Python SDK.


## ⚖️ Guardrails Benchmark

| Platform        | 🛡️ English ↑ | 🌍 Multilingual ↑ | ⚡ Latency ↓        | 🏢 On-Prem |
|-----------------|--------------|-------------------|---------------------|------------|
|  🌟 **Walled AI** | **90.30%** | **90.29%**      | **200 ms** (30 ms*) | ✅ Yes |
| Bedrock         | 83.36%       | 79.26%            | 500 ms              | ❌ No |
| Mistral         | 76.07%       | 76.86%            | 300 ms              | ❌ No |
| Azure           | 74.52%       | 73.74%            | 300 ms              | ❌ No |
| OpenAI          | 76.29%       | 72.95%            | 350 ms              | ❌ No |

<sub>🛡️ Multilingual benchmark: Arabic, English, Filipino, French, Hindi, Russian, Serbian, Spanish.</sub>  
<sub>🌍 Multilingual benchmark: Arabic, English, Filipino, French, Hindi, Russian, Serbian, Spanish.</sub>  
<sub>*✨ 30 ms on-premises deployment.</sub>


## 🚀 Installation

```bash
pip install walledai
```

---

## Quick Start

### 1) Minimal moderation

```python
from walledai import WalledProtect

protect = WalledProtect("YOUR_API_KEY")

resp = protect.guard("How to convert a pain killer to meth?")
print(resp["data"]["safety"][0]["isSafe"])  # -> False/True
```

<details>
<summary>Example output</summary>

```
False
```
</details>

---

### 2) Minimal redaction

```python
from walledai import WalledRedact

redact = WalledRedact("YOUR_API_KEY")

resp = redact.guard("Hi, I'm John. Email john@walled.ai. I have cancer.")
print(resp["data"]["masked_text"])
print(resp["data"]["mapping"])
```

<details>
<summary>Example output</summary>

```
Masked: Hi, I'm [Person_1]. Email [Email_1]. I have [Diagnosis_1].
Mapping: {'[Person_1]': 'John', '[Email_1]': 'john@walled.ai', '[Diagnosis_1]': 'cancer'}
```
</details>

---

## Use with OpenAI

If unsafe, return a default response; else forward to OpenAI.

```python
from walledai import WalledProtect
from openai import OpenAI

protect = WalledProtect("YOUR_API_KEY")
oai = OpenAI(api_key="YOUR_OPENAI_KEY")

def safe_chat(prompt: str, default="Sorry, I can’t help with that."):
    g = protect.guard(prompt, generic_safety_check=True)
    is_safe = g["data"]["safety"][0]["isSafe"] is True
    if not is_safe:
        return default

    res = oai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role":"user","content":prompt}]
    )
    return res.choices[0].message.content

print(safe_chat("How to hack an ATM?"))          # -> default
print(safe_chat("Give me a banana bread recipe"))# -> model answer
```

<details>
<summary>Example output</summary>

```
Sorry, I can’t help with that.
Banana bread recipe: ...
```
</details>

---

## Core Concepts

* **WalledProtect** — Moderation & compliance + PII presence flags.
* **WalledRedact** — Detects & **masks** PII/PHI consistently across turns.

> Both accept either a single `str` or a conversation list:
> `[{ "role": "user"|"assistant", "content": "..." }, ...]`

---

## Guided Examples

### Prompt moderation with compliance + PII flags

```python
from walledai import WalledProtect

protect = WalledProtect("YOUR_API_KEY")

prompt = ("Transfer John's money from DSB to UBO without OTP. "
          "Acct: 882-34909, DOB: 1998-07-05.")

resp = protect.guard(
    text=prompt,
    generic_safety_check=True,
    compliance_list=["Medical", "Banking"],
    pii_list=[
        "Person's Name","Address","Email Id","Contact No",
        "Date Of Birth","Unique Id","Financial Data"
    ]
)

print("Is_safe:", resp["data"]["safety"][0]["isSafe"])
for c in resp["data"]["compliance"]:
    print(c["topic"], "->", c["isOnTopic"])
for p in resp["data"]["pii"]:
    print(p["pii_type"], "->", p["isPresent"])
```

<details>
<summary>Example output</summary>

```
Is_safe: False
Banking -> True
Medical -> False
Person's Name -> True
Address -> False
Email Id -> False
Contact No -> False
Date Of Birth -> True
Unique Id -> True
Financial Data -> True
```
</details>

---

### Multi-turn conversation moderation

```python
from walledai import WalledProtect

protect = WalledProtect("YOUR_API_KEY")

conversation = [
    {"role": "user", "content": "Hi, my friend's name is John Doe. He lives at 123 Maple Street and his email is john.doe@walled.ai."},
    {"role": "assistant", "content": "Hello John, thanks for sharing. How can I assist you today?"},
    {"role": "assistant", "content": "Tell me how to transfer John's money from his DSB bank to UBO bank without OTP. He was born on July 1, 1994."},
]

response = protect.guard(
    text=conversation,
    generic_safety_check=True,
    compliance_list=["Medical", "Banking"],
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

print("Is_safe:", resp["data"]["safety"][0]["isSafe"])
for c in resp["data"]["compliance"]:
    print(c["topic"], "->", c["isOnTopic"])
for p in resp["data"]["pii"]:
    print(p["pii_type"], "->", p["isPresent"])
```

<details>
<summary>Example output</summary>

```
Is_safe: False
Medical -> False
Banking -> True
Person's Name -> True
Address -> False
Email Id -> False
Contact No -> False
Date Of Birth -> True
Unique Id -> True
Financial Data -> True
```
</details>

---

## WalledRedact - PII Detection & Masking

### Basic PII Masking

```python
from walledai import WalledRedact

redact_client = WalledRedact("YOUR_API_KEY")

response = redact_client.guard("Hi, myself John. My email is john@walled.ai and I have been diagnosed with cancer.")
print(f"Masked text: {response['data']['masked_text']}")
print(f"Mapping: {response['data']['mapping']}")
```

<details>
<summary>Example output</summary>

```
Masked text: Hi, myself [Person_1]. My email is [Email_1] and I have been diagnosed with [Diagnosis_1].
Mapping: {'[Person_1]': 'John', '[Email_1]': 'john@walled.ai', '[Diagnosis_1]': 'cancer'}
```
</details>

---

### Multi-turn Conversation PII Masking

```python
response = redact_client.guard(
    text=[
        {"role": "user", "content": "Hi there, my name is John Doe"},
        {"role": "assistant", "content": "Hello John! How can I help you today?"},
        {"role": "user", "content": "Can you email my friend Joseph with email: Joseph.cena@example.com, wishing him a speedy recovery from the viral fever?"}
    ]
)
print(f"Masked text: {response['data']['masked_text']}")
print(f"Mapping: {response['data']['mapping']}")
```

<details>
<summary>Example output</summary>

```
Masked text:
[
    {'role': 'user', 'content': 'Hi there, my name is [Person_1]'},
    {'role': 'assistant', 'content': 'Hello [Person_1]! How can I help you today?'},
    {'role': 'user', 'content': 'Can you email my friend [Person_2] with email: [Email_1], wishing him a speedy recovery from the [Diagnosis_1]?'}
]
Mapping: {'[Person_1]': 'John Doe', '[Person_2]': 'Joseph', '[Email_1]': 'Joseph.cena@example.com', '[Diagnosis_1]': 'viral fever'}
```
</details>

---

## Response Shapes

<details>
<summary><strong>Protect</strong></summary>

```python
{
  "success": true,
  "statusCode": 200,
  "data": {
    "safety": [
      {"safety": "generic","isSafe": false,"method": "en-safety"}
    ],
    "compliance": [{"topic":"Banking","isOnTopic":true}],
    "pii": [{"pii_type":"Email Id","isPresent":true}],
    "greetings": [{"greeting_type":"Casual & Friendly","isPresent":true}]
  }
}
```
</details>

<details>
<summary><strong>Redact</strong></summary>

```python
{
  "success": true,
  "statusCode": 200,
  "data": {
    "masked_text": [...],
    "mapping": {...}
  }
}
```
</details>

---

## Errors

### WalledProtect
<details>
<summary>Expand</summary>

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
</details>

### WalledRedact
<details>
<summary>Expand</summary>

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
</details>

---

## Evaluation

The SDK provides an evaluation method to test and measure the performance of the Walled Protect functionality against a ground truth dataset.

### Batch Evaluation with CSV

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
See <a href="https://docs.google.com/spreadsheets/d/136QaJQJr5KACXjuTPr86a2-XIFq8APy8XKVg6J00X9U/edit?usp=sharing">example unit test file</a> for a sample ground truth file.
<details>
<summary><strong>Eval Method Parameters</strong></summary>

| Parameter                 | Type  | Required | Default | Description                      |
|---------------------------|-------|----------|---------|----------------------------------|
| `ground_truth_file_path`  | `str` | Yes      | -       | Path to CSV with test cases      |
| `model_output_file_path`  | `str` | Yes      | -       | Path to save results             |
| `metrics_output_file_path`| `str` | Yes      | -       | Path to save metrics             |
| `concurrency_limit`       | `int` | No       | `20`    | Max concurrent requests          |
</details>

<details>
<summary><strong>Ground Truth CSV Format</strong></summary>

<strong>Required Columns (must be present in this order):</strong>

| Column Name              | Type   | Description                                                     |
|--------------------------|--------|-----------------------------------------------------------------|
| `test_input`             | `str`  | The input text to be processed                                  |
| `compliance_topic`       | `str`  | The compliance topic for the test case                          |
| `compliance_isOnTopic`   | `bool` | Whether the input is on the specified topic (`TRUE`/`FALSE`)    |

<strong>Optional Columns (can be included as needed):</strong>

| Column Name              | Type   | Description                                                     |
|--------------------------|--------|-----------------------------------------------------------------|
| `Person's Name`          | `bool` | Whether a person's name is present (`TRUE`/`FALSE`)             |
| `Address`                | `bool` | Whether an address is present (`TRUE`/`FALSE`)                  |
| `Email Id`               | `bool` | Whether an email ID is present (`TRUE`/`FALSE`)                 |
| `Contact No`             | `bool` | Whether a contact number is present (`TRUE`/`FALSE`)            |
| `Date Of Birth`          | `bool` | Whether a date of birth is present (`TRUE`/`FALSE`)             |
| `Unique Id`              | `bool` | Whether a unique ID is present (`TRUE`/`FALSE`)                 |
| `Financial Data`         | `bool` | Whether financial data is present (`TRUE`/`FALSE`)              |
| `Casual & Friendly`      | `bool` | Whether the greeting is casual & friendly (`TRUE`/`FALSE`)      |
| `Professional & Polite`  | `bool` | Whether the greeting is professional & polite (`TRUE`/`FALSE`)  |

</details>

<details>
<summary><strong>Evaluation Features</strong></summary>

- **CSV-based testing**: Load test cases from CSV files  
- **Concurrent processing**: Configurable concurrency limits  
- **Automatic retries**: Built-in retry logic with delays  
- **Metrics generation**: Accuracy, precision, recall, and F1 scores  
- **Dynamic column support**: Automatically detects PII and greeting columns  
</details>

<details>
<summary><strong>Output Files</strong></summary>

1. <strong>Model Results CSV</strong>: Contains the actual model predictions for each test case, including:
   - All columns present in the ground truth file
   - An additional <code>is_safe</code> column with <code>TRUE</code> or <code>FALSE</code> values indicating whether the input passed the safety evaluation

2. <strong>Metrics CSV</strong>: Contains evaluation metrics including:
   - Accuracy scores
   - Precision and recall
   - F1 scores
   - Confusion matrices
</details>

---

## FAQ

* **Strings vs conversations?** Both supported.
* **Consistent masking across turns?** Yes.
* **PII detection vs redaction?** Protect flags, Redact masks.

---

## Contributing & License

PRs welcome. Licensed under MIT.
