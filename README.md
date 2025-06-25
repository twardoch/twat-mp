# twat-mp

Parallel processing utilities primarily using the Pathos library for robust synchronous operations. This package provides convenient context managers and decorators for process-based and thread-based parallelism. Support for asynchronous multiprocessing via `aiomultiprocess` is included but considered experimental for the current MVP and will be stabilized in future releases.

## Features

* Core parallel processing options using Pathos:
  + `ProcessPool`: For CPU-intensive parallel processing.
  + `ThreadPool`: For I/O-bound parallel processing.
* Decorators for common synchronous parallel mapping operations:
  + `pmap`: Standard parallel map (eager evaluation).
  + `imap`: Lazy parallel map returning an iterator.
  + `amap`: Asynchronous-style map with automatic result retrieval (uses synchronous Pathos pools).
* Experimental Asynchronous Support (via `aiomultiprocess` - subject to stabilization):
  + `AsyncMultiPool`: For combined async/await with multiprocessing. (*Experimental*)
  + `apmap`: Async parallel map for use with async/await functions. (*Experimental*)
* Automatic CPU core detection for optimal pool sizing.
* Clean resource management with context managers.
* Full type hints and modern Python features.
* Flexible pool configuration with customizable worker count
* Graceful error handling and resource cleanup
* Enhanced exception propagation with detailed context
* Debug mode with comprehensive logging
* Optional dependencies to reduce installation footprint
* Version control system (VCS) based versioning using hatch-vcs

## Recent Updates

* Added debug mode with detailed logging via `set_debug_mode()`
* Enhanced error handling with `WorkerError` (previously `WorkerException`) for better context.
* Improved exception propagation from worker processes.
* Added comprehensive docstrings to all public functions and classes.
* Fixed build system configuration with proper version handling.
* Enhanced error handling and resource cleanup.
* Added comprehensive API reference documentation.
* Added real-world examples for various use cases.

## Installation

Core (Synchronous) Installation:
```bash
pip install twat-mp
```

To include experimental async support (requires `aiomultiprocess`):
```bash
pip install 'twat-mp[aio]'
```

With all extras and development tools:
```bash
pip install 'twat-mp[all,dev]'
```

## Usage

### Basic Synchronous Usage

```python
from twat_mp import ProcessPool, pmap

# Using the pool directly
with ProcessPool() as pool:
    results = pool.map(lambda x: x * 2, range(10))
    print(list(results))

# Using the decorator
@pmap
def double(x):
    return x * 2

results = list(double(range(10)))
print(results)
```

### Async Support (Experimental - For Future Stabilization)

**Note:** Async features are currently considered experimental due to potential environment-specific stability issues (e.g., test hangs). They are provided for early adopters and will be a focus for stabilization in future releases.

The package includes experimental async support through `aiomultiprocess`, allowing you to combine the benefits of async/await with multiprocessing:

```python
import asyncio
from twat_mp import AsyncMultiPool, apmap # Ensure 'aio' extra is installed

# Using the pool directly
async def process_items_async():
    # Note: Ensure AsyncMultiPool and apmap are imported if 'aio' extra is installed
    # and you intend to use these experimental features.
    # from twat_mp import AsyncMultiPool, apmap

    async with AsyncMultiPool() as pool: # Experimental
        async def work(x):
            await asyncio.sleep(0.1)  # Some async work
            return x * 2

        results = await pool.map(work, range(10))
        return results

# Using the decorator
@apmap # Experimental
async def double_async(x):
    await asyncio.sleep(0.1)  # Some async work
    return x * 2

async def main_async_example():
    # results_items = await process_items_async()
    # print(f"Async items processed: {results_items}")

    results_decorated = await double_async(range(10))
    print(f"Async decorated results: {results_decorated}") # [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

# if __name__ == "__main__":
# import asyncio
# asyncio.run(main_async_example())
```

Async support can be useful for:
- Performing CPU-intensive tasks in parallel within an async application.
- Handling many concurrent I/O operations when combined with async patterns.
- Processing results from async APIs in parallel.

### Advanced Async Features (Experimental)

The `AsyncMultiPool` (experimental) provides additional methods for different mapping strategies:

```python
import asyncio
# from twat_mp import AsyncMultiPool # Ensure 'aio' extra

async def main_advanced_async():
    # Note: Ensure AsyncMultiPool is imported if 'aio' extra is installed
    # and you intend to use these experimental features.
    from twat_mp import AsyncMultiPool

    # Using starmap for unpacking arguments
    async def sum_values(a, b):
        await asyncio.sleep(0.01)
        return a + b

    async with AsyncMultiPool() as pool: # Experimental
        # Regular map
        double_results = await pool.map(
            lambda x: x * 2,
            range(5)
        )
        print(f"Async map results: {double_results}")  # [0, 2, 4, 6, 8]

        # Starmap unpacks arguments
        sum_results = await pool.starmap(
            sum_values,
            [(1, 2), (3, 4), (5, 6)]
        )
        print(f"Async starmap results: {sum_results}")  # [3, 7, 11]

        # imap returns an async iterator
        print("Async imap results:")
        async for result in pool.imap(lambda x: x*x, range(3)): # Example with a simple lambda
            print(result)  # Prints 0, 1, 4 as they complete

# if __name__ == "__main__":
# import asyncio
# asyncio.run(main_advanced_async())
```

### Using Process and Thread Pools (Core MVP Feature)

The package provides dedicated context managers for robust synchronous parallel processing:

```python
from twat_mp import ProcessPool, ThreadPool

# For CPU-intensive operations
with ProcessPool() as pool:
    results = pool.map(lambda x: x * x, range(10))
    print(list(results))  # Expected: [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]

# For I/O-bound operations
with ThreadPool() as pool:
    results = pool.map(lambda x: x * 2, range(10))
    print(list(results))  # Expected: [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]

# Custom number of workers
with ProcessPool(nodes=4) as pool:
    results = pool.map(lambda x: x * x, range(10))
    print(list(results))
```

### Using Synchronous Map Decorators (Core MVP Feature)

The package provides three decorators for different synchronous mapping strategies using Pathos pools:

```python
from twat_mp import amap, imap, pmap # These are synchronous for MVP

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

### Debug Mode and Error Handling

The package provides a debug mode for detailed logging and enhanced error handling:

```python
from twat_mp import ProcessPool, set_debug_mode
import time
import random

def process_item(x):
    """Process an item with random delay and potential errors."""
    # Simulate random processing time
    time.sleep(random.random() * 0.5)
    
    # Randomly fail for demonstration
    if random.random() < 0.2:  # 20% chance of failure
        raise ValueError(f"Random failure processing item {x}")
        
    return x * 10

# Enable debug mode for detailed logging
set_debug_mode(True)

try:
    with ProcessPool() as pool:
        results = list(pool.map(process_item, range(10)))
        print(f"Processed results: {results}")
except Exception as e:
    print(f"Caught exception: {e}")
    # The exception will include details about which worker and input item caused the error
finally:
    # Disable debug mode when done
    set_debug_mode(False)
```

The enhanced error handling provides detailed context about failures:

```python
from twat_mp import ProcessPool

def risky_function(x):
    if x == 5:
        raise ValueError("Cannot process item 5")
    return x * 2

try:
    with ProcessPool() as pool:
        results = list(pool.map(risky_function, range(10)))
except ValueError as e:
    # The exception will include the worker ID and input item that caused the error
    print(f"Caught error: {e}")
    # Handle the error appropriately
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

### Web Scraping

Thread pools are ideal for I/O-bound operations like web scraping:

```python
import requests
from bs4 import BeautifulSoup
from twat_mp import ThreadPool

def fetch_page_title(url):
    """Fetch the title of a webpage."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else "No title found"
        return {"url": url, "title": title, "status": response.status_code}
    except Exception as e:
        return {"url": url, "error": str(e), "status": None}

# List of URLs to scrape
urls = [
    "https://www.python.org",
    "https://www.github.com",
    "https://www.stackoverflow.com",
    "https://www.wikipedia.org",
    "https://www.reddit.com"
]

# Use ThreadPool for I/O-bound operations
with ThreadPool() as pool:
    results = list(pool.map(fetch_page_title, urls))

# Print results
for result in results:
    if "error" in result:
        print(f"Error fetching {result['url']}: {result['error']}")
    else:
        print(f"{result['url']} - {result['title']} (Status: {result['status']})")
```

### Data Processing with Pandas

Process large datasets in parallel chunks:

```python
import pandas as pd
import numpy as np
from twat_mp import ProcessPool

def process_chunk(chunk_data):
    """Process a chunk of data."""
    # Simulate some data processing
    chunk_data['processed'] = chunk_data['value'] * 2 + np.random.randn(len(chunk_data))
    chunk_data['category'] = pd.cut(chunk_data['processed'], 
                                    bins=[-np.inf, 0, 10, np.inf], 
                                    labels=['low', 'medium', 'high'])
    # Calculate some statistics
    result = {
        'chunk_id': chunk_data['chunk_id'].iloc[0],
        'mean': chunk_data['processed'].mean(),
        'median': chunk_data['processed'].median(),
        'std': chunk_data['processed'].std(),
        'count': len(chunk_data),
        'categories': chunk_data['category'].value_counts().to_dict()
    }
    return result

# Create a large DataFrame
n_rows = 1_000_000
df = pd.DataFrame({
    'value': np.random.randn(n_rows),
    'group': np.random.choice(['A', 'B', 'C', 'D'], n_rows)
})

# Split into chunks for parallel processing
chunk_size = 100_000
chunks = []
for i, chunk_start in enumerate(range(0, n_rows, chunk_size)):
    chunk_end = min(chunk_start + chunk_size, n_rows)
    chunk = df.iloc[chunk_start:chunk_end].copy()
    chunk['chunk_id'] = i
    chunks.append(chunk)

# Process chunks in parallel
with ProcessPool() as pool:
    results = list(pool.map(process_chunk, chunks))

# Combine results
summary = pd.DataFrame(results)
print(summary)
```

### Async File Processing (Experimental)

This example demonstrates combining async I/O with the experimental `AsyncMultiPool`.

```python
import asyncio
import os
# import aiofiles # Requires separate installation: pip install aiofiles
# from twat_mp import AsyncMultiPool # Ensure 'aio' extra

async def count_words_async(filename):
    """Count words in a file asynchronously."""
    # Note: aiofiles needs to be installed separately.
    # This example is illustrative of how AsyncMultiPool could be used.
    try:
        # Placeholder for async file reading logic
        # async with aiofiles.open(filename, 'r') as f:
        #     content = await f.read()
        #     word_count = len(content.split())
        # return {"filename": filename, "word_count": word_count}
        await asyncio.sleep(0.01) # Simulate async read
        return {"filename": filename, "word_count": len(filename) * 5} # Dummy result
    except Exception as e:
        return {"filename": filename, "error": str(e)}

async def main_async_files():
    # from twat_mp import AsyncMultiPool # Ensure 'aio' extra
    # Create dummy files for example if needed, or use existing text files
    # For real use, ensure 'documents' directory exists and has .txt files
    script_dir = os.path.dirname(__file__) if "__file__" in locals() else "."
    doc_dir = os.path.join(script_dir, "documents_example")
    os.makedirs(doc_dir, exist_ok=True)
    if not os.listdir(doc_dir): # Create dummy files if dir is empty
        for i in range(3):
            with open(os.path.join(doc_dir, f"file{i}.txt"), "w") as f:
                f.write(f"This is dummy file {i} with some words.")

    files = [os.path.join(doc_dir, f) for f in os.listdir(doc_dir)
             if f.endswith(".txt")]

    if not files:
        print("No .txt files found in documents_example directory for async processing example.")
        return

    # Placeholder for AsyncMultiPool usage
    # async with AsyncMultiPool() as pool: # Experimental
    # results = await pool.map(count_words_async, files)
    
    # Simulating results for now as AsyncMultiPool is experimental
    results = [await count_words_async(f) for f in files]


    total_words = sum(r.get("word_count", 0) for r in results if "error" not in r)
    
    print("\nAsync File Processing Results (Experimental):")
    for result in results:
        if "error" in result:
            print(f"Error processing {result['filename']}: {result['error']}")
        else:
            print(f"{result['filename']}: {result['word_count']} words")
    print(f"Total word count (simulated): {total_words}")

# if __name__ == "__main__":
# import asyncio
# asyncio.run(main_async_files())
```

## API Reference

For detailed API documentation, see the [API Reference](API_REFERENCE.md).

## License

MIT
