from typing import Any

from .constants import RespType


# +OK\r\n => OK, 5
def read_simple_string(data: bytes) -> tuple[str, int]:
    pos = 1
    end = data.index(b"\r\n", pos)
    return data[pos:end].decode(), end + 2


# :123\r\n => 123, 6
def read_integer(data: bytes) -> tuple[int, int]:
    pos = 1
    end = data.index(b"\r\n", pos)
    return int(data[pos:end].decode()), end + 2


# -ERR message\r\n => "ERR message", 14
def read_error(data: bytes) -> tuple[str, int]:
    return read_simple_string(data)


# $5\r\nhello\r\n => "hello", 11
def read_bulk_string(data: bytes) -> tuple[str | None, int | None]:
    length, pos = read_integer(data)
    if length <= 0:
        return None, None

    return data[pos : pos + length].decode(), pos + length + 2


# *2\r\n$5\r\nhello\r\n$5\r\nworld\r\n => ["hello", "world"], int
def read_array(data: bytes) -> tuple[list, int]:
    length, pos = read_integer(data)
    res = []

    for _ in range(length):
        t = chr(data[pos])
        if t == "+":
            value, consumed = read_simple_string(data[pos:])
        elif t == ":":
            value, consumed = read_integer(data[pos:])
        elif t == "$":
            value, consumed = read_bulk_string(data[pos:])
        elif t == "*":
            value, consumed = read_array(data[pos:])
        else:
            raise ValueError(f"Unknown RESP type: {t}")

        res.append(value)
        if consumed is not None:
            pos += consumed

    return res, pos


def decode_resp(data: bytes) -> list[Any]:
    if not len(data):
        return []

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


class RespValue:
    def __init__(self, value, resp_type: RespType):
        self.value = value
        self.resp_type = resp_type


def encode_resp(value: RespValue | list[RespValue]) -> bytes:
    if isinstance(value, list):  # Array (list of RespValue)
        encoded = f"*{len(value)}\r\n".encode()
        for item in value:
            encoded += encode_resp(item)
        return encoded

    if value.resp_type == RespType.ERROR:
        return f"-{value.value}\r\n".encode()

    elif value.resp_type == RespType.INTEGER:
        return f":{value.value}\r\n".encode()

    elif value.resp_type == RespType.NULL:
        return b"$-1\r\n"

    elif value.resp_type == RespType.SIMPLE_STRING:
        return f"+{value.value}\r\n".encode()

    elif value.resp_type == RespType.BULK_STRING:
        if value.value is None:
            return b"$-1\r\n"
        s = str(value.value)
        return f"${len(s)}\r\n{s}\r\n".encode()

    elif value.resp_type == RespType.ARRAY:
        # value.value is expected to be an iterable of elements (possibly raw types)
        items = value.value or []
        encoded = f"*{len(items)}\r\n".encode()
        for item in items:
            if isinstance(item, RespValue):
                encoded += encode_resp(item)
            elif item is None:
                encoded += encode_resp(RespValue(None, RespType.NULL))
            elif isinstance(item, int):
                encoded += encode_resp(RespValue(item, RespType.INTEGER))
            else:
                # default strings/others to bulk string representation
                s = str(item)
                encoded += encode_resp(RespValue(s, RespType.BULK_STRING))
        return encoded

    else:
        raise TypeError(f"Unsupported RESP type: {value.resp_type}")

