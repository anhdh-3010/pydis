"""Key commands: DEL, EXPIRE, TTL, PERSIST, etc."""

from pydis.protocol import RespType, RespValue, encode_resp
from pydis.core import Store


def command_del(store: Store, args: list[str]) -> bytes:
    """DEL key [key ...] - Delete a key"""
    if not args:
        return encode_resp(
            RespValue("ERR wrong number of arguments for 'DEL'", RespType.ERROR)
        )
    deleted = 0
    for key in args:
        if store.delete(key):
            deleted += 1
    return encode_resp(RespValue(deleted, RespType.INTEGER))


def command_expire(store: Store, args: list[str]) -> bytes:
    """EXPIRE key seconds - Set a key's time to live in seconds"""
    if len(args) != 2:
        return encode_resp(
            RespValue("ERR wrong number of arguments for 'EXPIRE'", RespType.ERROR)
        )
    key, seconds = args
    try:
        seconds = int(seconds)
    except ValueError:
        return encode_resp(
            RespValue("ERR value is not an integer or out of range", RespType.ERROR)
        )

    result = store.expire(key, seconds)
    return encode_resp(RespValue(1 if result else 0, RespType.INTEGER))


def command_ttl(store: Store, args: list[str]) -> bytes:
    """TTL key - Get the time to live for a key"""
    if len(args) != 1:
        return encode_resp(
            RespValue("ERR wrong number of arguments for 'TTL'", RespType.ERROR)
        )
    key = args[0]
    ttl = store.ttl(key)
    return encode_resp(RespValue(ttl, RespType.INTEGER))


def command_persist(store: Store, args: list[str]) -> bytes:
    """PERSIST key - Remove the expiration from a key"""
    if len(args) != 1:
        return encode_resp(
            RespValue("ERR wrong number of arguments for 'PERSIST'", RespType.ERROR)
        )
    key = args[0]
    result = store.persist(key)
    return encode_resp(RespValue(1 if result else 0, RespType.INTEGER))

