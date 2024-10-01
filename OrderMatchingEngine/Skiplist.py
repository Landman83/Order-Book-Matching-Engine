import random
from typing import Optional, Tuple, Any

class Node:
    def __init__(self, key: float, value: Any):
        self.key = key
        self.value = value
        self.forward = []

class SkipList:
    def __init__(self, max_level: int = 16, p: float = 0.5):
        self.max_level = max_level
        self.p = p
        self.header = Node(None, None)
        self.header.forward = [None] * max_level
        self.level = 0

    def _random_level(self) -> int:
        lvl = 1
        while random.random() < self.p and lvl < self.max_level:
            lvl += 1
        return lvl

    def insert(self, key: float, value: Any) -> None:
        update = [None] * self.max_level
        current = self.header

        for i in range(self.level - 1, -1, -1):
            while current.forward[i] and current.forward[i].key < key:
                current = current.forward[i]
            update[i] = current

        level = self._random_level()

        if level > self.level:
            for i in range(self.level, level):
                update[i] = self.header
            self.level = level

        new_node = Node(key, value)
        for i in range(level):
            new_node.forward.append(update[i].forward[i])
            update[i].forward[i] = new_node

    def delete(self, key: float) -> Optional[Any]:
        update = [None] * self.max_level
        current = self.header

        for i in range(self.level - 1, -1, -1):
            while current.forward[i] and current.forward[i].key < key:
                current = current.forward[i]
            update[i] = current

        current = current.forward[0]

        if current and current.key == key:
            for i in range(self.level):
                if update[i].forward[i] != current:
                    break
                update[i].forward[i] = current.forward[i]

            while self.level > 1 and self.header.forward[self.level - 1] is None:
                self.level -= 1

            return current.value

        return None

    def search(self, key: float) -> Optional[Any]:
        current = self.header

        for i in range(self.level - 1, -1, -1):
            while current.forward[i] and current.forward[i].key < key:
                current = current.forward[i]

        current = current.forward[0]

        if current and current.key == key:
            return current.value

        return None

    def pop(self, key: float) -> Optional[Tuple[float, Any]]:
        value = self.delete(key)
        if value is not None:
            return (key, value)
        return None

    def __iter__(self):
        current = self.header.forward[0]
        while current:
            yield current.key, current.value
            current = current.forward[0]

    def __len__(self):
        count = 0
        current = self.header.forward[0]
        while current:
            count += 1
            current = current.forward[0]
        return count

    def __getitem__(self, key: float) -> Any:
        value = self.search(key)
        if value is None:
            raise KeyError(key)
        return value

    def __setitem__(self, key: float, value: Any) -> None:
        self.insert(key, value)

    def __contains__(self, key: float) -> bool:
        return self.search(key) is not None

    def __repr__(self):
        items = list(self)
        return f"SkipList({items})"