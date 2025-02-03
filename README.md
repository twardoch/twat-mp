# twat-multi

Parallel processing utilities using Pathos multiprocessing library. This package provides convenient wrappers and decorators around Pathos pools for easy parallel processing.

## Features

- Simple context manager for Pathos pool management
- Decorators for common parallel mapping operations:
  - `amap`: Asynchronous parallel map with automatic result retrieval
  - `imap`: Lazy parallel map returning an iterator
  - `pmap`: Standard parallel map
- Automatic CPU core detection and pool sizing
- Clean resource management with context managers
- Type hints and modern Python features

## Installation

```bash
pip install twat-multi
```

## Usage

### Using the Context Manager

The `pathos_with` context manager provides a clean way to manage Pathos pools:

```python
from twat_multi import pathos_with

with pathos_with() as pool:
    # Pool automatically uses optimal number of processes
    results = pool.map(lambda x: x * 2, range(1000))
    print(results[:5])  # [0, 2, 4, 6, 8]
```

### Using Map Decorators

The package provides three decorators for different mapping strategies:

```python
from twat_multi import amap, imap, pmap

# Asynchronous parallel map (results automatically retrieved)
@amap
def parallel_square(x):
    return x * x

results = parallel_square(range(1000))  # Returns list

# Lazy parallel map (returns iterator)
@imap
def parallel_cube(x):
    return x * x * x

for result in parallel_cube(range(1000)):
    print(result)  # Prints results as they become available

# Standard parallel map
@pmap
def parallel_double(x):
    return x * 2

results = parallel_double(range(1000))  # Returns list
```

### Function Composition

Decorators can be composed for complex parallel operations:

```python
from twat_multi import amap

@amap
def square(x):
    return x * x

@amap
def subtract_one(x):
    return x - 1

# Parallel composition of functions
results = subtract_one(square(range(1000)))
```

### Benchmarking

The package includes a benchmarking utility to compare sequential and parallel performance:

```python
from twat_multi import benchmark_parallel_vs_sequential

# Compare sequential vs parallel performance
benchmark_parallel_vs_sequential(size=1000)
```

## Dependencies

- `pathos`: For parallel processing functionality

## License

MIT License 