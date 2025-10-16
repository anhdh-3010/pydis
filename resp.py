from typing import Any


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
def read_array(data: bytes) -> tuple[list[str], int]:
    length, pos = read_integer(data)
    res = []
    for _ in range(length):
        value, consumed = read_bulk_string(data[pos:])
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


def encode_resp(value: Any) -> bytes:
    if isinstance(value, Exception):  # Error
        return f"-{value}\r\n".encode()

    elif isinstance(value, int):  # Integer
        return f":{value}\r\n".encode()

    elif value is None:  # Null bulk string
        return b"$-1\r\n"

    elif isinstance(value, list):  # Array
        encoded = f"*{len(value)}\r\n".encode()
        for item in value:
            if item is None:
                encoded += b"$-1\r\n"
            else:
                item_str = str(item)
                encoded += f"${len(item_str)}\r\n{item_str}\r\n".encode()
        return encoded

    elif isinstance(value, str):  # Simple String
        if value in ("OK", "PONG"):
            return f"+{value}\r\n".encode()

        return f"${value}\r\n".encode()

    else:  # Bulk String
        s = str(value)
        return f"${len(s)}\r\n{s}\r\n".encode()
