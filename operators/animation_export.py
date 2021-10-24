import bpy
import os
import fnmatch
from bpy.props import BoolProperty
from ..core import find_exportable_armatures, get_export_prefix, get_project_name, get_source_path, get_show_export_dialog
from ..utils import collections, modifiers, objects

ARMATURE_ICON = 'OUTLINER_OB_ARMATURE'

## - one Root bone and all other bones attached
## - exports animations from the NonLinear Animation Strips ('N' -> Strip to change the name) 
## (- avoid the name "Armature")
## - set to rest pose when exporting

class AnimationExporter(bpy.types.Operator):
    """Export armatures"""

    bl_label = "Animation Export"
    bl_idname = "screen.ezue4_animation_export"
    bl_description = "Export armatures"

    display_exportable: BoolProperty(name="Export Output", description="Should display the output result", default=False)

    def execute(self, context):
        """Open the default web browser to the help URL."""

        exportable_armatures = find_exportable_armatures()

        # change to object mode
        objects.switch_to_object_mode()
        if not exportable_armatures:
            self.report({'WARNING'}, "No exportable collections found!")
            return {'FINISHED'}

        try:
            for armature in exportable_armatures:
                self.export_armature(armature)
        except Exception as ex: 
            self.report({'WARNING'}, "Export Failed! See console for more information")
            print(f"Error: Failed to export, reason: {ex}")        

        self.report({'INFO'}, f"Export Completed")
        print("==========================")
        print("Export complete")
        print("==========================")
        return {'FINISHED'}

    def invoke(self, context, event):
        if get_show_export_dialog():
            return context.window_manager.invoke_props_dialog(self)
        return self.execute(context)

    def draw(self, context):
        """ Draw List of collections to export """
        export_armatures = find_exportable_armatures()
        
        some_missing_nla = False
        for armature in export_armatures:
            if not armature.animation_data or not armature.animation_data.nla_tracks:
                some_missing_nla = True
        
        if some_missing_nla:
            self.layout.row().label(text=f"WARNING: Missing NLA-Strips (See Output)!", icon="ERROR")

        box2 = self.layout.box()
        box2.prop(self, "display_exportable", icon="TRIA_DOWN" if self.display_exportable else "TRIA_RIGHT", text="Output")

        if self.display_exportable:
            for armature in export_armatures:
                inner_box = self.layout.box()
                inner_box.row().label(text=self.get_export_name_of_armature(armature), icon="EXPORT")
                if armature.animation_data and armature.animation_data.nla_tracks:
                    for nla_track in armature.animation_data.nla_tracks:
                        inner_box.row().label(text=nla_track.name, icon="NLA")
                else:
                    inner_box.row().label(text=f"Armature '{armature.name}' has no NLA-Strips", icon="ERROR")
                    
    def select_armature_and_children_to_export(self, armature):
        """Selects only all child objects that must be exported with parent object"""
        selectedObjs = []
        bpy.ops.object.select_all(action='DESELECT')
        for selectObj in objects.get_children_of(armature):
            if selectObj.name in bpy.context.view_layer.objects:
                if armature.type == "ARMATURE":
                    # With skeletal mesh the socket must be not exported,
                    # ue4 read it like a bone
                    if not fnmatch.fnmatchcase(selectObj.name, "SOCKET*"):
                        selectObj.select_set(True)
                        selectedObjs.append(selectObj)
                else:
                    selectObj.select_set(True)
                    selectedObjs.append(selectObj)

        armature.select_set(True)

        selectedObjs.append(armature)
        bpy.context.view_layer.objects.active = armature
        return selectedObjs

    def get_export_name_of_armature(self, armature):
        return get_project_name() + "_" + armature.name.removeprefix(get_export_prefix())

    def export_armature(self, armature):
        self.report({'INFO'}, f"Exporting collection '{armature.name}'")
        print("==========================")
        print("Exporting Armature: "+armature.name)
        print("==========================")

        bpy.ops.object.select_all(action='DESELECT')
        self.select_armature_and_children_to_export(armature)
        

        export_path = os.path.join( get_source_path() , self.get_export_name_of_armature(armature) + ".fbx")
        bpy.ops.export_scene.fbx(
            filepath=bpy.path.abspath(export_path),
            object_types={'ARMATURE', 'EMPTY', 'MESH'},
            axis_forward='X',
            axis_up ='Z',
            global_scale= 1.0,
            use_armature_deform_only=True,
            bake_anim=True,
            bake_anim_use_all_bones=True,
            bake_anim_use_nla_strips=True,
            bake_anim_use_all_actions=False,
            bake_anim_force_startend_keying=True,
            mesh_smooth_type="FACE",
            use_selection=True)

        bpy.ops.object.select_all(action='DESELECT')

    @classmethod
    def poll(cls, context):
        """Only allows this operator to execute if there is a valid selection."""
        return  find_exportable_armatures()


def menu_draw(self, context):
    """Create the menu item."""
    export_objects = find_exportable_armatures()
    menu_text="No Export Armatures in scene!"
    if export_objects:
        menu_text = f"Export Armatures ({len(export_objects)})"
    self.layout.operator(AnimationExporter.bl_idname, text=menu_text, icon=ARMATURE_ICON)


REGISTER_CLASSES = (
    AnimationExporter,
)
