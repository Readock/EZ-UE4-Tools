"""Blender add-on preferences for the Addon"""


from os import environ, path
from bpy.props import BoolProperty, StringProperty, EnumProperty
from bpy.types import AddonPreferences
from . import get_addon_name


class EZUE4AddonPreferences(AddonPreferences):
    """Preferences class for the Addon"""

    bl_idname = get_addon_name()
    bl_label = "Source Location"
    bl_region_type = 'UI'
    bl_category = 'EZUE4'

    stored_source_path: StringProperty(options={'HIDDEN'})

    def _source_path_changed(self, context):
        """Called when the source_path property is changed."""
        if not self.source_path:
            self.stored_source_path = self.source_path
        elif path.exists(self.source_path):
            self.stored_source_path = self.source_path
        else:
            print(f"Error: Path does not exist: '{self.source_path}'")
            if self.stored_source_path and path.exists(self.stored_source_path):
                self.source_path = self.stored_source_path

    show_export_dialog: BoolProperty(
        name="Show Export Dialog",
        description="If enabled, exporting confirm dialog will show up",
        default=True,
    )
    
    export_prefix: StringProperty(
        name="Export prefix",
        description="Prefix name to detect exportable collections",
        default= ".",
        subtype='NONE'
    )
    
    export_collection_name: StringProperty(
        name="Export collection",
        description="Name of the collection to be used for exporting",
        default= "EZ-UE4-Export",
        subtype='NONE'
    )
    
    source_path: StringProperty(
        name="Project source folder",
        description="Location of raw source files for your project, used as a root for scene & import/export paths",
        default= "",
        subtype='DIR_PATH',
        update=_source_path_changed,
    )

    def draw(self, context):
        """Draws the preferences."""
        self.layout.prop(self, 'show_export_dialog', expand=True)
        self.layout.prop(self, 'export_prefix', expand=True)
        self.layout.prop(self, 'export_collection_name', expand=True)
        self.layout.prop(self, 'source_path', expand=True)

    def set_items(self, items):
        """Sets custom properties back on this item."""
        for item in items:
            prop_val = getattr(self, item[0], None)
            if prop_val is not None:
                setattr(self, item[0], item[1])


REGISTER_CLASSES = (
    EZUE4AddonPreferences,
)
