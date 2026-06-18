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
        # [STUDENT TODO] Traverse internal nodes until you reach the target leaf.
        root = self._read_node(self.root_page_id)
        while not root.is_leaf:
            counter = 0
            for i in range(len(root.keys)):
                if key >= root.keys[i]: counter += 1
                else: break
            root = self._read_node(root.children[counter])
        return root.page_id

    def insert(self, key: int, value: int) -> None:
        # [STUDENT TODO] Insert the key/value pair into the correct leaf, split
        # overflowing nodes, and update the root if needed.
        raise NotImplementedError("Students should implement insert.")

    def _insert_recursive(self, page_id: int, key: int, value: int) -> tuple[int, int] | None:
        # [STUDENT TODO] Use recursion to bubble split information back up the tree.
        raise NotImplementedError("Students should implement recursive insert.")

    def _insert_into_leaf(
        self,
        node: BPlusTreeNode,
        key: int,
        value: int,
    ) -> tuple[int, int] | None:
        # [STUDENT TODO] Keep keys sorted within each leaf and define the
        # duplicate-key policy.
        lidx = -1
        for i in range(len(node.keys)):
            if node.keys[i] == key: raise Exception # duplicate
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
        # [STUDENT TODO] Route insertion through the right child and handle a
        # child split by inserting a promoted separator key.
        raise NotImplementedError("Students should implement internal insertion.")

    def _split_leaf(self, node: BPlusTreeNode) -> tuple[int, int]:
        # [STUDENT TODO] Split an overflowing leaf and maintain the leaf links.
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
        # [STUDENT TODO] Split an overflowing internal node and return the
        # promoted separator key.
        raise NotImplementedError("Students should implement internal splitting.")

    def search(self, key: int) -> int | None:
        # [STUDENT TODO] Use the leaf traversal helper and scan the leaf for an
        # exact-match lookup.
        leaf = self._read_node(self._find_leaf_page(key))
        for i in range(len(leaf.keys)):
            if leaf.keys[i] == key: return leaf.values[i]
        return None

    def range_search(self, start_key: int, end_key: int) -> list[tuple[int, int]]:
        # [STUDENT TODO] Walk the linked leaf pages to support range queries.
        raise NotImplementedError("Students should implement range_search.")


__all__ = ["BPlusTreeNode", "BPlusTree"]
