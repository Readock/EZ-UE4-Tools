import bpy
import os
import fnmatch
from bpy.props import BoolProperty
from ..core import find_exportable_armatures, unselect_unwanted_objects_for_export, preferences
from ..utils import collections, modifiers, objects, armatures, export, addon, modes

ACTIONS_SUFFIX = "_Animations"

class AnimationExporter(bpy.types.Operator):
    """Export armatures"""

    bl_label = "Animation Export"
    bl_idname = "screen.ezue4_animation_export"
    bl_description = "Export armatures"
    custom_icon = 'OUTLINER_OB_ARMATURE'

    display_exportable: BoolProperty(name="Export Output", description="Should display the output result", default=False)

    should_export_mesh: BoolProperty(name="Mesh", default=True)
    should_export_actions: BoolProperty(name="Actions", default=True)

    def execute(self, context):
        """Export armature and its actions"""

        exportable_armatures = find_exportable_armatures()

        # change to object mode
        modes.switch_to_object()
        modes.exit_local_view()

        if not exportable_armatures:
            self.report({'WARNING'}, "No exportable armatures found!")
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
        if preferences.show_export_dialog():
            return context.window_manager.invoke_props_dialog(self)
        return self.execute(context)

    def draw(self, context):
        """ Draw List of collections to export """
        export_armatures = find_exportable_armatures()
        
        row = self.layout.row(align=True)
        row.label(text="Export:")
        row.prop(self, "should_export_mesh", text="Mesh", toggle=True)
        row.prop(self, "should_export_actions", text="Actions", toggle=True)

        for armature in export_armatures:
            root_bone_count = 0
            for bone in armature.data.bones:
                if not bone.parent:
                    root_bone_count = root_bone_count + 1 
            if root_bone_count > 1:
                self.layout.row().label(text=f"'{armature.name}' has more than one root bone!", icon="ERROR")

        if self.should_export_actions:
            for armature in export_armatures:
                if not armatures.get_actions(armature):
                    self.layout.row().label(text=f"'{armature.name}' has no actions", icon="ERROR")
        
        if not self.should_export_actions and not self.should_export_mesh:
            self.layout.row().label(text=f"Nothing to Export! (select 'Mesh' or 'Actions')", icon="ERROR")

        box2 = self.layout.box()
        box2.prop(self, "display_exportable", icon="TRIA_DOWN" if self.display_exportable else "TRIA_RIGHT", text="Output")

        if self.display_exportable:
            for armature in export_armatures:
                inner_box = self.layout.box()
                
                if self.should_export_mesh:
                    col = inner_box.column()
                    row = col.split(factor=0.05, align=True)
                    row.label(text="")
                    r = row.row(align=True)
                    r.label(text=self.get_export_name_of_armature(armature), icon="MESH_DATA")

                if self.should_export_actions:
                    actions = armatures.get_actions(armature)
                    if actions:
                        for action in actions:
                            col = inner_box.column()
                            row = col.split(factor=0.05, align=True)
                            row.label(text="")
                            r = row.row(align=True)
                            r.label(text=self.get_export_name_of_armature(armature)+"_"+action.name, icon="ACTION")
                    else:
                        col = inner_box.column()
                        row = col.split(factor=0.05, align=True)
                        row.label(text="")
                        r = row.row(align=True)
                        r.label(text=f"ERROR: No Actions found!", icon="ERROR")

                    
    def select_armature_with_mesh(self, armature):
        """Selects only all child objects that must be exported with parent object"""
        bpy.ops.object.select_all(action='DESELECT')
        for child in objects.get_children_of(armature):
            if child.name in bpy.context.view_layer.objects:
                # With skeletal mesh the socket must be not exported,
                # ue4 read it like a bone
                if not fnmatch.fnmatchcase(child.name, "SOCKET*"):
                    child.select_set(True)
        objects.set_active(armature)
        unselect_unwanted_objects_for_export()
 
    def get_export_name_of_armature(self, armature):
        """Generates the output name for an armature"""
        name = preferences.armature_export_name_template()
        armature_name = armature.name.removeprefix(preferences.export_prefix())
        name = name.replace("$(armature)", armature_name)
        name = name.replace("$(file)", addon.get_project_name())
        return name

    def batch_export_actions(self, armature):
        """Export all actions as seperate fbx file"""
        armatures.create_animation_data(armature)
        actions = armatures.get_actions(armature)
        for action in actions:
            # set the scenes frame start/end from the actions frame range...
            bpy.context.scene.frame_start, bpy.context.scene.frame_end = int(round(action.frame_range[0], 0)), int(round(action.frame_range[1], 0))
            
            armatures.clear_pose_transform(armature)
            # setting the action to be the active one...
            armature.animation_data.action = action

            objects.deselect()
            self.select_armature_with_mesh(armature)

            armature.data.pose_position = 'POSE'            
            self.export_action_as_fbx(self.get_export_name_of_armature(armature) + "_" + action.name)
    
    def export_mesh(self, armature):
        """Export the armature and mesh"""
        objects.deselect()
        self.select_armature_with_mesh(armature)

        self.export_mesh_as_fbx(self.get_export_name_of_armature(armature))
        objects.deselect()

    def export_mesh_as_fbx(self, name):
        """Export fbx"""
        export_path = os.path.join( preferences.source_path() , name + ".fbx")
        bpy.ops.export_scene.fbx(
            filepath=bpy.path.abspath(export_path),
            object_types={'ARMATURE', 'EMPTY', 'MESH'},
            apply_scale_options='FBX_SCALE_ALL', 
            apply_unit_scale= True,
            bake_space_transform=False,
            axis_forward='X',
            axis_up ='Z',
            global_scale= 1.0,
            use_armature_deform_only=True,
            use_mesh_edges=False,
            bake_anim=False,
            mesh_smooth_type="EDGE",
            use_selection=True)

    def export_action_as_fbx(self, name):
        """Export fbx"""        
        export_path = os.path.join( preferences.source_path() , name + ".fbx")
        bpy.ops.export_scene.fbx(
            filepath=bpy.path.abspath(export_path),
            object_types={'ARMATURE', 'EMPTY'},
            apply_scale_options='FBX_SCALE_ALL', 
            apply_unit_scale= True,
            bake_space_transform=False,
            axis_forward='X',
            axis_up ='Z',
            global_scale= 1.0,
            add_leaf_bones=False,
            use_armature_deform_only=True,
            bake_anim=True,
            bake_anim_use_all_bones=True,
            bake_anim_use_nla_strips=False,
            bake_anim_use_all_actions=False,
            bake_anim_force_startend_keying=True,
            mesh_smooth_type="EDGE",
            use_mesh_edges=False,
            batch_mode='OFF',
            use_selection=True)

    def export_armature(self, armature):
        self.report({'INFO'}, f"Exporting collection '{armature.name}'")
        print("==========================")
        print("Exporting Armature: "+armature.name)
        print("==========================")
        
        self.scale_armature_for_export(armature)
        
        if self.should_export_actions:
            self.batch_export_actions(armature)
        if self.should_export_mesh:
            self.export_mesh(armature)

        self.revert_scale_armature_for_export(armature)
    
    def scale_armature_for_export(self, armature):
        """Apply armature scale for ue4 export"""
        objects.deselect()
        export_scale_factor = export.units_blender_to_fbx_factor()
        objects.set_active(armature)
        objects.unit_scale_selected(export_scale_factor)
        objects.deselect()

    def revert_scale_armature_for_export(self, armature):
        """Revert armature scale after ue4 export"""
        objects.deselect()
        export_scale_factor = export.units_blender_to_fbx_factor()
        objects.set_active(armature)
        objects.unit_scale_selected(1.0/export_scale_factor)
        objects.deselect()

    @classmethod
    def poll(cls, context):
        """Only allows this operator to execute if there is a valid selection."""
        return find_exportable_armatures() and bpy.data.is_saved


def menu_draw(self, context):
    """Create the menu item."""
    export_objects = find_exportable_armatures()
    menu_text="No Export Armatures in scene!"
    if not bpy.data.is_saved:
        menu_text = "Save file first!"
    if export_objects:
        menu_text = f"Export Armatures ({len(export_objects)})"
    self.layout.operator(AnimationExporter.bl_idname, text=menu_text, icon=AnimationExporter.custom_icon)


REGISTER_CLASSES = (
    AnimationExporter,
)
