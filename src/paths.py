# src/paths.py
import os
from pathlib import Path

# Root folder of the project (one level above src)
ROOT_FOLDER = Path(__file__).parents[1]

def get_folder(*args):
    """
    Returns absolute path to a folder relative to the project root.

    Example:
        get_folder("docs") -> C:/Users/.../sxs/docs
        get_folder("outputs", "plots") -> C:/Users/.../sxs/outputs/plots
    """
    return os.path.join(ROOT_FOLDER, *args)

def get_file(*args):
    """
    Returns absolute path to a file relative to the project root.

    Example:
        get_file("docs", "sankey_nodes.xlsx")
    """
    return os.path.join(ROOT_FOLDER, *args)