from typing import List, Literal, Optional, Any
from typing_extensions import TypedDict, NotRequired

class SafetyItem(TypedDict):
    safety: str
    isSafe: bool
    score: int

class GreetingItem(TypedDict):
    greeting_type: str
    isPresent: bool

class Data(TypedDict):
    safety: NotRequired[Optional[List[SafetyItem]]]
    compliance: NotRequired[Optional[List]]
    pii: NotRequired[Optional[List]]
    greetings: NotRequired[Optional[List[GreetingItem]]]

class GuardRailResponse(TypedDict):
    success: bool
    statusCode:int
    message:NotRequired[Optional[str]]
    errorCode:NotRequired[Optional[str]]
    data: NotRequired[Optional[Data]]
    details: NotRequired[Optional[Any]]

class TextInput(TypedDict):
    role: str
    content: str
