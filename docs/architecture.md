# twat-mp Architecture

This document explains the architecture of the `twat-mp` package using simple diagrams.

## Component Overview

```
+---------------------------+
|       twat-mp Package     |
+---------------------------+
           |
           |
           v
+---------------------------+
|      Core Components      |
+---------------------------+
           |
           +----------------+----------------+
           |                |                |
           v                v                v
+------------------+ +---------------+ +---------------------+
|  Process-based   | |  Thread-based | |  Async-based        |
|  Parallelism     | |  Parallelism  | |  Parallelism        |
|  (Core MVP)      | |  (Core MVP)   | |  (Experimental)     |
+------------------+ +---------------+ +---------------------+
|                  | |               | |                     |
| - MultiPool      | | - ThreadPool  | | - AsyncMultiPool    |
| - ProcessPool    | |               | |   (Experimental)    |
| - pmap, imap,    | |               | | - apmap             |
|   amap decorators| |               | |   (Experimental)    |
+------------------+ +---------------+ +---------------------+
           |                |                |
           |                |                |
           v                v                v
+---------------------------+---------------------------+
|                 Underlying Libraries                  |
+---------------------------+---------------------------+
|                                                       |
|  - pathos (for ProcessPool, ThreadPool - Core MVP)    |
|  - aiomultiprocess (for AsyncMultiPool - Experimental)|
|                                                       |
+-------------------------------------------------------+
```

## Execution Flow

### Process/Thread Pool Execution Flow (Core MVP)

```
+-------------+     +-------------+     +----------------+
| User Code   |     | Pool        |     | Worker         |
| with        |---->| Creation    |---->| Processes      |
| ProcessPool |     | (Context)   |     | or Threads     |
+-------------+     +-------------+     +----------------+
      |                   |                    |
      |                   |                    |
      v                   v                    v
+-------------+     +-------------+     +----------------+
| Function    |     | Task        |     | Parallel       |
| to Execute  |---->| Distribution|---->| Execution      |
+-------------+     +-------------+     +----------------+
                          |                    |
                          |                    |
                          v                    v
                    +-------------+     +----------------+
                    | Result      |<----| Results        |
                    | Collection  |     | from Workers   |
                    +-------------+     +----------------+
                          |
                          |
                          v
                    +-------------+
                    | Return      |
                    | to User     |
                    +-------------+
```

### Async Pool Execution Flow (Experimental Feature)

```
+-------------+     +-------------+     +----------------+
| Async       |     | AsyncMulti  |     | Worker         |
| User Code   |---->| Pool        |---->| Processes      |
+-------------+     | Creation    |     |                |
      |             +-------------+     +----------------+
      |                   |                    |
      v                   v                    v
+-------------+     +-------------+     +----------------+
| Async       |     | Task        |     | Parallel       |
| Function    |---->| Distribution|---->| Execution of   |
+-------------+     +-------------+     | Async Functions|
                          |             +----------------+
                          |                    |
                          v                    v
                    +-------------+     +----------------+
                    | Await       |<----| Async Results  |
                    | Results     |     | from Workers   |
                    +-------------+     +----------------+
                          |
                          |
                          v
                    +-------------+
                    | Return      |
                    | to User     |
                    +-------------+
```

## Decorator Pattern

```
+-------------+     +-------------+     +----------------+
| Function    |     | Decorator   |     | Wrapped        |
| Definition  |---->| Application |---->| Function       |
| @pmap       |     | (mmap)      |     |                |
+-------------+     +-------------+     +----------------+
                          |                    |
                          |                    |
                          v                    v
                    +-------------+     +----------------+
                    | Function    |     | MultiPool      |
                    | Call with   |---->| Creation &     |
                    | Iterable    |     | Management     |
                    +-------------+     +----------------+
                                               |
                                               |
                                               v
                                        +----------------+
                                        | Parallel       |
                                        | Execution &    |
                                        | Result Return  |
                                        +----------------+
```

## Class Hierarchy

```
                  +-------------+
                  |  MultiPool  |
                  +-------------+
                        ^
                        |
          +-------------+-------------+
          |                           |
+-----------------+         +-----------------+
|  ProcessPool    |         |   ThreadPool    |
+-----------------+         +-----------------+


+------------------+
| AsyncMultiPool   |
| (Experimental)   |
+------------------+
```

## Decorator Relationships

```
                  +-------------+
                  |    mmap     |
                  | (factory)   |
                  +-------------+
                        |
                        v
          +-------------+-------------+-------------+
          |             |             |             |
+-----------------+  +------+  +------+  +-----------------+
|      pmap       |  | imap |  | amap |  |  apmap          |
| (eager eval)    |  | (lazy)|  |(async)|  |  (Experimental) |
+-----------------+  +------+  +------+  +-----------------+
```
