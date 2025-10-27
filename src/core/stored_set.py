from typing import Any
from src.algorithms.skiplist import SkipList


class StoredSet:
    def __init__(self) -> None:
        self.map = {}  # member -> score
        self.skip_list = SkipList()

    def zadd(self, member: Any, score: int) -> bool:
        """Thêm hoặc cập nhật member"""
        if member in self.map:
            old_score = self.map[member]
            if old_score != score:
                self.skip_list.remove(old_score, member)

        self.map[member] = score
        self.skip_list.insert(score, member)
        return True

    def zrank(self, member: Any) -> int | None:
        """Trả về rank (0-based)"""
        if member not in self.map:
            return None
        score = self.map[member]
        return self.skip_list.get_rank(score, member)

    def zrem(self, member: Any) -> int:
        """Xoá member"""
        if member not in self.map:
            return 0
        score = self.map[member]
        self.skip_list.remove(score, member)
        del self.map[member]
        return 1

    def zscore(self, member) -> int | None:
        """Trả về score"""
        return self.map.get(member)

    def zcard(self) -> int:
        """Số lượng phần tử"""
        return len(self.skip_list)
