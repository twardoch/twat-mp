# twat-mp: Parallel Processing Utilities for Python

`twat-mp` is a Python library designed to simplify parallel processing. It leverages the power of the [Pathos](https://pathos.readthedocs.io/en/latest/) library for robust synchronous parallel operations and offers experimental support for asynchronous parallelism using [aiomultiprocess](https://github.com/omnilib/aiomultiprocess). Whether you're dealing with CPU-bound computations or I/O-bound tasks, `twat-mp` provides convenient tools to help you write efficient, parallelized Python code.

This project is part of the [**twat**](https://pypi.org/project/twat/) collection of Python utilities.

## Who is it For?

`twat-mp` is for Python developers who want to:
- Speed up their applications by running tasks in parallel.
- Utilize multiple CPU cores effectively for computationally intensive work.
- Improve responsiveness of applications performing many I/O operations (e.g., network requests, file operations).
- Write cleaner and more manageable parallel code using context managers and decorators.

## Why is it Useful?

- **Simplified Parallelism:** Abstracts away much of the boilerplate associated with Python's native multiprocessing.
- **Performance Gains:** Enables significant speedups for suitable tasks by distributing work across multiple processes or threads.
- **CPU and I/O Optimization:** Offers distinct tools (`ProcessPool` for CPU-bound, `ThreadPool` for I/O-bound) to best match your workload.
- **Resource Management:** Automatic and reliable cleanup of parallel resources using context managers.
- **Enhanced Error Handling:** Provides clearer error messages from worker processes, making debugging easier.
- **Flexible Configuration:** Allows customization of worker counts, with sensible defaults based on system CPU cores.
- **Modern Python:** Built with type hints and modern Python features.

## Features

- **Synchronous Parallel Processing (Core):**
    - `ProcessPool`: Context manager for CPU-intensive tasks, utilizing multiple processes.
    - `ThreadPool`: Context manager for I/O-bound tasks, utilizing multiple threads.
    - Decorators for common parallel mapping operations:
        - `@pmap`: Standard parallel map (eager evaluation).
        - `@imap`: Lazy parallel map, returning an iterator (memory-efficient).
        - `@amap`: Asynchronous-style map that collects results (uses synchronous Pathos pools).
- **Experimental Asynchronous Support (via `aiomultiprocess`):**
    - `AsyncMultiPool`: Context manager for combining `async/await` with multiprocessing.
    - `@apmap`: Decorator for applying `async` functions in parallel.
- **Automatic CPU Core Detection:** Optimizes default pool sizes.
- **Debug Mode:** Provides detailed logging for troubleshooting.
- **Customizable Worker Count:** Flexibly configure the number of parallel workers.
- **Enhanced Exception Propagation:** Clearer context for errors occurring in worker processes/threads.

## Installation

You can install `twat-mp` using pip:

**Core Installation (Synchronous Features):**
```bash
pip install twat-mp
```

**With Experimental Async Support:**
To include the experimental asynchronous features (which require `aiomultiprocess`), install the `aio` extra:
```bash
pip install 'twat-mp[aio]'
```

**With All Extras and Development Tools:**
```bash
pip install 'twat-mp[all,dev]'
```

## Basic Usage (Programmatic)

`twat-mp` is a library and is used programmatically within your Python scripts.

### Synchronous Parallelism

#### Using `ProcessPool` for CPU-Bound Tasks

Ideal for tasks that perform heavy computations.

```python
from twat_mp import ProcessPool

def calculate_square(x):
    # Simulate a CPU-intensive calculation
    # In a real scenario, this would be actual computation
    result = 0
    for _ in range(x * 10000): # Ensure this is not too small to see effect
        result +=1
    return x * x

if __name__ == "__main__":
    with ProcessPool() as pool:
        numbers = range(10)
        results = pool.map(calculate_square, numbers)
        print(f"Squares: {list(results)}")
        # Expected (order may vary if not collected into a list immediately for some pool methods):
        # Squares: [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
```

#### Using `ThreadPool` for I/O-Bound Tasks

Suitable for tasks that spend time waiting for external operations like network requests or file I/O.

```python
from twat_mp import ThreadPool
import time
import requests # Make sure to install: pip install requests

def fetch_url_status(url):
    try:
        response = requests.get(url, timeout=5)
        return url, response.status_code
    except requests.RequestException as e:
        return url, str(e)

if __name__ == "__main__":
    urls = [
        "https://www.python.org",
        "https://www.github.com",
        "https://nonexistent.example.com" # Example of a failing URL
    ]
    with ThreadPool(nodes=len(urls)) as pool: # Using more threads for I/O
        results = pool.map(fetch_url_status, urls)
        for url, status in results:
            print(f"Status for {url}: {status}")
```

#### Using Synchronous Decorators

Decorators provide a concise way to parallelize functions.

```python
from twat_mp import pmap, imap, amap
import time

# @pmap: Eager parallel map
@pmap
def process_data_pmap(item):
    # print(f"pmap processing {item}")
    time.sleep(0.01) # Simulate work
    return item * 2

# @imap: Lazy parallel map (results as an iterator)
@imap
def process_data_imap(item):
    # print(f"imap processing {item}")
    time.sleep(0.01) # Simulate work
    return item * 3

# @amap: Asynchronous-style map (collects all results)
@amap
def process_data_amap(item):
    # print(f"amap processing {item}")
    time.sleep(0.01) # Simulate work
    return item * 4

if __name__ == "__main__":
    data = range(5)

    print("pmap results:", list(process_data_pmap(data)))
    # Expected: pmap results: [0, 2, 4, 6, 8]

    print("imap results:")
    for res_imap in process_data_imap(data):
        print(res_imap, end=" ") # 0 3 6 9 12
    print()

    print("amap results:", list(process_data_amap(data)))
    # Expected: amap results: [0, 4, 8, 12, 16]
```

### Experimental Asynchronous Parallelism

**Note:** These features are experimental and require `aiomultiprocess` (`pip install 'twat-mp[aio]'`). Their API and behavior might change in future releases.

#### Using `AsyncMultiPool`

Combines `async/await` with multiprocessing.

```python
import asyncio
from twat_mp import AsyncMultiPool # Requires 'aio' extra

async def async_work(x):
    await asyncio.sleep(0.1)  # Simulate async I/O or CPU work in an async context
    return x * 2

async def main_async_pool():
    # Ensure AsyncMultiPool is imported if 'aio' extra is installed
    # and you intend to use these experimental features.
    # from twat_mp import AsyncMultiPool

    async with AsyncMultiPool() as pool: # Experimental
        results = await pool.map(async_work, range(5))
        print(f"AsyncMultiPool results: {results}")
        # Expected: AsyncMultiPool results: [0, 2, 4, 6, 8]

if __name__ == "__main__":
    # To run this example, ensure 'aio' extra is installed.
    # You might need to check if AsyncMultiPool is available due to its optional dependency.
    try:
        from twat_mp import AsyncMultiPool
        asyncio.run(main_async_pool())
    except ImportError:
        print("Async features not available. Install with 'pip install \"twat-mp[aio]\"'")
    except RuntimeError as e:
        print(f"Async example runtime error: {e}") # Handles test hangs etc.

```

#### Using `@apmap` Decorator (Experimental)

```python
import asyncio
from twat_mp import apmap # Requires 'aio' extra

@apmap # Experimental
async def double_async_apmap(x):
    await asyncio.sleep(0.1)  # Simulate async work
    return x * 2

async def main_apmap_example():
    results = await double_async_apmap(range(5))
    print(f"apmap decorated results: {results}")
    # Expected: apmap decorated results: [0, 2, 4, 6, 8]

if __name__ == "__main__":
    # To run this example, ensure 'aio' extra is installed.
    try:
        from twat_mp import apmap
        asyncio.run(main_apmap_example())
    except ImportError:
        print("Async features not available. Install with 'pip install \"twat-mp[aio]\"'")
    except RuntimeError as e:
        print(f"Async example runtime error: {e}")
```

## Real-World Examples (Conceptual)

### Image Processing (CPU-Bound)
```python
# Conceptual example for parallel image resizing
from twat_mp import ProcessPool
# from PIL import Image # Requires: pip install Pillow
import os

def resize_image(image_path):
    # Placeholder for actual image processing
    # print(f"Resizing {image_path}...")
    # with Image.open(image_path) as img:
    #     resized_img = img.resize((img.width // 2, img.height // 2))
    #     # save resized_img
    time.sleep(0.1) # Simulate work
    return f"Resized {os.path.basename(image_path)}"

if __name__ == "__main__":
    # Create dummy image files for the example
    # os.makedirs("dummy_images", exist_ok=True)
    # image_files = []
    # for i in range(5):
    #     fp = f"dummy_images/image_{i}.png"
    #     # with open(fp, "w") as f: f.write("dummy") # Create placeholder
    #     image_files.append(fp)

    # Assuming image_files is a list of paths to image files
    image_files = [f"image_{i}.png" for i in range(5)] # Dummy list

    if image_files:
        with ProcessPool() as pool:
            results = pool.map(resize_image, image_files)
            for r in results:
                print(r)
    else:
        print("No image files to process for example.")
```

### Web Scraping (I/O-Bound)
```python
# Conceptual example for parallel web scraping
from twat_mp import ThreadPool
import requests
# from bs4 import BeautifulSoup # Requires: pip install beautifulsoup4

def fetch_page_title(url):
    try:
        # print(f"Fetching {url}...")
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        # soup = BeautifulSoup(response.text, 'html.parser')
        # title = soup.title.string if soup.title else "No title"
        time.sleep(0.1) # Simulate network latency and parsing
        return f"Title for {url}: Fetched (simulated)"
    except requests.RequestException as e:
        return f"Error fetching {url}: {e}"

if __name__ == "__main__":
    urls_to_scrape = [
        "https://www.python.org",
        "https://www.github.com",
        "https://www.djangoproject.com",
    ]
    with ThreadPool(nodes=len(urls_to_scrape)) as pool:
        results = pool.map(fetch_page_title, urls_to_scrape)
        for r in results:
            print(r)
```

---

## Technical Details

### How the Code Works

#### Synchronous Components (`src/twat_mp/mp.py`)

The synchronous part of `twat-mp` is built around the Pathos library.

- **`MultiPool`**: This is the base context manager class.
    - It handles the creation and cleanup of Pathos pools (`PathosProcessPool` or `PathosThreadPool`).
    - If the number of `nodes` (workers) isn't specified, it defaults to the system's CPU count using `pathos.helpers.mp.cpu_count()`.
    - Upon entering the context (`__enter__`), it instantiates the specified Pathos pool.
    - Crucially, it patches the pool's `map` method to use `_worker_wrapper`. This ensures that any exceptions from worker functions are caught and wrapped in a `WorkerError`.
    - On exiting (`__exit__`), it ensures the pool is properly closed, joined, and cleared, handling `KeyboardInterrupt` for quicker termination.

- **`ProcessPool` & `ThreadPool`**: These are subclasses of `MultiPool` that default to using `PathosProcessPool` and `PathosThreadPool` respectively. They are the primary context managers for users.

- **`_worker_wrapper(func, item, worker_id)`**:
    - This internal function wraps the user's target function (`func`) that is executed in a worker.
    - If `func(item)` executes successfully, its result is returned.
    - If `func(item)` raises an exception, `_worker_wrapper` catches it, logs the error and traceback (if debug mode is on), and then re-raises it as a `WorkerError`. This custom exception includes the original exception, the input `item` that caused the failure, an optional `worker_id` (typically the item's index), and the traceback string.

- **`WorkerError`**:
    - A custom exception class inheriting from `Exception`.
    - It's designed to provide more context about errors occurring in worker processes/threads, bundling the original exception, the problematic input, and traceback.

- **`mmap(how, get_result=False, debug=None)`**: This is a decorator factory.
    - It's not directly used by end-users but is the engine behind `@pmap`, `@imap`, and `@amap`.
    - The `how` argument specifies the Pathos mapping method to use:
        - `'map'`: Standard eager evaluation (used by `@pmap`).
        - `'imap'`: Lazy evaluation, returns an iterator (used by `@imap`).
        - `'amap'`: Asynchronous-style map; Pathos's `amap` returns a future-like object.
    - The `get_result=True` parameter (used by `@amap`) means the decorator will automatically call `.get()` on the result of Pathos's `amap` to retrieve the computed values.
    - The factory returns a decorator, which in turn wraps the user's function. When the decorated function is called with an iterable, it internally creates a `MultiPool` (defaulting to `ProcessPool`), gets the specified mapping method from the pool, and applies it to the user's function and iterable.
    - It handles `WorkerError` propagation: if a `WorkerError` is caught, it attempts to re-raise the `original_exception` for a more natural error flow for the user.

- **`set_debug_mode(enabled: bool)`**:
    - A global function to enable or disable `DEBUG_MODE`.
    - When enabled, it configures logging to `DEBUG` level, providing detailed output about pool creation, task execution, and cleanup.

#### Experimental Asynchronous Components (`src/twat_mp/async_mp.py`)

These components rely on the `aiomultiprocess` library and are marked as experimental.

- **`_check_aiomultiprocess()`**: A utility function that raises an `ImportError` if `aiomultiprocess` is not installed, guiding the user to install it via `pip install 'twat-mp[aio]'`.

- **`AsyncMultiPool`**: An asynchronous context manager.
    - On `__aenter__`, it creates an `aiomultiprocess.Pool` instance. Users can specify the number of `processes`, an `initializer` function for workers, and `initargs`.
    - It provides `async` methods:
        - `map(func, iterable)`: Applies an `async` function `func` to each item in `iterable` in parallel.
        - `starmap(func, iterable)`: Similar to `map`, but unpacks argument tuples from `iterable`.
        - `imap(func, iterable)`: Returns an async iterator that yields results as they complete.
    - On `__aexit__`, it handles the shutdown of the `aiomultiprocess.Pool` gracefully (close, join) with a fallback to terminate if necessary. It also includes robust error handling during cleanup.

- **`@apmap` Decorator**:
    - An `async` decorator for `async` functions.
    - When the decorated `async` function is called with an iterable, `@apmap` internally creates an `AsyncMultiPool` and uses its `map` method to execute the function calls in parallel.
    - It simplifies the pattern of setting up and tearing down an `AsyncMultiPool` for a single parallel map operation.

#### Error Handling Strategy

- **Synchronous:** Worker exceptions are caught by `_worker_wrapper` and re-raised as `WorkerError`. The `mmap` decorator factory then catches `WorkerError` and typically re-raises the `original_exception` contained within it. This makes the error handling feel more direct to the user.
- **Asynchronous (Experimental):** Errors within `aiomultiprocess` tasks are generally propagated by `aiomultiprocess` itself. `AsyncMultiPool` and `@apmap` wrap calls to `aiomultiprocess` methods and may raise `RuntimeError` for issues during pool operations or if `aiomultiprocess` itself raises an error that isn't more specific.

#### Resource Management

- The primary mechanism for resource management is the use of context managers:
    - `with ProcessPool() as pool:` / `with ThreadPool() as pool:`
    - `async with AsyncMultiPool() as pool:` (Experimental)
- The `__exit__` and `__aexit__` methods of these context managers are responsible for ensuring that underlying pools (Pathos or aiomultiprocess) are properly closed, worker processes/threads are joined, and resources are released. This happens automatically, even if errors occur within the `with` block.

### Coding and Contribution Rules

We encourage contributions to `twat-mp`! Please follow these guidelines:

#### Conventions

- **Formatting:** Code is formatted using [Ruff](https://github.com/astral-sh/ruff) (which includes Black-compatible formatting). Key settings (from `pyproject.toml`):
    - `line-length = 88`
    - `quote-style = "double"`
    - `indent-style = "space"`
- **Linting:** Ruff is also used for linting, with an extended set of rules (`I` for isort, `N` for pep8-naming, `B` for flake8-bugbear, `RUF` for Ruff-specific rules). See `pyproject.toml` for specific ignored rules.
- **Typing:** The project uses type hints and is checked with [MyPy](http://mypy-lang.org/). Stricter MyPy options are enabled (e.g., `disallow_untyped_defs`, `no_implicit_optional`).

#### Testing

- Tests are written using [Pytest](https://docs.pytest.org/).
- **Running Tests:**
    - Core synchronous tests: `hatch run test:test` (runs tests in parallel, ignores async tests).
    - To run specific tests or with coverage: `hatch run test:test-cov`.
    - Asynchronous tests (require `[aio]` extra) are typically in `tests/test_async_mp.py` and can be run specifically if needed, e.g., `pytest tests/test_async_mp.py`. Project configuration aims to skip these by default if `aiomultiprocess` is not available or if explicitly excluded.
- **Benchmarks:** Performance benchmarks use `pytest-benchmark`. Run with `hatch run test:bench`.
- New features should include corresponding tests. Bug fixes should ideally include a test that reproduces the bug.

#### Dependencies

- **Core:** `pathos` is a core dependency.
- **Optional:** `aiomultiprocess` is an optional dependency, required for the experimental async features. It's managed via the `[aio]` extra in `pyproject.toml`.
- Development dependencies (linters, testing tools) are listed under `[project.optional-dependencies]` (e.g., `test`, `dev`).

#### Versioning

- Versioning is managed by `hatch-vcs`, which derives the project version from Git tags.

#### Contribution Process

1. **Fork the repository** on GitHub.
2. **Create a new branch** for your feature or bug fix: `git checkout -b feature/your-feature-name` or `bugfix/issue-description`.
3. **Make your changes.** Ensure you add tests and update documentation if necessary.
4. **Run linters and tests** locally to ensure everything passes:
   ```bash
   hatch run lint:all
   hatch run test:test
   hatch run test:test-cov
   ```
5. **Commit your changes** with clear and descriptive commit messages.
6. **Push your branch** to your fork: `git push origin feature/your-feature-name`.
7. **Open a Pull Request (PR)** against the `main` branch of the `twardoch/twat-mp` repository.
8. Clearly describe your changes in the PR. Link to any relevant issues.

#### Project Structure

- `src/twat_mp/`: Main source code for the library.
    - `mp.py`: Synchronous multiprocessing components.
    - `async_mp.py`: Experimental asynchronous multiprocessing components.
- `tests/`: Pytest tests.
- `docs/`: Additional documentation (like `architecture.md`).
- `pyproject.toml`: Project metadata, dependencies, and tool configurations.
- `README.md`: This file.

## API Reference

For detailed API documentation of all classes, methods, and functions, please see the [API Reference (API_REFERENCE.md)](API_REFERENCE.md).

## License

`twat-mp` is licensed under the [MIT License](LICENSE).
