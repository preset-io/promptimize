import os, sys
import importlib
import pkgutil
from pathlib import Path
from typing import List, Type, Any, Union


def is_instance_or_derivative(obj: Any, object_type: Type) -> bool:
    return isinstance(obj, object_type)


def discover_objects(path: str, object_type: Type) -> List[Any]:
    objects = []
    folder_path = Path(path).resolve()

    # Add the folder to the Python path to enable importing modules from it
    if folder_path not in sys.path:
        sys.path.insert(0, str(folder_path))

    # Iterate over all the modules in the folder
    for _, module_name, _ in pkgutil.iter_modules([str(folder_path)]):
        # Import the module
        module = importlib.import_module(module_name)

        # Iterate over the objects in the module
        for name, obj in module.__dict__.items():
            # Check if the object is an instance or derivative of the specified type
            if is_instance_or_derivative(obj, object_type):
                objects.append(obj)
            # Check if the object is a list or tuple containing instances or derivatives of the specified type
            elif isinstance(obj, (list, tuple)):
                for item in obj:
                    if is_instance_or_derivative(item, object_type):
                        objects.append(item)
    return objects
