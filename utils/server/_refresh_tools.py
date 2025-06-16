# import threading
# _refresh_lock = threading.Lock()

# def refresh_tools(lock: threading.Lock = _refresh_lock, time_between_refreshes_in_seconds: int = 60) -> None:
#     """
#     Refresh the tools by reloading the tools module.

#     This function is designed to be run in a separate thread to avoid blocking the main thread.
#     It uses a lock to ensure that only one thread can refresh the tools at a time.
#     """
#     with _refresh_lock:
#         import importlib
#         import tools.functions as tools
#         importlib.reload(tools)
