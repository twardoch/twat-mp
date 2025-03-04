# twat-mp

Parallel processing utilities using Pathos and aiomultiprocess libraries. This package provides convenient context managers and decorators for parallel processing, with process-based, thread-based, and async-based pools.

## Features

* Multiple parallel processing options:
  + `ProcessPool`: For CPU-intensive parallel processing using Pathos
  + `ThreadPool`: For I/O-bound parallel processing using Pathos
  + `AsyncMultiPool`: For combined async/await with multiprocessing using aiomultiprocess
* Decorators for common parallel mapping operations:
  + `pmap`: Standard parallel map (eager evaluation)
  + `imap`: Lazy parallel map returning an iterator
  + `amap`: Asynchronous map with automatic result retrieval
  + `apmap`: Async parallel map for use with async/await functions
* Automatic CPU core detection for optimal pool sizing
* Clean resource management with context managers
* Full type hints and modern Python features
* Flexible pool configuration with customizable worker count
* Graceful error handling and resource cleanup
* Optional dependencies to reduce installation footprint
* Version control system (VCS) based versioning using hatch-vcs

## Recent Updates

* Fixed build system configuration with proper version handling
* Enhanced error handling and resource cleanup
* Improved compatibility with Python 3.12+ async features
* Added comprehensive API reference documentation
* Added real-world examples for various use cases

## Installation

Basic installation:
```bash
pip install twat-mp
```

With async support:
```bash
pip install 'twat-mp[aio]'
```

With all extras and development tools:
```bash
pip install 'twat-mp[all,dev]'
```

## Usage

### Basic Usage

```python
from twat_mp import ProcessPool, pmap

# Using the pool directly
with ProcessPool() as pool:
    results = pool.map(lambda x: x * 2, range(10))

# Using the decorator
@pmap
def double(x):
    return x * 2

results = double(range(10))
```

### Async Support

The package provides async support through `aiomultiprocess`, allowing you to combine the benefits of async/await with multiprocessing:

```python
import asyncio
from twat_mp import AsyncMultiPool, apmap

# Using the pool directly
async def process_items():
    async with AsyncMultiPool() as pool:
        async def work(x):
            await asyncio.sleep(0.1)  # Some async work
            return x * 2

        results = await pool.map(work, range(10))
        return results

# Using the decorator
@apmap
async def double(x):
    await asyncio.sleep(0.1)  # Some async work
    return x * 2

async def main():
    results = await double(range(10))
    print(results)  # [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

asyncio.run(main())
```

The async support is particularly useful when you need to:
- Perform CPU-intensive tasks in parallel
- Handle many concurrent I/O operations
- Combine async/await with true multiprocessing
- Process results from async APIs in parallel

### Advanced Async Features

The `AsyncMultiPool` provides additional methods for different mapping strategies:

```python
import asyncio
from twat_mp import AsyncMultiPool

async def main():
    # Using starmap for unpacking arguments
    async def sum_values(a, b):
        await asyncio.sleep(0.01)
        return a + b

    async with AsyncMultiPool() as pool:
        # Regular map
        double_results = await pool.map(
            lambda x: x * 2,
            range(5)
        )
        print(double_results)  # [0, 2, 4, 6, 8]

        # Starmap unpacks arguments
        sum_results = await pool.starmap(
            sum_values,
            [(1, 2), (3, 4), (5, 6)]
        )
        print(sum_results)  # [3, 7, 11]

        # imap returns an async iterator
        async for result in pool.imap(sum_values, [(1, 1), (2, 2), (3, 3)]):
            print(result)  # Prints 2, 4, 6 as they complete

asyncio.run(main())
```

### Using Process and Thread Pools

The package provides dedicated context managers for both process and thread pools:

```python
from twat_mp import ProcessPool, ThreadPool

# For CPU-intensive operations
with ProcessPool() as pool:
    results = pool.map(lambda x: x * x, range(10))
    print(list(results))  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# For I/O-bound operations
with ThreadPool() as pool:
    results = pool.map(lambda x: x * 2, range(10))
    print(list(results))  # [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

# Custom number of workers
with ProcessPool(nodes=4) as pool:
    results = pool.map(lambda x: x * x, range(10))
```

### Using Map Decorators

The package provides three decorators for different mapping strategies:

```python
from twat_mp import amap, imap, pmap

# Standard parallel map (eager evaluation)
@pmap
def square(x: int) -> int:
    return x * x

results = list(square(range(10)))
print(results)  # [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# Lazy parallel map (returns iterator)
@imap
def cube(x: int) -> int:
    return x * x * x

for result in cube(range(5)):
    print(result)  # Prints results as they become available

# Asynchronous parallel map with automatic result retrieval
@amap
def double(x: int) -> int:
    return x * 2

results = list(double(range(10)))
print(results)  # [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
```

### Function Composition

Decorators can be composed for complex parallel operations:

```python
from twat_mp import amap

@amap
def compute_intensive(x: int) -> int:
    result = x
    for _ in range(1000):  # Simulate CPU-intensive work
        result = (result * x + x) % 10000
    return result

@amap
def io_intensive(x: int) -> int:
    import time
    time.sleep(0.001)  # Simulate I/O wait
    return x * 2

# Chain parallel operations
results = list(io_intensive(compute_intensive(range(100))))
```

## Real-World Examples

### Image Processing

Processing images in parallel can significantly speed up operations like resizing, filtering, or format conversion:

```python
from twat_mp import ProcessPool
from PIL import Image
import os

def resize_image(file_path):
    """Resize an image to 50% of its original size."""
    try:
        with Image.open(file_path) as img:
            # Get the original size
            width, height = img.size
            # Resize to 50%
            resized = img.resize((width // 2, height // 2))
            # Save with '_resized' suffix
            output_path = os.path.splitext(file_path)[0] + '_resized' + os.path.splitext(file_path)[1]
            resized.save(output_path)
            return output_path
    except Exception as e:
        return f"Error processing {file_path}: {e}"

# Get all image files in a directory
image_files = [f for f in os.listdir('images') if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
image_paths = [os.path.join('images', f) for f in image_files]

# Process images in parallel
with ProcessPool() as pool:
    results = list(pool.map(resize_image, image_paths))

print(f"Processed {len(results)} images")
```

### Data Processing with Pandas

Splitting a large DataFrame into chunks and processing them in parallel:

```python
from twat_mp import ProcessPool
import pandas as pd
import numpy as np

def process_chunk(chunk):
    """Apply complex transformations to a DataFrame chunk."""
    # Simulate CPU-intensive calculations
    chunk['calculated'] = np.sqrt(chunk['value'] ** 2 + chunk['other_value'] ** 2)
    chunk['category'] = chunk['calculated'].apply(lambda x: 'high' if x > 50 else 'medium' if x > 20 else 'low')
    return chunk

# Create a large DataFrame
df = pd.DataFrame({
    'value': np.random.randint(1, 100, 100000),
    'other_value': np.random.randint(1, 100, 100000)
})

# Split into chunks
chunk_size = 10000
chunks = [df.iloc[i:i+chunk_size] for i in range(0, len(df), chunk_size)]

# Process chunks in parallel
with ProcessPool() as pool:
    processed_chunks = list(pool.map(process_chunk, chunks))

# Combine results
result_df = pd.concat(processed_chunks)
print(f"Processed DataFrame with {len(result_df)} rows")
```

### Web Scraping with Async Support

Using the async capabilities to scrape multiple web pages concurrently:

```python
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from twat_mp import AsyncMultiPool, apmap

async def fetch_page(url):
    """Fetch a web page and extract its title."""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    title = soup.title.string if soup.title else "No title found"
                    return {'url': url, 'title': title, 'status': response.status}
                else:
                    return {'url': url, 'error': f'Status code: {response.status}', 'status': response.status}
        except Exception as e:
            return {'url': url, 'error': str(e), 'status': None}

# Use the decorator for parallel processing
@apmap
async def fetch_all_pages(url):
    return await fetch_page(url)

async def main():
    # List of URLs to scrape
    urls = [
        'https://python.org',
        'https://github.com',
        'https://stackoverflow.com',
        'https://news.ycombinator.com',
        'https://reddit.com'
    ]

    # Fetch all pages in parallel
    results = await fetch_all_pages(urls)

    # Print results
    for result in results:
        if 'error' in result:
            print(f"Error fetching {result['url']}: {result['error']}")
        else:
            print(f"Title of {result['url']}: {result['title']}")

if __name__ == "__main__":
    asyncio.run(main())
```

### File System Operations

Processing files in a directory structure:

```python
from twat_mp import ThreadPool
import os
import hashlib

def calculate_file_hash(file_path):
    """Calculate SHA-256 hash of a file."""
    if not os.path.isfile(file_path):
        return (file_path, None, "Not a file")

    try:
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            # Read in chunks to handle large files
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return (file_path, hasher.hexdigest(), None)
    except Exception as e:
        return (file_path, None, str(e))

def find_files(directory):
    """Recursively find all files in a directory."""
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths

# Get all files in a directory
files = find_files('/path/to/directory')

# Use ThreadPool for I/O-bound operations
with ThreadPool() as pool:
    results = list(pool.map(calculate_file_hash, files))

# Process results
for file_path, file_hash, error in results:
    if error:
        print(f"Error processing {file_path}: {error}")
    else:
        print(f"{file_path}: {file_hash}")

## Dependencies

* `pathos`: For process and thread-based parallel processing
* `aiomultiprocess` (optional): For async-based parallel processing

## Development

To set up the development environment:

```bash
# Install in development mode with test dependencies
uv pip install -e ".[test]"

# Install with async support for testing all features
uv pip install -e ".[aio,test]"

# Run tests
python -m pytest tests/

# Run benchmarks
python -m pytest tests/test_benchmark.py
```

## License

MIT License
.
