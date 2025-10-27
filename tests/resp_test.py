from src.protocol import RespType, RespValue, decode_resp, encode_resp


class TestDecodeRESP:
    # test simple string
    def test_decode_ping(self):
        data = b"*1\r\n$4\r\nPING\r\n"
        result = decode_resp(data)
        assert result == ["PING"]

    def test_decode_echo(self):
        data = b"*2\r\n$4\r\nECHO\r\n$5\r\nhello\r\n"
        result = decode_resp(data)
        assert result == ["ECHO", "hello"]

    def test_decode_simple_string(self):
        data = b"+OK\r\n"
        result = decode_resp(data)
        assert result == ["OK"]

    # test simple integer
    def test_decode_integer(self):
        data = b":123\r\n"
        result = decode_resp(data)
        assert result == [123]

    # test bulk string
    def test_decode_bulk_string(self):
        data = b"$5\r\nhello\r\n"
        result = decode_resp(data)
        assert result == ["hello"]

    def test_decode_empty_bulk_string(self):
        data = b"$0\r\n\r\n"
        result = decode_resp(data)
        assert result == [None]

    def test_decode_array(self):
        data = b"*2\r\n$5\r\nhello\r\n$5\r\nworld\r\n"
        result = decode_resp(data)
        assert result == ["hello", "world"]

    def test_decode_empty_array(self):
        data = b"*0\r\n"
        result = decode_resp(data)
        assert result == []

    def test_decode_nested_array(self):
        data = b"*2\r\n$5\r\nouter\r\n*2\r\n$6\r\ninner1\r\n$6\r\ninner2\r\n"
        result = decode_resp(data)
        assert result == ["outer", ["inner1", "inner2"]]

    def test_decode_error(self):
        data = b"-ERR something went wrong\r\n"
        result = decode_resp(data)
        assert result == ["ERR something went wrong"]


class TestEncodeRESP:
    def test_encode_null_bulk_string(self):
        result = encode_resp(RespValue(None, RespType.BULK_STRING))
        assert result == b"$-1\r\n"

    def test_encode_empty_bulk_string(self):
        result = encode_resp(RespValue("", RespType.BULK_STRING))
        assert result == b"$0\r\n\r\n"

    def test_encode_simple_string(self):
        result = encode_resp(RespValue("PONG", RespType.SIMPLE_STRING))
        assert result == b"+PONG\r\n"

    def test_encode_integer(self):
        result = encode_resp(RespValue(42, RespType.INTEGER))
        assert result == b":42\r\n"

    def test_encode_bulk_string(self):
        result = encode_resp(RespValue("hello", RespType.BULK_STRING))
        assert result == result == b"$5\r\nhello\r\n"

    def test_encode_array(self):
        result = encode_resp(RespValue(["hello", "world"], RespType.ARRAY))
        assert result == b"*2\r\n$5\r\nhello\r\n$5\r\nworld\r\n"

    def test_encode_mixed_array(self):
        value = RespValue(["OK", 123, None, "foo"], RespType.ARRAY)
        result = encode_resp(value)
        assert result == b"*4\r\n$2\r\nOK\r\n:123\r\n$-1\r\n$3\r\nfoo\r\n"

    def test_encode_error(self):
        result = encode_resp(RespValue("ERR unknown command", RespType.ERROR))
        assert result == b"-ERR unknown command\r\n"

    def test_encode_nested_array(self):
        value = RespValue(
            ["outer", RespValue(["inner1", "inner2"], RespType.ARRAY)], RespType.ARRAY
        )
        result = encode_resp(value)
        assert result == b"*2\r\n$5\r\nouter\r\n*2\r\n$6\r\ninner1\r\n$6\r\ninner2\r\n"
