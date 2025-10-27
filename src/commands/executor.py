"""Command executor - routes commands to appropriate handlers."""

from pydis.protocol import RespType, RespValue, encode_resp
from pydis.core import Store
from .string import command_echo, command_get, command_set, command_setnx, command_incr
from .key import command_del, command_expire, command_ttl, command_persist

# Global store instance
store = Store()


def command_ping(store: Store, args: list[str]) -> bytes:
    """PING - Ping the server"""
    if len(args) > 0:
        return encode_resp(
            RespValue("ERR wrong number of arguments for 'PING'", RespType.ERROR)
        )
    return encode_resp(RespValue("PONG", RespType.SIMPLE_STRING))


# Command registry
COMMANDS = {
    "PING": command_ping,
    "ECHO": command_echo,
    "GET": command_get,
    "SET": command_set,
    "DEL": command_del,
    "EXPIRE": command_expire,
    "TTL": command_ttl,
    "PERSIST": command_persist,
    "SETNX": command_setnx,
    "INCR": command_incr,
}


def execute_command(parts: list[str]) -> bytes:
    """Execute a Redis command.

    Args:
        parts: List of command parts, where parts[0] is the command name
               and parts[1:] are the arguments.

    Returns:
        Encoded RESP response as bytes.
    """
    if not parts:
        return encode_resp(RespValue("ERR empty command", RespType.ERROR))

    cmd = parts[0].upper()
    args = parts[1:]

    handler = COMMANDS.get(cmd)

    if not handler:
        return encode_resp(RespValue(f"ERR unknown command {cmd}", RespType.ERROR))

    result = handler(store, args)
    return result
