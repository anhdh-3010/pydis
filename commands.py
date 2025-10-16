from resp import encode_resp

COMMANDS = {
    "PING": lambda args: encode_resp("PONG"),
    "ECHO": lambda args: args[0]
    if args
    else encode_resp(Exception("ERR wrong number of arguments")),
}


def execute_command(parts: list[str]) -> bytes:
    if not parts:
        return encode_resp(Exception("ERR empty command"))

    cmd = parts[0].upper()
    args = parts[1:]

    handler = COMMANDS.get(cmd)

    if not handler:
        return encode_resp(Exception(f"ERR unknown command {cmd}"))

    result = handler(args)
    return result
