"""Custom Blender Operators that are loaded by default with the Tools.

If you add a new Operator, please define register() and unregister() functions
for it, and then import it in this file and add it to the __operators__ list.
"""


from . import (
    documentation,
    collection_exporter,
)


# List of operators to load by default.
REGISTER_CLASSES = (
    documentation,
    collection_exporter,
)
