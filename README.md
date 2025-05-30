# Walled AI SDK

A Python SDK for interacting with Walled AI.

## Installation
```sh
pip install walledai
```
## Usage

```python
from walledai import WalledProtect
# Initialise the client 
client = WalledProtect("your_api_key",retries=3)# retries is optional
```
## Walled Protect

```python
response = client.guardrail(
    text="Hello , How are you", 
    greetings_list=["generalgreetings"], 
    text_type="prompt", 
    generic_safety_check=True
)
print(response)
```


Processes the text using Walled AI's protection mechanisms.

#### Parameters:
- **`text`** (*str*, required): The input text to be processed.
- **`greetings_list`** (*list of str*, optional): A list of predefined greetings categories.
- **`text_type`** (*str*, optional): Type of text being processed. Defaults to `"prompt"`.
- **`generic_safety_check`** (*bool*, optional): Whether to apply a general safety filter. Defaults to `True`.

#### Example Usage:
```python
response = client.guardrail(
    text="Hello , How are you", 
    greetings_list=["generalgreetings"], 
    text_type="prompt", 
    generic_safety_check=True
)
print(response)
```

### Example Responses
The response returned by the guardrail method is a dictionary.
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
## PII

Processes the text using Walled AI's PII mechanisms.

#### Parameters:
- **`text`** (*str*, required): The input text to be processed.

#### Example Usage:
```python
response = client.pii(
    text="Hello , How are you Henry", 
)
print(response)
```

### Example Responses
The response returned by the guardrail method is a dictionary.
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
If an error occurs, the SDK will retry the request up to the specified number of retries (`retries` parameter in `WalledProtect`) or default retry number. If the retries are exhausted, it will return an error response.
```python
{
    "success": false,
    "error": "Invalid API key provided."
}
```
