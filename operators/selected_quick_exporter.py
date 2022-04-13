"""Export operator for faster and more consistent export Workflow"""

import bpy
import os
from bpy.props import BoolProperty, StringProperty
from ..core import get_export_collection_name, get_project_name, get_source_path, get_show_export_dialog
from ..utils import collections, export, objects
from bpy_extras.io_utils import ExportHelper

class SelectedQuickExporter(bpy.types.Operator, ExportHelper):
    """ Export collections """
    bl_idname = "screen.ezue4_export_selected"
    bl_label = "Quick Export Selected"
    bl_description = "Export collections"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    custom_icon = 'TIME'

    fix_scale_on_export: BoolProperty(name="Fix Scale", description="Scale x100 to fix unreal scaling issues", default=True)
    auto_uv_unwrap_export: BoolProperty(name="Auto UV Unwrap", description="Automated unwrapping after merging objects", default=True)
    clean_up_export: BoolProperty(name="Clean-Up Export", description="Clean-Up will delete the meshes generated for export", default=True)
    exclude_none_solid: BoolProperty(name="Exclude None-Solid", description="Dont export selected WIRE or BOUNDS objects", default=True)

    # Override ExportHelper
    filepath: StringProperty(subtype="FILE_PATH", default='untitled')
    filename_ext = ".fbx"
    filter_glob : StringProperty(default="*.fbx", options={'HIDDEN'})

    def execute(self, context):
        """Exports the selected objects"""        

        # change to object mode
        objects.switch_to_object_mode()

        if not objects.get_selected():
            self.report({'WARNING'}, "No objects selected to export!")
            return {'FINISHED'}

        try:
            self.export_selected()
        except Exception as ex: 
            self.report({'WARNING'}, "Export Failed! See console for more information")
            print(f"Error: Failed to export, reason: {ex}")        
            
        return {'FINISHED'}     

    def invoke(self, context, event):
        self.filepath = "ez_quick_export" + self.filename_ext
        context.window_manager.fileselect_add(self)  
        return {'RUNNING_MODAL'}

    def draw(self, context):
        """ Draw export settings """        
        box = self.layout.box()

        row = box.row()
        row.prop(self, "fix_scale_on_export")
        row = box.row()
        row.prop(self, "auto_uv_unwrap_export")
        row = box.row()
        row.prop(self, "exclude_none_solid")
        row = box.row()
        row.prop(self, "clean_up_export")


    def export_selected(self):
        """ Export objects of a collection to a FBX """
        if not objects.get_selected():
            return

        self.report({'INFO'}, f"Exporting selected objects")
        print("==========================")
        print("Exporting: Selected objects")
        print("==========================")

        if self.exclude_none_solid:
            objects.unselect_none_solid()

        joined_obj = objects.smart_join_selected()
        
        collections.create_collection(get_export_collection_name())

        # move to export collection
        collections.move_to_collection_with_name(joined_obj, get_export_collection_name())

        # auto UV
        if self.auto_uv_unwrap_export:
            objects.auto_uv_selected()

        # export
        export.selected_objects_as_fbx(fix_scale = self.fix_scale_on_export, export_path=self.filepath)
        
        if self.clean_up_export:
            collections.delete_collection_with_name(get_export_collection_name())
    
        self.report({'INFO'}, f"Export Completed")
        print("==========================")
        print("Export complete")
        print("==========================")

    @classmethod
    def poll(cls, context):
        """Only allows this operator to execute if there is a valid selection."""
        return objects.get_selected()
    
def menu_draw(self, context):
    """Create the menu item."""
    menu_text="Nothing selected!"
    if objects.get_selected():
        menu_text = f"Export selected ({len(objects.get_selected())})"
    self.layout.operator(SelectedQuickExporter.bl_idname, text=menu_text, icon=SelectedQuickExporter.custom_icon)

REGISTER_CLASSES = (
    SelectedQuickExporter,
)
