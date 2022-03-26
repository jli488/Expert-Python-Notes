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

