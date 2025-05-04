from typing import Any, Dict

def deep_merge_two_dictionaries(base_dict: Dict[str, Any], overlay_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merge two dictionaries, with values from overlay_dict taking precedence.
    
    Args:
        base_dict: The base dictionary to merge into
        overlay_dict: The dictionary whose values take precedence
        
    Returns:
        A new merged dictionary
    """
    result = base_dict.copy()
    
    for key, value in overlay_dict.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_two_dictionaries(result[key], value)
        else:
            result[key] = value
            
    return result