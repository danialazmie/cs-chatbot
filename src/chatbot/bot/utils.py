import yaml
import os

def load_credentials(path: str) -> list:
    """
    Loads credentials from a YAML file and sets them as environment variables.

    Args:
        path (str): The file path to the YAML file containing credentials.

    Returns:
        list: A list of the credential keys that were set as environment variables.
    """
    
    with open(path, 'r') as file:
        credentials = yaml.safe_load(file)

    for key, value in credentials.items():
        os.environ[key] = value

    return list(credentials.keys())