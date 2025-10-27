from enum import Enum


class RespType(Enum):
    SIMPLE_STRING = "simple_string"
    BULK_STRING = "bulk_string"
    INTEGER = "integer"
    ERROR = "error"
    ARRAY = "array"
    NULL = "null"

