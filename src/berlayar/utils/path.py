# berlayar/utils/path.py

import os

def get_absolute_path(relative_path):
    base_path = os.path.dirname(__file__)  # Get the directory of the current script
    absolute_path = os.path.join(base_path, relative_path)  # Construct the absolute path
    return os.path.abspath(absolute_path)  # Resolve any '..' components

def find_project_root(current_path, identifier):
    """
    Recursively searches for a directory containing the identifier starting from current_path and moving upwards.
    Returns the path to the directory if found, otherwise None.
    """
    if os.path.exists(os.path.join(current_path, identifier)):
        return current_path  # Identifier found, return current path
    parent_path = os.path.dirname(current_path)
    if parent_path == current_path:
        # Root of the filesystem reached without finding identifier
        return None
    return find_project_root(parent_path, identifier)  # Continue search in the parent directory

def get_project_root():
    """
    Finds the 'berlayar' project root based on a unique identifier.
    Adjust 'unique_identifier' as needed to match your project structure.
    """
    script_location = os.path.dirname(os.path.abspath(__file__))
    unique_identifier = '.env'  # Example identifier, change as needed
    project_root = find_project_root(script_location, unique_identifier)
    if project_root is None:
        raise Exception("Project root not found.")
    return project_root

def construct_path_from_root(relative_path):
    """
    Constructs an absolute path given a relative path from the project root.
    """
    project_root = get_project_root()
    return os.path.join(project_root, relative_path)
