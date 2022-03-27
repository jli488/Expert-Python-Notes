# Chapter-02: New Things in Python

## New features

### Assignment expressions

- Statements: Consecutive actions or instructions that your program executes

  - Value assignments
  - `if` clauses
  - `for` and `while` loops
  - Function and class definitions

- Expressions: Anything that can be put into an `if` clause

  - Literals
  - Values returned by operators (exclude in-place operators)
  - Comprehensions
  - Function calls and method calls are expressions too

- Python provides syntax features that were expression counterparts of their statements

  - Lambda expressions for anonymous functions as a counterpart for function definitions

    ```python
    lambda x: x ** 2
    ```

  - Type object instantiation as a counterpart for class definition

    ```python
    type("MyClass", (), {})
    ```

  - Various comprehensions as a counterpart for loops

    ```python
    squares_of_2 = [x**2 for x in range(10)]
    ```

  - Compound expressions as a counterpart for `if ... else` statements

    ```python
    "odd" if number % 2 else "even"
    ```

For many years, we haven't had access to syntax that would convey the semantics of assigning a value to a variable in the form of an expression, until the **walrus** operator `:=` in Python 3.8

```python
a = (c := 'odd' if 2 % 2 else 'even')
# c := 'odd' if 2 % 2 else 'even' is an expression, and c is assigned with 'even'
# The expression itself also evaluated to 'even'
```

This feature has two use cases:

- In the `if ... else` statement if the assignment is used directly in the branch

- Reusing the same data in multiple places in larger expressions, such as:

  ```python
  first_name = "John"
  last_name = "Doe"
  height = 168
  weight = 70
  user = {
      "first_name": first_name,
      "last_name": last_name,
      "display_name": f"{first_name} {last_name}",
      "height":  height,
      "weight": weight,
      "bmi": weight / (height / 100) ** 2,
  }
  
  # can be re-written as
  
  user = {
      "first_name": (first_name := "John"),
      "last_name": (last_name := "Doe"),
      "display_name": f"{first_name} {last_name}",
      "height": (height := 168),
      "weight": (weight := 70),
      "bmi": weight / (height / 100) ** 2,
  }
  ```

### Type-hinting generics

Type-hinting allow you to annotate variable, argument, and function return types with type definitions. These type annotations serve documentational purposes, but can also be used to validate your code using external tools, such as `mypy` or `pyright`

Example:

```python
from typing import Any
def get_ci(d: dict, key: str) -> Any:
    for k, v in d.items():
        if key.lower() == k.lower():
            return v
```

The above example works for one level check, i.e. if instead of providing a `dict` for the first argument, someone supplied a `list`, then most IDE can capture this miss typed argument, but what if you want to check the type of the key and value in the `dict`? This is where generic types can help:

```python
dict[KeyType, ValueType]
 
# and then:

def get_ci(d: dict[str, Any], key: str) -> Any: ...
```

### Positional-only parameters

Python3.8 added the option to define specific arguments as positional-only. Careful consideration as to which arguments should be passed as position-only and which as keyword-only serves to make the definition of functions more susceptible to future changes.

```python
def concatenate(first: str, second: str, /, *, delim: str):
    return delim.join([first, second])
```

- All arguments preceding the `/` mark are **positional-only** arguments
- All arguments following the `*` mark are **keyword-only** arguments

There can be only one valid function call for the above definition:

```python
concatenate("John", "Doe", delim=" ")
```

If one day we want to make the function definition accept an unlimited number of positional arguments. As there is only one way in which this function can be used, we can safely change the function to

```python
def concatenate(*items, delim: str):
    return delim.join(items)
```

### zoneinfo module

Starting from Python3.9, the standard library provides a `zoneinfo` module that is an interface to the time zone database either provided by your operating system or obtained as a first-party `tzdata` package from PyPI

`ZoneInfo` class can be used as a `tzinfo` parameter of the `datetime` object constructor, as in the following example (this will create a zone-aware datetime object)

```python
from datetime import datetime
from zoneinfo import ZoneInfo
dt = datetime(2020, 11, 28, tzinfo=ZoneInfo("Europe/Warsaw"))
```

You can obtain a full list of all the time zones available in your system using the `zoneinfo.available_timezones()` function

### graphlib module

`graphlib` is a module that provides utilities for working with graph-like data structures. A graph is a data structure consisting of nodes connected by edges. There are two main types of graphs:

- An **undirected graph** is a graph where every edge is undirected. So, if *A* and *B* are connected to edge *E*, you can traverse from *A* to *B* or *B* to *A* using the same edge *E*
- A **directed graph** is a graph where every edge is directed. So, if an edge *E* starts from *A* and connected to node *B*, then you can traverse from *A* to *B* using *E*, but cannot traverse from *B* to *A*

Moreover, graphs can be either **cyclic** or **acyclic**. A cyclic graph is a graph that has at least one cycle, an acyclic graph is a graph that does not have any cycles.

Specifically, Python3.9 provided `TopologicalSorter` utility to sort DAG based on reachability, the usage looks like:

```python
from graphlib import TopologicalSorter

# keys are origin nodes and values are sets of destination nodes
table_reference = {
    "customers": set(),
    "accounts": {"customers"},
    "products": set(),
    "orders": {"accounts", "customers"},
    "order_products": {"orders", "products"}
}

sorter = TopologicalSorter(table_reference)
print(list(sorter.static_order()))
# ['customers', 'products', 'accounts', 'orders', 'order_products']
```

`TopologicalSorter` doesn't check for the existence of cycles during initialization, although it will detect cycles during sorting. If a cycle is found, the `static_order()` method will raise a `graphlib.CycleError` exception.

## Not that new, but still shiny

