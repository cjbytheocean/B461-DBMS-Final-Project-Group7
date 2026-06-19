"""
Project: B461-Database Concepts - Summer 2026
Author: [Student Name]
Role: Student Starter Code

Students are expected to complete the TODO sections in this file.
Do not modify protected sections marked as [INSTRUCTOR ONLY].
"""

"""Simplified B+ tree for the student starter."""

import json
from bisect import bisect_left, bisect_right
from dataclasses import dataclass, field

try:
    from .buffer_pool_manager import BufferPoolManager
    from .config import BPLUS_ORDER
except ImportError:
    from buffer_pool_manager import BufferPoolManager
    from config import BPLUS_ORDER


@dataclass
class BPlusTreeNode:
    page_id: int
    is_leaf: bool
    keys: list[int] = field(default_factory=list)
    values: list[int] = field(default_factory=list)
    children: list[int] = field(default_factory=list)
    next_leaf: int | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "page_id": self.page_id,
            "is_leaf": self.is_leaf,
            "keys": self.keys,
            "values": self.values,
            "children": self.children,
            "next_leaf": self.next_leaf,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> "BPlusTreeNode":
        return cls(
            page_id=int(payload["page_id"]),
            is_leaf=bool(payload["is_leaf"]),
            keys=[int(value) for value in payload.get("keys", [])],
            values=[int(value) for value in payload.get("values", [])],
            children=[int(value) for value in payload.get("children", [])],
            next_leaf=payload.get("next_leaf"),
        )


# ================================
# [STUDENT TODO] IMPLEMENT BELOW
# ================================
class BPlusTree:
    def __init__(
        self,
        buffer_pool_manager: BufferPoolManager,
        order: int = BPLUS_ORDER,
    ) -> None:
        if order < 3:
            raise ValueError("B+ tree order must be at least 3.")

        self.buffer_pool_manager = buffer_pool_manager
        self.order = order
        root = self._allocate_node(is_leaf=True)
        self.root_page_id = root.page_id

    def _serialize(self, node: BPlusTreeNode) -> bytes:
        encoded = json.dumps(node.to_dict(), separators=(",", ":")).encode("utf-8")
        if len(encoded) > self.buffer_pool_manager.disk_manager.page_size:
            raise ValueError("Serialized B+ tree node does not fit in one page.")
        return encoded

    def _allocate_node(self, is_leaf: bool) -> BPlusTreeNode:
        page = self.buffer_pool_manager.new_page()
        node = BPlusTreeNode(page_id=page.page_id, is_leaf=is_leaf)
        self._write_node(node)
        self.buffer_pool_manager.unpin_page(node.page_id)
        return node

    def _read_node(self, page_id: int) -> BPlusTreeNode:
        page = self.buffer_pool_manager.fetch_page(page_id)
        raw = bytes(page.data).rstrip(b"\x00")
        self.buffer_pool_manager.unpin_page(page_id)
        if not raw:
            raise ValueError(f"Page {page_id} does not contain a valid B+ tree node.")
        return BPlusTreeNode.from_dict(json.loads(raw.decode("utf-8")))

    def _write_node(self, node: BPlusTreeNode) -> None:
        page = self.buffer_pool_manager.fetch_page(node.page_id)
        payload = self._serialize(node)
        page.data[:] = b"\x00" * len(page.data)
        page.data[: len(payload)] = payload
        self.buffer_pool_manager.unpin_page(node.page_id, is_dirty=True)

    def _find_leaf_page(self, key: int) -> int:
        root = self._read_node(self.root_page_id)
        while not root.is_leaf:
            counter = 0
            for i in range(len(root.keys)):
                if key >= root.keys[i]: counter += 1
                else: break
            root = self._read_node(root.children[counter])
        return root.page_id

    def insert(self, key: int, value: int) -> None:
        insertion = self._insert_recursive(self.root_page_id, key, value)
        if insertion:
            page_id, new_key = insertion
            new_node = self._allocate_node(False)
            new_node.keys.append(new_key)
            new_node.children.append(self.root_page_id)
            new_node.children.append(page_id)
            self._write_node(new_node)
            self.root_page_id = new_node.page_id

    def _insert_recursive(self, page_id: int, key: int, value: int) -> tuple[int, int] | None:
        node = self._read_node(page_id)
        if node.is_leaf: return self._insert_into_leaf(node, key, value)
        else: return self._insert_into_internal(node, key, value)

    def _insert_into_leaf(
        self,
        node: BPlusTreeNode,
        key: int,
        value: int,
    ) -> tuple[int, int] | None:
        lidx = -1
        for i in range(len(node.keys)):
            if node.keys[i] == key:
                node.values[i] = value
                self._write_node(node)
                return None
            elif node.keys[i] < key: lidx = i
            else: pass
        node.keys.insert(lidx + 1, key)
        node.values.insert(lidx + 1, value)
        if len(node.keys) == self.order:
            return self._split_leaf(node)
        else:
            self._write_node(node)
            return None

    def _insert_into_internal(
        self,
        node: BPlusTreeNode,
        key: int,
        value: int,
    ) -> tuple[int, int] | None:
        idx = 0
        for i in range(len(node.keys)):
            if key <= node.keys[i]: break
            idx += 1
        ins = self._insert_recursive(node.children[idx], key, value)
        if ins:
            page_id, new_key = ins
            c = 0
            for v in node.keys:
                if v < new_key:
                    c += 1
            node.keys.insert(c, new_key)
            node.children.insert(c + 1, page_id)
            if len(node.keys) == self.order: return self._split_internal(node)
            else:
                self._write_node(node)
                return None
        else: return None

    def _split_leaf(self, node: BPlusTreeNode) -> tuple[int, int]:
        mp_idx = len(node.keys) // 2
        left = (node.keys[:mp_idx], node.values[:mp_idx])
        right = (node.keys[mp_idx:], node.values[mp_idx:])
        node.keys = left[0]
        node.values = left[1]
        rhs = self._allocate_node(True)
        rhs.keys = right[0]
        rhs.values = right[1]
        rhs.next_leaf = node.next_leaf
        node.next_leaf = rhs.page_id
        self._write_node(node)
        self._write_node(rhs)
        return (rhs.page_id, rhs.keys[0])

    def _split_internal(self, node: BPlusTreeNode) -> tuple[int, int]:
        mp_idx = len(node.keys) // 2
        mid_key = node.keys[mp_idx]
        left_internal = node.keys[:mp_idx]
        left_children = node.children[:mp_idx+1]
        right_internal = node.keys[mp_idx+1:]
        right_children = node.children[mp_idx+1:]
        new_node = self._allocate_node(False)
        new_node.keys = right_internal
        new_node.children = right_children
        node.keys = left_internal
        node.children = left_children
        self._write_node(new_node)
        self._write_node(node)
        return (new_node.page_id, mid_key)

    def search(self, key: int) -> int | None:
        leaf = self._read_node(self._find_leaf_page(key))
        for i in range(len(leaf.keys)):
            if leaf.keys[i] == key: return leaf.values[i]
        return None

    def range_search(self, start_key: int, end_key: int) -> list[tuple[int, int]]:
        leaf = self._read_node(self._find_leaf_page(start_key))
        res = []
        while leaf.next_leaf is not None:
            res += [(leaf.keys[i], leaf.values[i]) for i in range(len(leaf.keys)) if leaf.keys[i] >= start_key and leaf.keys[i] <= end_key]
            leaf = self._read_node(leaf.next_leaf)

        res += [(leaf.keys[i], leaf.values[i]) for i in range(len(leaf.keys)) if leaf.keys[i] >= start_key and leaf.keys[i] <= end_key]
        return res


__all__ = ["BPlusTreeNode", "BPlusTree"]
