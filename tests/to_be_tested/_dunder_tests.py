# import asyncio
# from pathlib import Path
# from typing import Any, Callable, Coroutine
# from functools import cached_property
# import logging

# class Debugger:
#     pass

# class TryExcept:

#     def __init__(self, *args):
#         self._try_except_dicts = []
#         for arg in args:
#             try_except_dict = {
#                 ""
#                 "exception": Exception,
#                 "msg": "An {exception_type} exception occurred: {e}",
#                 "raise_": True,
#                 "default_return": "NO_DEFAULT", # Since None can also be a desired return value.
#                 "logger": print,
#                 "async_": False,
#                 "raise_from": None, # Exception
#                 "num_retries": 0,
#             }
#             match arg:
#                 case Exception():
#                     try_except_dict["exception"] = arg
#                 case str():
#                     try_except_dict["msg"] = arg
#                 case dict():
#                     try_except_dict.update(arg)
#                 case logging.Logger():
#                     # Replace the prints with logger calls
#                     try_except_dict["logger"] = arg
#                 case Callable() | Coroutine():
#                     pass
#                 case hasattr(arg, "__init__"): # Class instance
#                     pass
#                 case _:
#                     raise TypeError(
#                         f"Invalid argument type: {type(arg).__name__}."
#                         "Expected an exception, str, dict, logger, function, or coroutine."
#                     )
#             self._try_except_dicts.append(try_except_dict)

#     def try_except(self) -> Callable:
#         for dict in self._try_except_dicts:
#             for key, value in dict.items():
#                 if key == "exception":
#                     exception = value
#                 elif key == "msg":
#                     msg = value
#                 elif key == "raise_":
#                     raise_ = value
#                 elif key == "default_return":
#                     default_return = value
#                 elif key == "logger":
#                     logger = value
#                 elif key == "async_":
#                     async_ = value

#     def exception_chain(self, *exceptions, **kwargs): # Shamelessly stolen from pathlib
#         """Construct a new try_except chain object from any number of try_except-like objects.
#         Subclasses may override this method to customize how new try_except objects
#         are created from methods like `retry()`.
#         """
#         return type(self)(*exceptions, **kwargs)

#     def retry(self, *exception):
#         """Catch exceptions in the chain."""
#         try:
#             return self.exception_chain(exception, {"raise_": False})
#         except KeyError as e:
#             raise NotImplemented

#     def catch(self, *exception):
#         """Catch exceptions in the chain."""
#         try:
#             return self.exception_chain(exception, {"raise_": False})
#         except KeyError as e:
#             raise NotImplemented
    
#     def __rand__(self, exception):
#         try:
#             return self.exception_chain(exception)
#         except KeyError:
#             raise NotImplemented

#     def __lshift__(self, exception):
#         """Handle exceptions in the chain."""
#         try:
#             return self.exception_chain(exception)
#         except KeyError:
#             raise NotImplemented

#     def __rshift__(self, exception):
#         try:
#             return self.exception_chain(exception)
#         except KeyError:
#             raise NotImplemented

#     @cached_property
#     def result(self):
#         pass

# # Global configuration manager instance
# from pathlib import Path
# ROOT_DIR = Path(__file__).resolve().parent.parent
# CONFIG_PATH = ROOT_DIR / 'configs.yaml'

# chain = TryExcept(open((CONFIG_PATH.resolve())))

# def except_(e: Exception):
#     return TryExcept(e)

# def catch(e: Exception):
#     return TryExcept(e, {"raise_": False})

# def on_error_raise(e: Exception):
#     return TryExcept(e, {"raise_": True})

# def retry(e: Exception, num_retries: int):
#     return TryExcept(e, {"num_retries": num_retries})

# chain >> (
#     yaml.YAMLError, {
#         "raise_": False, 
#         "msg": "Error loading configuration file: {e}. Using default configuration."
#     }
# ) >> {
#     FileNotFoundError: "Configuration file not found at {CONFIG_PATH}. Using default configuration.",
#     ValidationError: "Error validating configuration file: {e}. Using default configuration.",
#     "raise": False,
# } >> print("love") & catch(ValidationError) & on_error_raise(Exception
# ) >> retry(ValidationError, 3) >> open(CONFIG_PATH.resolve(), 'r') >> print("yahoo") >> catch(Exception) >> range()



# chain.try_except()
# chain.catch()
