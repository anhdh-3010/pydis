# A simple in-memory key-value database

### Run server

```bash
# use uv
uv run python -m pydis.server
````

### Connect with redis-cli

```bash
redis-cli -p 65432
```

## Testing

```bash
uv run pytest tests/ -v
```

## Commands supported

### String Commands
- `PING` - Ping server
- `ECHO message` - Echo message
- `GET key` - Get value
- `SET key value [EX seconds]` - Set value with optional TTL
- `SETNX key value` - Set if not exists
- `INCR key` - Increment integer value

### Key Commands
- `DEL key [key ...]` - Delete keys
- `EXPIRE key seconds` - Set TTL
- `TTL key` - Get remaining TTL
- `PERSIST key` - Remove TTL

## Todo list

### New Commands 
- `hash.py` - HSET, HGET, HDEL, HGETALL, etc.
- `list.py` - LPUSH, RPUSH, LPOP, RPOP, LRANGE, etc.
- `set.py` - SADD, SREM, SMEMBERS, SINTER, etc.
- `sorted_set.py` - ZADD, ZRANGE, ZRANK, etc.

### Algorithms 
- LRU/LFU cache eviction policies
- HyperLogLog cho cardinality estimation
- Bloom filters
- Geospatial indexing

### Other Features
- Persistence (RDB, AOF)
- Replication
- Pub/Sub
- Transactions (MULTI/EXEC)

## Architecture

- **Non-blocking I/O**: Sử dụng `selectors` để xử lý multiple connections
- **Thread-safe**: Store sử dụng locks cho thread safety
- **TTL Management**: Background thread tự động evict expired keys
- **RESP Protocol**: Fully compliant với Redis protocol
