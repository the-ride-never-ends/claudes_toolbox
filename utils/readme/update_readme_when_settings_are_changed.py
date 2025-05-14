from functools import wraps
from pathlib import Path
import re
import shutil
from typing import Any, Callable, Pattern


from configs import configs
from logger import logger


def _format_config_json(pattern: Pattern[str], new_section: str) -> str:
    """Format the config jsons in the new section."""
    if "config\n```json" in pattern:
        for old, new in [("  }", "}"),('    "command"', '  "command"'),('    "args"', '  "args"')]:
            new_section = new_section.replace(old, new)
    return new_section


def _update(pattern: Pattern[str], file_content: str, readme_content: str, formatting: str = "") -> str:
    """Update the README content with the new settings."""

    # Extract the old content from the README
    match = re.search(pattern, readme_content, re.DOTALL)

    if match:
        old_section = match.group(1)

        # Extract the new content from the file
        new_section = "\n".join(
            [f"{formatting}{line.strip()}" for line in file_content.strip().split('\n') if line.strip()]
        ).strip()

        # Format the config jsons
        new_section = _format_config_json(pattern, new_section)

        # If something changed, replace the original content
        if new_section != old_section:
            readme_content = readme_content.replace(old_section, new_section)

    else:
        logger.warning(f"Pattern '{pattern}' not found in README content. Skipping...")

    return readme_content

def file_operation_error(func: Callable = None, *, return_this_on_error: Any = None, raise_: bool = False) -> Callable:
    """Decorator factory to handle file operation errors."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            errored = None
            errors = (PermissionError, IsADirectoryError, FileNotFoundError, OSError, Exception)
            try:
                return func(*args, **kwargs)
            except errors as e:
                errored = e
                logger.error(f"{type(e).__name__}: {e}")
            finally:
                if errored is not None:
                    if raise_:
                        raise errored
                    if return_this_on_error is not None:
                        return return_this_on_error
        return wrapper
    if func is None:
        return decorator
    return decorator(func)

@file_operation_error(return_this_on_error="")
def _load_file(file_path: Path) -> str:
    """Load the content of a file."""
    with open(file_path, "r") as file:
        return file.read()

@file_operation_error
def _create_backup(file_path: Path) -> None:
    """Create a backup of the file."""
    shutil.copy(file_path, file_path.with_suffix('.md.bak'))
    logger.info(f"Created backup of '{file_path}'.")

@file_operation_error
def _restore_backup(file_path: Path) -> None:
    """Restore the backup of the file."""
    shutil.move(file_path.with_suffix('.md.bak'), file_path)
    logger.info(f"Restored backup of '{file_path}'.")

@file_operation_error
def _remove_backup(file_path: Path) -> None:
    file_path.with_suffix('.md.bak').unlink()
    logger.debug(f"Removed backup of '{file_path}'.")

def backup_markdown_file(func: Callable) -> Callable:
    """Decorator to create a backup of a markdown file before writing."""
    @wraps(func)
    def wrapper(file_path: Path, content: str):
        errored = False
        # Create a backup of the original file
        _create_backup(file_path)
        try:
            return func(file_path, content)
        except Exception as e:
            errored = True
            logger.error(f"Error while writing to '{file_path}': {e}")
            _restore_backup(file_path)
        finally:
            if not errored:
                # Remove the backup if the operation was successful
                _remove_backup(file_path)
    return wrapper


@backup_markdown_file
@file_operation_error
def _write_file(file_path: Path, content: str) -> None:
    """Write the content to a file."""
    with open(file_path, "w") as file:
        file.write(content)
        logger.info(f"Wrote content to '{file_path}'.")


def update_readme_when_settings_are_changed() -> None:
    """Update the README file with new settings if they have changed."""

    if configs.update_readme_when_settings_are_changed is True:
        logger.info("Updating README file with new settings...")
        # Load the README file.
        readme_content = _load_file(configs.ROOT_DIR / "README.md")
        if not readme_content:
            return

        paths = [
            ('requirements.txt', r"## Requirements\n(.*?)\n## Installation", "- ",),
            ('configs.yaml.example', r"```yaml\n(.*?)\n```", "  ",), 
            ('run_linux.config', r"```run_linux.config\n```json\n(.*?)\n```", "  ",),
            ('run_windows.config', r"```run_windows.config\n```json\n(.*?)\n```", "  ",),
            ('run_wsl.config', r"```run_wsl.config\n```json\n(.*?)\n```", "  ",),
        ]

        for path, pattern, formatting in paths:
            path = configs.ROOT_DIR / path
            # Check if the file exists
            if not path.exists():
                logger.warning(f"The file '{path}' does not exist. Skipping...")
                continue

            # Load the file, skipping failed loads and empty files.
            file_content = _load_file(path)
            if not file_content:
                continue

            # Update the README content.
            readme_content = _update(pattern, file_content, readme_content, formatting=formatting)

        # Write the updated content back to the README file.
        _write_file(configs.ROOT_DIR / "README.md", readme_content)

if __name__ == "__main__":
    update_readme_when_settings_are_changed()
