# lazy_import.py: last updated 02:46 AM on May 30, 2025

**File Path:** `/home/kylerose1946/claudes_toolbox/claudes_toolbox/utils/common_/lazy_import.py`

## Table of Contents

### Functions

- [`lazy_import`](#lazy_import)

## Functions

## `lazy_import`

```python
def lazy_import(name)
```

Import a module lazily. The module is not loaded until it is accessed.
Taken directly from: https://docs.python.org/3/library/importlib.html#implementing-lazy-imports

name: str
    The name of the module to import.

**Returns:**

- `types.ModuleType`: ModuleType
        The module object.

**Examples:**

```python
lazy_typing = lazy_import("typing")
    #lazy_typing is a real module object,
    #but it is not loaded in memory yet.
    lazy_typing.TYPE_CHECKING
```
