from constants import RespType
from resp import RespValue, encode_resp
from store import Store

store = Store()


def command_ping(args):
    if len(args) > 0:
        return encode_resp(
            RespValue("ERR wrong number of arguments for 'PING'", RespType.ERROR)
        )
    return encode_resp(RespValue("PONG", RespType.SIMPLE_STRING))


def command_echo(args):
    if len(args) != 1:
        return encode_resp(
            RespValue("ERR wrong number of arguments for 'ECHO'", RespType.ERROR)
        )
    return encode_resp(RespValue(args[0], RespType.BULK_STRING))


def command_get(args):
    if len(args) != 1:
        return encode_resp(
            RespValue("ERR wrong number of arguments for 'GET'", RespType.ERROR)
        )
    val = store.get(args[0])
    if val is None:
        return encode_resp(RespValue(None, RespType.NULL))

    return encode_resp(RespValue(val, RespType.BULK_STRING))


def command_set(args):
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


def command_del(args):
    if not args:
        return encode_resp(
            RespValue("ERR wrong number of arguments for 'DEL'", RespType.ERROR)
        )
    deleted = 0
    for key in args:
        if store.delete(key):
            deleted += 1
    return encode_resp(RespValue(deleted, RespType.INTEGER))


def command_expire(args):
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


def command_ttl(args):
    if len(args) != 1:
        return encode_resp(
            RespValue("ERR wrong number of arguments for 'TTL'", RespType.ERROR)
        )
    key = args[0]
    ttl = store.ttl(key)
    return encode_resp(RespValue(ttl, RespType.INTEGER))


def command_persist(args):
    if len(args) != 1:
        return encode_resp(
            RespValue("ERR wrong number of arguments for 'PERSIST'", RespType.ERROR)
        )
    key = args[0]
    result = store.persist(key)
    return encode_resp(RespValue(1 if result else 0, RespType.INTEGER))


def command_setnx(args):
    if len(args) != 2:
        return encode_resp(
            RespValue("ERR wrong number of arguments for 'SETNX'", RespType.ERROR)
        )
    key, value = args
    success = store.setnx(key, value)
    return encode_resp(RespValue(1 if success else 0, RespType.INTEGER))


def command_incr(args):
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
    if not parts:
        return encode_resp(RespValue("ERR empty command", RespType.ERROR))

    cmd = parts[0].upper()
    args = parts[1:]

    handler = COMMANDS.get(cmd)

    if not handler:
        return encode_resp(RespValue(f"ERR unknown command {cmd}", RespType.ERROR))

    result = handler(args)
    return result
