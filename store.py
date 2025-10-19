import random
import threading
import time
from typing import Any


class Store:
    def __init__(self):
        # main data: key -> value
        self.data: dict[str, Any] = {}
        # TTL: key -> expire_timestamp
        self.expire_times: dict[str, float] = {}
        self.lock = threading.Lock()

        self._stop_eviction = False
        self._eviction_thread = threading.Thread(
            target=self._evict_expired_keys_loop, daemon=True
        )
        self._eviction_thread.start()

    def _evict_expired_keys_loop(self):
        """Chạy nền: mỗi giây kiểm tra ngẫu nhiên các key"""
        while not self._stop_eviction:
            time.sleep(1)
            self._evict_sample()

    def _evict_sample(self, sample_size: int = 20):
        """Chọn ngẫu nhiên 1 số key đã hết hạn để xoá"""
        with self.lock:
            if not self.expire_times:
                return
            sample_key = random.sample(
                list(self.expire_times.keys()),
                k=min(sample_size, len(self.expire_times)),
            )

            for key in sample_key:
                self._is_expired(key)

    def _is_expired(self, key: str) -> bool:
        expire_time = self.expire_times.get(key)
        if expire_time is None:
            return False

        if time.time() > expire_time:
            self.data.pop(key, None)
            self.expire_times.pop(key, None)
            return True

        return False

    def set(self, key: str, value: Any, ex: int | None):
        with self.lock:
            self.data[key] = value
            if ex is not None:
                self.expire_times[key] = time.time() + ex
            elif key in self.expire_times:
                self.expire_times.pop(key)

    def setnx(self, key: str, value: Any) -> bool:
        """Chỉ set khi key chưa tồn tại"""
        with self.lock:
            if key in self.data and not self._is_expired(key):
                return False

            self.data[key] = value
            return True

    def incr(self, key: str) -> int:
        """tăng giá trị của value lên 1"""
        with self.lock:
            if self._is_expired(key):
                self.data.pop(key, None)
            val = self.data.get(key, 0)
            try:
                new_val = int(val) + 1
            except ValueError:
                raise TypeError(f"Value for key '{key}' is not an integer")
            self.data[key] = new_val

            return new_val

    def get(self, key: str) -> Any | None:
        if key not in self.data:
            return None
        if self._is_expired(key):
            return None

        return self.data[key]

    def delete(self, key: str) -> bool:
        with self.lock:
            existed = key in self.data
            self.data.pop(key, None)
            self.expire_times.pop(key, None)
            return existed

    def ttl(self, key: str) -> int:
        if key not in self.data:
            return -2  # key not found
        if key not in self.expire_times:
            return -1  # not have ttl
        remaining = int(self.expire_times[key] - time.time())
        if remaining < 0:
            self._is_expired(key)
            return -2

        return remaining

    def expire(self, key: str, seconds: int) -> bool:
        if key not in self.data:
            return False

        with self.lock:
            self.expire_times[key] = time.time() + seconds

        return True

    def persist(self, key: str) -> bool:
        """Xoá ttl của key"""
        with self.lock:
            return self.expire_times.pop(key, None) is not None

    def stop(self):
        self._stop_eviction = True
        self._eviction_thread.join(timeout=1)
