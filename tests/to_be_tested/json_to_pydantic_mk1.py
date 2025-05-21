import importlib.util
import json
import keyword
import re
from pathlib import Path
from typing import Any
import traceback


def _to_snake_case(name: str) -> str:
    """Convert camelCase or PascalCase to snake_case"""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def _structure_signature(data: dict) -> tuple:
    """Create a hashable structure signature for deduplication"""
    return tuple(sorted((key, type(value).__name__) for key, value in data.items()))

def _sanitize_field_name(name: str) -> str:
    """Sanitize field names to be valid Python identifiers"""
    name = re.sub(r'\W|^(?=\d)', '_', name)
    if keyword.iskeyword(name):
        name += "_"
    return name

def _build_model(
    data: dict[str, Any],
    class_name: str,
    model_registry: dict,
    structure_map: dict,
    allow_optional_fields: bool = False
) -> str:
    """
    Builds a Pydantic model definition dynamically based on the provided data structure.

    Args:
        data (dict[str, Any]): The input dictionary representing the structure of the data.
        class_name (str): The name of the Pydantic model class to be generated.
        model_registry (dict): A registry to store generated model definitions by class name.
        structure_map (dict): A mapping of structure signatures to class names to avoid duplication.
        allow_optional_fields (bool, optional): Whether to allow fields with `None` values to be marked as optional. Defaults to False.

    Returns:
        str: The generated Pydantic model definition as a string.
    """
    # Generate a unique structure key for deduplication
    structure_key = _structure_signature(data)
    if structure_key in structure_map:
        return structure_map[structure_key]

    # Map the structure key to the class name
    structure_map[structure_key] = class_name
    fields = []

    # Iterate through the dictionary to generate fields
    for key, value in data.items():
        safe_key = _sanitize_field_name(key)  # Sanitize the field name
        field_type = _infer_type(
            value, model_registry, structure_map, safe_key, allow_optional_fields
        )

        # Handle optional fields if allowed
        if allow_optional_fields and value is None:
            field_type = f"Optional[{field_type}]"

        # Generate alias code for the field
        aliases = [_to_snake_case(key)]
        if key.lower() != key:
            aliases.append(key.lower())
        alias_code = f" = Field(alias='{aliases[0]}')" if aliases else ""

        # Append the field definition
        fields.append(f"    {safe_key}: {field_type}{alias_code}")

    # Generate the model definition string, add it to the registry, and return the definition.
    model_def = f"class {class_name}(BaseModel):\n" + "\n".join(fields) if fields else f"class {class_name}(BaseModel):\n    pass"
    model_registry[class_name] = model_def
    return model_def

def _infer_type(
    value: Any,
    model_registry: dict,
    structure_map: dict,
    parent_key: str,
    allow_optional_fields: bool
) -> str:
    """
    Infers the Pydantic-compatible type of a given value and updates the model registry
    and structure map if necessary.

    Args:
        value (Any): The value whose type needs to be inferred. Can be a dict, list, or primitive type.
        model_registry (dict): A dictionary to store dynamically generated Pydantic models.
        structure_map (dict): A mapping of parent keys to their corresponding data structures.
        parent_key (str): The key associated with the current value, used for naming generated models.
        allow_optional_fields (bool): Whether to allow fields to be optional in the generated models.

    Returns:
        str: A string representing the inferred type, compatible with Pydantic type annotations.
    """
    # Match the type of the value to determine the appropriate Pydantic-compatible type
    match value:
        # If the value is a dictionary, treat it as a nested model
        case dict():
            class_name = f"{parent_key.capitalize()}"  # Generate a class name based on the parent key
            # Recursively build the nested model
            _build_model(value, class_name, model_registry, structure_map, allow_optional_fields)
            return class_name  # Return the class name for the nested model

        # If the value is a list, determine the type of its elements
        case list():
            if not value:  # If the list is empty, default to a generic list of Any
                return "List[Any]"
            inner_types = set()  # Collect the types of elements in the list
            for item in value:
                # Infer the type of each item in the list
                inner_type = _infer_type(item, model_registry, structure_map, parent_key, allow_optional_fields)
                inner_types.add(inner_type)
            # If the list contains multiple types, return a union of those types
            return f"List[{', '.join(sorted(inner_types))}]" if len(inner_types) > 1 else f"List[{inner_types.pop()}]"
        case str():
            return "str"
        case bool():
            return "bool"
        case int():
            return "int"
        case float():
            return "float"
        case _: # Default to Any if the type is not recognized.
            return "Any"

def json_to_pydantic(
    json_data: str | dict[str, Any],
    output_dir: str,
    model_name: str = "GeneratedModel",
    allow_optional_fields: bool = False
) -> str:
    """
    Turn JSON data into a Pydantic model or series of models.
    Any nested structures will be converted into their own models and placed as fields their parent models.
    NOTE: Only POSIX-style paths are supported at this time.

    Args:
        json_data (str | dict): JSON data as a JSON string, JSON dictionary, or path to a JSON file.
            
        output_dir (str): Directory to save the generated model file.
        model_name (str): Name of the generated model class. Defaults to "GeneratedModel".
        allow_optional_fields (bool): If True, allows models fields to be optional. Defaults to False.

    Returns:
        str: A success message that contains the path to the output file.

    Raises:
        FileNotFoundError: If the output directory does not exist.
        TypeError: If the input JSON is not a string, dictionary, or path to a JSON file.
        ValueError: 
            - If the input JSON is invalid.
            - If there is any error during model generation.
            - If importing the generated model fails.
            - If generated model fails to validate against the input JSON.
        IOError: If there is an error writing to the output file.
    """
    if not Path(output_dir).exists():
        raise FileNotFoundError(f"Output directory '{output_dir}' does not exist.")
    else:
        output_path = Path(output_dir) / f"{model_name}.py"

    if isinstance(json_data, str):
        try:
            if Path(json_data).is_file() and json_data.endswith(".json"):
                with open(json_data, "r") as f:
                    json_data = json.load(f)
            else:
                json_data = json.loads(json_data)
        except Exception as e:
            raise ValueError(f"Invalid JSON input: {e}") from e

    if not isinstance(json_data, dict):
        raise TypeError(
            "Input JSON must be a JSON string, JSON dictionary, "
            f"or a path to a json file, not '{type(json_data).__name__}'."
        )

    model_registry: dict = {}
    structure_map: dict = {}
    try:
        _build_model(json_data, model_name, model_registry, structure_map, allow_optional_fields)
    except Exception as e:
        traceback.print_exc()
        raise ValueError(f"Error generating Pydantic model: {e}") from e

    sorted_models = sorted(model_registry.items())
    model_code = "from pydantic import BaseModel, Field\nfrom typing import List, Any, Union, Optional\n\n" + "\n\n".join([v for _, v in sorted_models])
    try:
        with open(output_path.resolve(), "w") as file:
            file.write(model_code)
    except Exception as e:
        raise IOError(f"Error writing to output file {output_path}: {e}") from e
    
    # Import the generated model to check if it validates against the original JSON
    try:
        spec = importlib.util.spec_from_file_location(model_name, output_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        generated_model = getattr(module, model_name)
    except Exception as e:
        raise ValueError(f"Error importing generated model from '{output_path}': {e}") from e

    try:
        _ = generated_model(**json_data)
    except Exception as e:
        raise ValueError(f"Generated model failed to validate against input JSON: {e}") from e

    return f"Model(s) generated successfully and saved to '{output_path}'"
