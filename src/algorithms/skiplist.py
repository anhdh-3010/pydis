import random
from typing import Any


class SkipListNode:
    def __init__(self, score: int | None, member: Any, level: int) -> None:
        self.score = score
        self.member = member
        self.forward: list[SkipListNode | None] = [None] * (level + 1)


class SkipList:
    MAX_LEVEL = 16
    P = 0.5

    def __init__(self) -> None:
        self.header = SkipListNode(None, None, self.MAX_LEVEL)
        self.level = 0
        self.length = 0

    def random_level(self) -> int:
        """Tạo một cấp độ ngẫu nhiên cho nút mới."""
        lvl = 0
        while random.random() < self.P and lvl < self.MAX_LEVEL:
            lvl += 1

        return lvl

    def insert(self, score: int, member: Any) -> None:
        """Chèn một nút mới vào Skip List."""
        update = [self.header] * (self.MAX_LEVEL + 1)
        current = self.header

        # tìm vị trí để chèn
        for i in reversed(range(self.level + 1)):
            next_node = current.forward[i]
            # di chuyển dọc level i tới node trước node có key >= key (hoặc None)
            while (
                next_node
                and next_node.score is not None
                and (
                    next_node.score < score
                    or (next_node.score == score and next_node.member < member)
                )
            ):
                current = next_node
                next_node = current.forward[i]

            update[i] = current  # node trước vị trí chèn ở level i

        current_temp = current.forward[0]

        # nếu member đã tồn tại -> không chèn
        if (
            current_temp
            and current_temp.score == score
            and current_temp.member == member
        ):
            return

        lvl = self.random_level()

        # nếu lvl random mà > level hiện tai -> cập nhập thêm level mới
        if lvl > self.level:
            for i in range(self.level + 1, lvl + 1):
                update[i] = self.header

            self.level = lvl

        new_node = SkipListNode(score, member, lvl)
        for i in range(lvl + 1):
            # nối new_node vào sau update[i]
            new_node.forward[i] = update[i].forward[i]
            update[i].forward[i] = new_node

        self.length += 1

    def remove(self, score: int, member: Any) -> bool:
        update = [self.header] * (self.MAX_LEVEL + 1)
        current = self.header

        # tìm vị trí để chèn
        for i in reversed(range(self.level + 1)):
            next_node = current.forward[i]
            # di chuyển dọc level i tới node trước node có key >= key (hoặc None)
            while (
                next_node
                and next_node.score is not None
                and (
                    next_node.score < score
                    or (next_node.score == score and next_node.member < member)
                )
            ):
                current = next_node
                next_node = current.forward[i]

            update[i] = current  # node trước vị trí chèn ở level i

        current_temp = current.forward[0]

        if (
            current_temp
            and current_temp.score == score
            and current_temp.member == member
        ):
            for i in range(self.level + 1):
                if update[i].forward[i] != current_temp:
                    break

                update[i].forward[i] = current_temp.forward[i]

            while self.level > 0 and not self.header.forward[self.level]:
                self.level -= 1

            self.length -= 1

            return True

        return False

    def get_rank(self, score: int, member: Any) -> int | None:
        """Trả về rank (0-based) của member"""
        rank = 0
        current = self.header
        for i in reversed(range(self.level + 1)):
            next_node = current.forward[i]
            while (
                next_node
                and next_node.score is not None
                and (
                    next_node.score < score
                    or (next_node.score == score and next_node.member < member)
                )
            ):
                rank += 1
                current = next_node
                next_node = current.forward[i]

        current_temp = current.forward[0]
        if (
            current_temp
            and current_temp.score == score
            and current_temp.member == member
        ):
            return rank

        return None

    def __len__(self):
        return self.length
