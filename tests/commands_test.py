from resp import decode_resp
from commands import execute_command


class TestIntegration:
    def test_full_ping_resp(self):
        # client sends RESP-encoded *1\r\n$4\r\nPING\r\n
        raw = b"*1\r\n$4\r\nPING\r\n"
        parts = decode_resp(raw)
        result = execute_command(parts)
        assert result == b"+PONG\r\n"

    def test_full_echo_resp(self):
        raw = b"*2\r\n$4\r\nECHO\r\n$5\r\nhello\r\n"
        parts = decode_resp(raw)
        result = execute_command(parts)
        assert result == b"$5\r\nhello\r\n"
