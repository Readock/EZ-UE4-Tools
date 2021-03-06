"""Custom Blender Operators that are loaded by default with the Tools.

If you add a new Operator, please define register() and unregister() functions
for it, and then import it in this file and add it to the __operators__ list.
"""


from .documentation import AddonDocumentation
from .open_source_path import OpenSourcePath
from .collection_exporter import CollectionExporter
from .animation_export import AnimationExporter
from .selected_quick_exporter import SelectedQuickExporter
from .perforce_checkout import PerforceCheckout


# List of operators to load by default.
REGISTER_CLASSES = (
    AddonDocumentation,
    OpenSourcePath,
    AnimationExporter,
    CollectionExporter,
    SelectedQuickExporter,
    PerforceCheckout,
)
