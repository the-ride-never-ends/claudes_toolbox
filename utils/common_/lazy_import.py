import importlib.util
import sys
import types

def lazy_import(name: str) -> types.ModuleType:
    """
    Import a module lazily. The module is not loaded until it is accessed.
    Taken directly from: https://docs.python.org/3/library/importlib.html#implementing-lazy-imports

    name: str
        The name of the module to import.

    Returns:
        ModuleType
            The module object.

    Example:
        lazy_typing = lazy_import("typing")
        #lazy_typing is a real module object,
        #but it is not loaded in memory yet.
        lazy_typing.TYPE_CHECKING

    """
    spec = importlib.util.find_spec(name)
    loader = importlib.util.LazyLoader(spec.loader)
    spec.loader = loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    loader.exec_module(module)
    return module
