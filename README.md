# A Redis Clone in Python

Pydis là một implementation của Redis được viết bằng Python, hỗ trợ RESP protocol và các commands cơ bản.

## 📁 Cấu trúc dự án

```
pydis/
├── src/
│   └── pydis/
│       ├── __init__.py
│       ├── server.py              # Server chính với socket handling
│       ├── core/                  # Storage engine
│       │   ├── __init__.py
│       │   └── store.py           # In-memory store với TTL support
│       ├── protocol/              # RESP protocol implementation
│       │   ├── __init__.py
│       │   ├── resp.py            # RESP encoder/decoder
│       │   └── constants.py       # RESP types
│       ├── commands/              # Redis commands (organized by data type)
│       │   ├── __init__.py
│       │   ├── executor.py        # Command executor & registry
│       │   ├── string.py          # String commands (GET, SET, INCR, etc.)
│       │   └── key.py             # Key commands (DEL, EXPIRE, TTL, etc.)
│       └── algorithms/            # Algorithms (for future implementations)
│           └── __init__.py
├── tests/                         # Test suite
│   ├── __init__.py
│   ├── commands_test.py
│   └── resp_test.py
├── pyproject.toml
├── README.md
└── uv.lock
```

### Chạy server

```bash
# Sử dụng uv
uv run python -m pydis.server
```

Server sẽ chạy trên `127.0.0.1:65432`

### Kết nối với redis-cli

```bash
redis-cli -p 65432
```

## Testing

```bash
uv run pytest tests/ -v
```

## Commands được hỗ trợ

### String Commands
- `PING` - Ping server
- `ECHO message` - Echo message
- `GET key` - Get value
- `SET key value [EX seconds]` - Set value với optional TTL
- `SETNX key value` - Set if not exists
- `INCR key` - Increment integer value

### Key Commands
- `DEL key [key ...]` - Delete keys
- `EXPIRE key seconds` - Set TTL
- `TTL key` - Get remaining TTL
- `PERSIST key` - Remove TTL

## Tương lai

### Commands mới (trong `src/pydis/commands/`)
- `hash.py` - HSET, HGET, HDEL, HGETALL, etc.
- `list.py` - LPUSH, RPUSH, LPOP, RPOP, LRANGE, etc.
- `set.py` - SADD, SREM, SMEMBERS, SINTER, etc.
- `sorted_set.py` - ZADD, ZRANGE, ZRANK, etc.

### Algorithms (trong `src/pydis/algorithms/`)
- LRU/LFU cache eviction policies
- HyperLogLog cho cardinality estimation
- Bloom filters
- Geospatial indexing

### Features khác
- Persistence (RDB, AOF)
- Replication
- Pub/Sub
- Transactions (MULTI/EXEC)

## 🏗️ Kiến trúc

- **Non-blocking I/O**: Sử dụng `selectors` để xử lý multiple connections
- **Thread-safe**: Store sử dụng locks cho thread safety
- **TTL Management**: Background thread tự động evict expired keys
- **RESP Protocol**: Fully compliant với Redis protocol
