from typing import Any, Dict, List, Optional, Union
from typing_extensions import TypedDict, NotRequired

class ConversationEntry(TypedDict):
    role: str
    content: str

class Data(TypedDict, total=False):  # total=False allows optional keys
    success: bool
    statusCode: int
    remark: str
    error: Any  # can be str or None
    input: Union[str, List[ConversationEntry]]
    masked_conversation: Optional[List[ConversationEntry]]
    masked_text: Optional[str]
    mapping: Dict[str, str]

class PIIResponse(TypedDict):
    success: bool
    statusCode:int
    message:NotRequired[Optional[str]]
    errorCode:NotRequired[Optional[str]]
    data: NotRequired[Optional[Data]]
    details: NotRequired[Optional[Any]]