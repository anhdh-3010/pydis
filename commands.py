from constants import RespType
from resp import RespValue, encode_resp

COMMANDS = {
    "PING": lambda args: encode_resp(RespValue("PONG", RespType.SIMPLE_STRING)),
    "ECHO": lambda args: encode_resp(RespValue(args[0], RespType.BULK_STRING))
    if args
    else encode_resp(RespValue("ERR wrong number of arguments", RespType.ERROR)),
}


def execute_command(parts: list[str]) -> bytes:
    if not parts:
        return encode_resp(RespValue("ERR empty command", RespType.ERROR))

    cmd = parts[0].upper()
    args = parts[1:]

    handler = COMMANDS.get(cmd)

    if not handler:
        return encode_resp(RespValue(f"ERR unknown command {cmd}", RespType.ERROR))

    result = handler(args)
    return result
