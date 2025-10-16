# +OK\r\n => OK, 5
from typing import Any


def read_simple_string(data: bytes) -> tuple[str, int]:
    pos = 1
    end = data.index(b'\r\n', pos)
    return data[pos:end].decode(), end + 2

# :123\r\n => 123, 6
def read_integer(data: bytes) -> tuple[int, int]:
    pos = 1
    end = data.index(b'\r\n', pos)
    return int(data[pos:end].decode()), end + 2

# -ERR message\r\n => "ERR message", 14
def read_error(data: bytes) -> tuple[str, int]:
    return read_simple_string(data)

# $5\r\nhello\r\n => "hello", 11
def read_bulk_string(data: bytes) -> tuple[str, int]:
    length, pos = read_integer(data)
    if length <= 0:
        return None, None

    return data[pos:pos+length].decode(), pos+length+2 

# *2\r\n$5\r\nhello\r\n$5\r\nworld\r\n => ["hello", "world"], int 
def read_array(data: bytes) -> tuple[list[str], int]:
    length, pos = read_integer(data)
    res = []
    for _ in range(length):
        value, consumed = read_bulk_string(data[pos:])
        res.append(value)
        pos += consumed
        
    return res, pos


def resp_parse(data: bytes) -> list[Any]:
    if not len(data):
        return None
    
    type_resp = chr(data[0])
    result = []
    if type_resp == "+":
        res, _ = read_simple_string(data)
    elif type_resp == ":":
        res, _ = read_integer(data)
    elif type_resp == "-":
        res, _ = read_error(data)
    elif type_resp == "$":
        res, _ = read_bulk_string(data)
    elif type_resp == "*":
        res, _ = read_array(data)
    else:
        raise ValueError(f"Unknown RESP type prefix: {type_resp}")
    
    if isinstance(res, list):
        result = res
    else:
        result.append(res)
    
    return result
