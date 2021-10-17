import bpy
import os
from ..core import get_source_path


def set_active(obj):
    """ Sets the object as active """
    if obj:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

def find_with_name(name):
    return bpy.context.scene.objects[name]

def set_active_with_name(name):
    set_active(find_with_name(name))

def smooth_normals_of_selected():
    if bpy.context.selected_objects:
        # make shure we have one object active selected
        if not bpy.context.view_layer.objects.active:
            set_active(bpy.context.selected_objects[0])
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.smooth_normals()
        switch_to_object_mode()

def unselect_none_solid():
    """ Unselect objects that are displayed as bounds or wire (usualy cutter) """
    for obj in bpy.context.selected_objects:
        if obj and obj.type == 'MESH':
            if obj.display_type == 'WIRE' or obj.display_type == 'BOUNDS':
                obj.select_set(False)

def switch_to_object_mode():
    if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

def export_selected_as_fbx(export_name):    
    export_path = os.path.join( get_source_path() , export_name + ".fbx")
    bpy.ops.export_scene.fbx(filepath=export_path, use_selection=True, mesh_smooth_type="FACE")