import os
from pathlib import Path
import re
from typing import Dict, Any



def parse_env_file(file_path: Path) -> Dict[str, Any]:
    """
    Parse a .env file and return its contents as a dictionary.
    
    Args:
        file_path: Path to the .env file
        
    Returns:
        Dictionary containing environment variables from the file
    """
    env_vars = {}
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Parse key-value pairs
            match = re.match(r'^([A-Za-z0-9_]+)=(.*)$', line)
            if match:
                key, value = match.groups()
                # Remove quotes if present
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                env_vars[key] = value
                
    return env_vars


def merge_envs(root_dir: str, output_path: str = None, env_filename: str = ".env") -> Dict[str, Any]:
    """
    Walk through a directory to find all .env files and merge them,
    with values from deeper directories taking precedence.

    Args:
        root_dir: The root directory to start searching from
        output_path: Optional path to write the merged environment variables to
        env_filename: The name of the environment files to merge (default: ".env")

    Returns:
        The merged environment variables dictionary
    """
    root_dir = Path(root_dir).resolve()

    # Start with empty environment variables
    merged_env_vars = {}

    # Keep track of directories by depth to ensure proper precedence
    env_files_by_depth = {}

    # Walk through all directories
    for dirpath, _, filenames in os.walk(root_dir):
        path = Path(dirpath)
        if env_filename in filenames:
            # Calculate depth from root
            depth = len(path.relative_to(root_dir).parts)
            env_path = path / env_filename

            try:
                env_data = parse_env_file(env_path)
                if env_data:  # Skip empty env files
                    env_files_by_depth[depth] = env_files_by_depth.get(depth, []) + [(env_path, env_data)]
            except Exception as e:
                print(f"Error reading {env_path}: {e}")

    # Merge env files in order of depth (shallow to deep)
    for depth in sorted(env_files_by_depth.keys()):
        for env_path, env_data in env_files_by_depth[depth]:
            # For env files, we just need to update values, not deep merge
            merged_env_vars.update(env_data)
            print(f"Merged environment variables from {env_path}")

    # Write merged env vars to output file if specified
    if output_path:
        output_path = output_path if isinstance(output_path, Path) else Path(output_path)
        with open(output_path, 'w') as f:
            for key, value in sorted(merged_env_vars.items()):
                # Add quotes if the value contains spaces
                if ' ' in str(value):
                    f.write(f'{key}="{value}"\n')
                else:
                    f.write(f'{key}={value}\n')
        print(f"Wrote merged environment variables to {output_path}")

    return merged_env_vars

