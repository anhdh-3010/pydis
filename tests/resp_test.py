from resp import decode_resp, encode_resp


class TestRESP:
    def test_decode_simple_string(self):
        data = b"+OK\r\n"
        result = decode_resp(data)
        assert result == ["OK"]

    def test_decode_integer(self):
        data = b":123\r\n"
        result = decode_resp(data)
        assert result == [123]

    def test_decode_bulk_string(self):
        data = b"$5\r\nhello\r\n"
        result = decode_resp(data)
        assert result == ["hello"]

    def test_decode_array(self):
        data = b"*2\r\n$5\r\nhello\r\n$5\r\nworld\r\n"
        result = decode_resp(data)
        assert result == ["hello", "world"]

    def test_encode_simple_string(self):
        result = encode_resp("PONG")
        assert result == b"+PONG\r\n"

    def test_encode_integer(self):
        result = encode_resp(42)
        assert result == b":42\r\n"

    def test_encode_bulk_string(self):
        result = encode_resp("hello")
        assert result == b"+hello\r\n" or result == b"$5\r\nhello\r\n"

    def test_encode_array(self):
        result = encode_resp(["hello", "world"])
        assert result == b"*2\r\n$5\r\nhello\r\n$5\r\nworld\r\n"
