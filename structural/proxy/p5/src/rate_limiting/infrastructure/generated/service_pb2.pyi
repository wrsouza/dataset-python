from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class DataRequest(_message.Message):
    __slots__ = ("client_id", "key")
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    client_id: str
    key: str
    def __init__(self, client_id: _Optional[str] = ..., key: _Optional[str] = ...) -> None: ...

class DataResponse(_message.Message):
    __slots__ = ("key", "value", "served_at_unix_ms")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    SERVED_AT_UNIX_MS_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: str
    served_at_unix_ms: int
    def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ..., served_at_unix_ms: _Optional[int] = ...) -> None: ...
