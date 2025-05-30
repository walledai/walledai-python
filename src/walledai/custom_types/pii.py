from typing import List, Optional
from typing_extensions import TypedDict, NotRequired

class Data(TypedDict):
    sucess:bool
    remark:str
    input:str
    mapping:dict

class PIIResponse(TypedDict):
    success: bool
    data: NotRequired[Optional[Data]]
    error: NotRequired[Optional[Exception]]
