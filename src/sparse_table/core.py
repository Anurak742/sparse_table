from __future__ import annotations

import math
from typing import Callable, List, Sequence, TypeVar

T = TypeVar("T")


def _identity(x: T) -> T:
    return x


class SparseTable:
    """Preprocess an immutable sequence for idempotent range queries.

    A sparse table answers queries of the form "reduce the contiguous
    sub-sequence ``data[l:r]``" in O(1) time after O(n log n) preprocessing,
    provided the reduction operation is **idempotent**: ``op(x, x) == x``.
    Minimum, maximum, gcd, and bit-and satisfy this; sum and product do not
    (they double-count overlapping blocks).

    The trick that makes queries O(1) is covering ``[l, r)`` with two
    overlapping power-of-two blocks whose union is exactly ``[l, r)``. Because
    the operation is idempotent, the overlap is harmless. We precompute every
    block of length 2^k starting at every position, then answer a query with
    ``op(table[k][l], table[k][r - 2^k])`` where ``k = floor(log2(r - l))``.

    The constructor accepts an optional ``value`` transform applied to each
    element before indexing. The common use case is indexing a list of objects
    (records, tuples) by one comparable field while returning the original
    element. Passing ``value`` lets us store the original elements in the table
    and only compare on the projection, so ``query`` returns the element itself
    rather than the projection.
    """

    def __init__(
        self,
        data: Sequence[T],
        op: Callable[[T, T], T],
        *,
        value: Callable[[T], T] = _identity,
    ) -> None:
        if not callable(op):
            raise TypeError("op must be callable")
        if not callable(value):
            raise TypeError("value must be callable")

        self._op = op
        self._value = value
        n = len(data)
        self._n = n
        self._data: List[T] = list(data)

        if n == 0:
            self._levels: List[List[T]] = []
            self._log: List[int] = [0]
            return

        # Precompute floor(log2(k)) for k up to n so each query is a lookup
        # rather than a per-call math.log2 (avoids float round-trip too).
        log = [0] * (n + 1)
        for k in range(1, n + 1):
            log[k] = log[k - 1] + (1 << (log[k - 1] + 1) <= k)
        self._log = log

        # Level 0 is the raw (transformed) data.
        levels: List[List[T]] = [self._data[:]]
        # number of blocks of length 2^k that fit is n - (1 << k) + 1
        k = 1
        while (1 << k) <= n:
            prev = levels[k - 1]
            length = n - (1 << k) + 1
            row: List[T] = [None] * length  # type: ignore[list-item]
            half = 1 << (k - 1)
            for i in range(length):
                row[i] = op(prev[i], prev[i + half])
            levels.append(row)
            k += 1
        self._levels = levels

    def query(self, l: int, r: int) -> T:
        """Return ``op`` over ``data[l:r]`` (half-open interval).

        Requires ``0 <= l < r <= n``. Single-element queries (``l + 1 == r``)
        return ``data[l]``.
        """
        n = self._n
        if not (0 <= l < r <= n):
            raise IndexError(f"invalid range [{l}, {r}) for length {n}")
        width = r - l
        k = self._log[width]
        row = self._levels[k]
        # Two overlapping blocks of length 2^k whose union is [l, r):
        #   [l, l + 2^k) and [r - 2^k, r). Idempotence makes overlap safe.
        left = row[l]
        right = row[r - (1 << k)]
        return self._op(left, right)

    @property
    def n(self) -> int:
        return self._n
