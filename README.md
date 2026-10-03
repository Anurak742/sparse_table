# sparse_table

A small Python library that preprocesses an immutable sequence so idempotent range queries (minimum, maximum, gcd, bit-and) answer in O(1).

## Usage

```python
from sparse_table import SparseTable

data = [3, 1, 4, 1, 5, 9, 2, 6]
st = SparseTable(data, min)

assert st.query(0, len(data)) == 1   # whole-array minimum
assert st.query(2, 5) == 1           # min of [4, 1, 5]

# Index a list of records by one field, return the record itself:
people = [("alice", 30), ("bob", 25), ("carol", 35)]
by_age = SparseTable(people, lambda a, b: a if a[1] < b[1] else b, value=lambda p: p[1])
assert by_age.query(0, 3) == ("bob", 25)
```

## Why

Range-minimum over an immutable array is a classic pain point: a naive scan is O(n) per query, a segment tree is O(log n) per query with O(n) build, and a sparse table is O(1) per query with O(n log n) build. This library exists for the case where you build once and query many times against data that never changes. The trade-off is memory: the table stores roughly n log n elements.

The operation must be **idempotent** — `op(x, x) == x`. The query answers by combining two overlapping power-of-two blocks; idempotence makes the overlap harmless. Use this for `min`, `max`, `gcd`, `bitwise_and`. Do **not** use it for `sum` or `product`: overlapping blocks double-count.

## Edge cases

- `query(l, r)` uses a half-open interval and requires `0 <= l < r <= n`. An empty range (`l == r`) raises `IndexError`, since there is no element to return.
- The table keeps a shallow copy of the input as a list, so mutating the original sequence after construction has no effect on queries.
- The optional `value` callable is applied to each element at build time only; `query` returns the original element, not the projection.

## Exported names

- `SparseTable` — the only public class. Constructor: `SparseTable(data, op, *, value=identity)`. Method: `query(l, r)`. Property: `n`.

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.

