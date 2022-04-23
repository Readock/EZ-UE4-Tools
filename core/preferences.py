"""Blender add-on preferences for the Addon"""
import bpy
from os import environ, path
from bpy.props import BoolProperty, StringProperty, EnumProperty
from bpy.types import AddonPreferences
from ..utils import addon
from os.path import normpath
from pathlib import Path

def source_path():
    """Returns the Addon's Project source path."""
    source_path = __preferences().source_path
    if not source_path:
        # use path of blend file as default
        return Path(bpy.data.filepath).parent
    return bpy.path.abspath(normpath(source_path))

def export_prefix():
    """Returns the Addon's export prefix for collections."""
    return __preferences().export_prefix

def export_priority_object_prefix():
    """Returns the Addon's export prefix for priority objects."""
    return __preferences().export_priority_object_prefix

def export_exclude_object_prefix():
    """Returns the Addon's export prefix for object exclude."""
    return __preferences().export_exclude_object_prefix

def collision_prefix():
    """Returns the Addon's collision prefix for collections."""
    return __preferences().collision_prefix

def lowpoly_regex():
    """Returns the Addon's lp regex for collections."""
    return __preferences().lowpoly_regex

def highpoly_regex():
    """Returns the Addon's hp regex for collections."""
    return __preferences().highpoly_regex

def autouv_prefix():
    """Returns the Addon's auto uv regex for collections."""
    return __preferences().autouv_prefix

def export_collection_name():
    """Returns the Addon's export collections name"""
    return __preferences().export_collection_name
    
def show_export_dialog():
    """Returns the Addon's Project source path."""
    return __preferences().show_export_dialog

def collection_export_name_template():
    """Export current scene only."""
    return __preferences().collection_export_name_template

def armature_export_name_template():
    """Export current scene only."""
    return __preferences().armature_export_name_template


class EZUE4AddonPreferences(AddonPreferences):
    """Preferences class for the Addon"""
    bl_idname = addon.get_addon_name()
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
        description="Prefix name to detect exportable collections and armatures",
        default= ".",
        subtype='NONE'
    )

    export_priority_object_prefix: StringProperty(
        name="Object first priority prefix",
        description="Object prefix to set this object as active before merging (eg. to use its origin or shading)",
        default= ".",
        subtype='NONE'
    )
    
    export_exclude_object_prefix: StringProperty(
        name="Object exclude prefix",
        description="Prefix name to detect objects that should not be exported",
        default= "#",
        subtype='NONE'
    )
    
    collision_prefix: StringProperty(
        name="Collision (UCX) prefix",
        description="Prefix to to detect the collision of exportable collections",
        default= "UCX_",
        subtype='NONE'
    )
    
    lowpoly_regex: StringProperty(
        name="LowPoly (LP) regex",
        description="Regex to detect low poly",
        default= "(?i)_lp$",
        subtype='NONE'
    )
    
    highpoly_regex: StringProperty(
        name="HighPoly (HP) regex",
        description="Regex to detect high poly",
        default= "(?i)_hp$",
        subtype='NONE'
    )
    
    autouv_prefix: StringProperty(
        name="Auto UV prefix",
        description="Auto uv unwrap prefix",
        default= "AUV_",
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
    
    collection_export_name_template: StringProperty(
        name="Export name template",
        description="Template for the export name",
        default= "$(file)_$(collection)",
        subtype='NONE'
    )
    
    armature_export_name_template: StringProperty(
        name="Export name template",
        description="Template for the export name",
        default= "$(file)_$(armature)",
        subtype='NONE'
    )

    def draw(self, context):
        """Draws the preferences."""
        self.layout.prop(self, 'source_path', expand=True)
        self.layout.prop(self, 'show_export_dialog', expand=True)
        self.layout.prop(self, 'export_prefix', expand=True)
        self.layout.prop(self, 'export_priority_object_prefix', expand=True)
        self.layout.prop(self, 'export_exclude_object_prefix', expand=True)        
        self.layout.prop(self, 'collision_regex', expand=True)
        self.layout.prop(self, 'export_collection_name', expand=True)
        
        box = self.layout.box()
        box.label(text="Collection Export:", icon="OUTLINER_OB_GROUP_INSTANCE")
        box.prop(self, 'autouv_prefix', expand=True)
        box.prop(self, 'lowpoly_regex', expand=True)
        box.prop(self, 'highpoly_regex', expand=True)
        box.prop(self, 'collection_export_name_template', expand=True)

        box = self.layout.box()
        box.label(text="Armature Export:", icon="OUTLINER_OB_ARMATURE")
        box.prop(self, 'armature_export_name_template', expand=True)

        box = self.layout.box()
        box.label(text="Pie Menu:", icon="KEY_HLT")
        box.label(text="Ctrl + Alt + Shift + W")

    def set_items(self, items):
        """Sets custom properties back on this item."""
        for item in items:
            prop_val = getattr(self, item[0], None)
            if prop_val is not None:
                setattr(self, item[0], item[1])
                

def __preferences() -> EZUE4AddonPreferences:
    return bpy.context.preferences.addons[addon.get_addon_name()].preferences

REGISTER_CLASSES = (
    EZUE4AddonPreferences,
)
