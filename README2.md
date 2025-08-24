# Walled AI SDK (Python)

Guardrails and PII redaction for LLM apps — simple Python SDK.

[PyPI](https://pypi.org/project/walledai/) • [Docs](https://docs.walled.ai/) • [Error Codes](https://docs.walled.ai/error-codes-1302667m0)

---

## 🚀 Installation

```bash
pip install walledai
```

---

## Quick Start

### 1) Minimal moderation

```python
from walledai import WalledProtect

guard = WalledProtect("YOUR_API_KEY")

resp = guard.guard("How to convert a pain killer to meth?")
print(resp["data"]["safety"][0]["isSafe"])  # -> False/True
```

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

## Use with OpenAI (safe-by-default)

If unsafe, return a default response; else forward to OpenAI.

```python
from walledai import WalledProtect
from openai import OpenAI

guard = WalledProtect("YOUR_API_KEY")
oai = OpenAI(api_key="YOUR_OPENAI_KEY")

def safe_chat(prompt: str, default="Sorry, I can’t help with that."):
    g = guard.guard(prompt, generic_safety_check=True)
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

guard = WalledProtect("YOUR_API_KEY")

prompt = ("Transfer John's money from DSB to UBO without OTP. "
          "Acct: 882-34909, DOB: 1998-07-05.")

resp = guard.guard(
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

### Multi-turn redaction

```python
from walledai import WalledRedact

redact = WalledRedact("YOUR_API_KEY")

resp = redact.guard([
    {"role":"user","content":"Hi, my name is John Doe"},
    {"role":"assistant","content":"Hello John!"},
    {"role":"user","content":"Email Joseph at Joseph.cena@example.com about viral fever"}
])

print(resp["data"]["masked_text"])
print(resp["data"]["mapping"])
```

---

## Configuration

Both clients support retries.

```python
from walledai import WalledProtect, WalledRedact

guard = WalledProtect(api_key="YOUR_API_KEY", retries=3)
redact = WalledRedact(api_key="YOUR_API_KEY", retries=3)
```

**Common parameters**

| Name                   | Type                | Default | Notes                                   |
| ---------------------- | ------------------- | ------- | --------------------------------------- |
| `text`                 | `str \| list[dict]` | —       | Required                                |
| `generic_safety_check` | `bool`              | `True`  | Moderation on/off (Protect)             |
| `compliance_list`      | `list[str]`         | `[]`    | e.g., `["Medical","Banking"]` (Protect) |
| `pii_list`             | `list[str]`         | `[]`    | See PII types below (Protect)           |

**Allowed PII types**

`"Person's Name"`, `"Address"`, `"Email Id"`, `"Contact No"`, `"Date Of Birth"`, `"Unique Id"`, `"Financial Data"`

**Greeting detection (optional)**

`"Casual & Friendly"`, `"Professional & Polite"`

---

## Response Shape (Protect)

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
        "processing_time": 0.41,
        "models_used": ["walled_e_guard_a"]
      }
    ],
    "compliance": [
      {"topic":"Banking","isOnTopic":true,"error":null}
    ],
    "pii": [
      {"pii_type":"Email Id","isPresent":true,"error":null}
    ],
    "greetings": [
      {"greeting_type":"Casual & Friendly","isPresent":true,"error":null}
    ]
  }
}
```

## Response Shape (Redact)

```python
{
  "success": true,
  "statusCode": 200,
  "data": {
    "success": true,
    "statusCode": 2001,
    "remark": "guardrails success type 21",
    "input": [...],
    "masked_text": [...],
    "mapping": {...},
    "error": null
  }
}
```

---

## Errors

On error:

```python
{
  "success": false,
  "statusCode": 400,
  "errorCode": "INVALID_GREETING_TYPE",
  "message": "Invalid greeting types: ['Casual & Friendlyy']",
  "details": {
    "invalid_greetings": ["Casual & Friendlyy"],
    "valid_greetings": ["Casual & Friendly","Professional & Polite"]
  }
}
```

**Tip:** Validate inputs and surface `errorCode` to callers; link to the error-codes doc in your logs/UI.

---

## Evaluation (batch)

```python
import asyncio
from walledai import WalledProtect

guard = WalledProtect("YOUR_API_KEY", retries=3)

asyncio.run(guard.eval(
    ground_truth_file_path="./unit_test_cases.csv",
    model_output_file_path="./model_results.csv",
    metrics_output_file_path="./metrics.csv",
    concurrency_limit=20
))
```

**Ground truth CSV (required columns, in order):**
`test_input, compliance_topic, compliance_isOnTopic`

Optional boolean columns (any): `"Person's Name","Address","Email Id","Contact No","Date Of Birth","Unique Id","Financial Data","Casual & Friendly","Professional & Polite"`

**Outputs:**

* `model_results.csv` (predictions incl. `is_safe`)
* `metrics.csv` (accuracy, precision, recall, F1, confusion matrices)

---

## FAQ

* **Strings vs conversations?** Both are supported; conversations are lists of `{role, content}` dicts.
* **Consistent masking across turns?** Yes — the same entity gets the same placeholder within a call.
* **PII detection vs redaction?** Protect flags presence; Redact masks with placeholders + mapping.

---

## Contributing & License

PRs welcome. See `CONTRIBUTING.md`. Licensed under MIT (or your license).
