# twat-mp

`twat-mp` provides parallel processing utilities built on [Pathos](https://pathos.readthedocs.io/en/latest/), designed to make it easy to run CPU-bound and I/O-bound work across multiple processes or threads.

It is part of the [**twat**](https://pypi.org/project/twat/) ecosystem — a collection of focused Python utilities that plug into a common host package.

## Installation

```bash
pip install twat-mp
```

For async multiprocessing support (experimental):

```bash
pip install twat-mp[aio]
```

## Quick start

### Decorator API

```python
from twat_mp import pmap

@pmap
def resize_image(path: str) -> str:
    # expensive CPU work here
    return output_path

results = list(resize_image(image_paths))   # processed in parallel
```

### Context manager API

```python
from twat_mp import ProcessPool, ThreadPool

# CPU-bound: use ProcessPool (bypasses the GIL)
with ProcessPool(nodes=4) as pool:
    squares = pool.map(lambda x: x**2, range(100))

# I/O-bound: use ThreadPool (lighter, avoids pickling overhead)
with ThreadPool(nodes=8) as pool:
    statuses = pool.map(fetch_url, urls)
```

## When to use which pool

| Workload | Pool | Why |
|---|---|---|
| Number crunching, image processing | `ProcessPool` | Bypasses Python's GIL; true parallel execution |
| Network requests, file reads | `ThreadPool` | Lightweight; avoids process-spawn overhead |

## Decorator variants

| Decorator | Evaluation | Returns | Best for |
|---|---|---|---|
| `pmap` | Eager | `list` | Typical parallel map |
| `imap` | Lazy | `iterator` | Large inputs, streaming results |
| `amap` | Submit-now / collect-later | `list` | Fire-and-collect pattern |
| `mmap(how)` | Configurable | varies | Custom strategies |

## Error handling

Errors raised inside worker functions are captured as `WorkerError` when using the pool context managers directly. When using the decorators (`pmap`, `imap`, `amap`), the original exception is re-raised transparently.

```python
from twat_mp import pmap
from twat_mp.mp import WorkerError

@pmap
def risky(x: int) -> int:
    if x < 0:
        raise ValueError(f"negative input: {x}")
    return x * x

try:
    list(risky([-1, 2, 3]))
except ValueError as e:
    print(f"caught: {e}")  # original exception propagated
```
