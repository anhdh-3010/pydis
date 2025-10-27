"""String commands: GET, SET, SETNX, INCR, etc."""

from pydis.protocol import RespType, RespValue, encode_resp
from pydis.core import Store


def command_echo(store: Store, args: list[str]) -> bytes:
    """ECHO message - Returns message"""
    if len(args) != 1:
        return encode_resp(
            RespValue("ERR wrong number of arguments for 'ECHO'", RespType.ERROR)
        )
    return encode_resp(RespValue(args[0], RespType.BULK_STRING))


def command_get(store: Store, args: list[str]) -> bytes:
    """GET key - Get the value of key"""
    if len(args) != 1:
        return encode_resp(
            RespValue("ERR wrong number of arguments for 'GET'", RespType.ERROR)
        )
    val = store.get(args[0])
    if val is None:
        return encode_resp(RespValue(None, RespType.NULL))

    return encode_resp(RespValue(val, RespType.BULK_STRING))


def command_set(store: Store, args: list[str]) -> bytes:
    """SET key value [EX seconds] - Set the string value of a key"""
    if len(args) < 2:
        return encode_resp(
            RespValue("ERR wrong number of arguments for 'SET'", RespType.ERROR)
        )

    key = args[0]
    value = args[1]
    ex = None

    # hỗ trợ SET key value EX seconds
    if len(args) >= 4 and args[2].upper() == "EX":
        try:
            ex = int(args[3])
        except ValueError:
            return encode_resp(
                RespValue("ERR value is not an integer or out of range", RespType.ERROR)
            )

    store.set(key, value, ex)
    return encode_resp(RespValue("OK", RespType.SIMPLE_STRING))


def command_setnx(store: Store, args: list[str]) -> bytes:
    """SETNX key value - Set the value of a key, only if the key does not exist"""
    if len(args) != 2:
        return encode_resp(
            RespValue("ERR wrong number of arguments for 'SETNX'", RespType.ERROR)
        )
    key, value = args
    success = store.setnx(key, value)
    return encode_resp(RespValue(1 if success else 0, RespType.INTEGER))


def command_incr(store: Store, args: list[str]) -> bytes:
    """INCR key - Increment the integer value of a key by one"""
    if len(args) != 1:
        return encode_resp(
            RespValue("ERR wrong number of arguments for 'INCR'", RespType.ERROR)
        )
    key = args[0]
    try:
        new_val = store.incr(key)
    except TypeError:
        return encode_resp(
            RespValue("ERR value is not an integer or out of range", RespType.ERROR)
        )
    return encode_resp(RespValue(new_val, RespType.INTEGER))

