import bpy
import os

def add_to_selection(obj):
    """ Sets the object as selected (and not active) """
    if obj:
        obj.select_set(True)

def remove_from_selection(obj):
    """ Sets the object as not selected"""
    if obj:
        obj.select_set(False)

def set_active(obj):
    """ Sets the object as active """
    if obj:
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

def get_active():
    return bpy.context.view_layer.objects.active

def get_selected():
    return bpy.context.selected_objects

def deselect():
    """ Deselects all active elements """
    bpy.ops.object.select_all(action='DESELECT')

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
                remove_from_selection(obj)

def switch_to_object_mode():
    """ Switch mode to object mode """
    if bpy.context.active_object and bpy.context.active_object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

def switch_to_edit_mode():
    """ Switch mode to object mode """
    if bpy.context.active_object and bpy.context.active_object.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')

def get_direct_children_of(obj):
    """ Get all direct childs of a object """
    if not obj:
        return []
    child_objects = []
    for childObj in bpy.data.objects:
        if childObj.library is None:
            pare = childObj.parent
            if pare is not None:
                if pare.name == obj.name:
                    child_objects.append(childObj)
    return child_objects

def get_children_of(obj):
    """ Get all (recrusive) childs of an object """
    child_objects = []
    if not obj:
        return child_objects
    def tryAppend(obj):
        if obj.name in bpy.context.scene.objects:
            child_objects.append(obj)

    for newobj in get_direct_children_of(obj):
        for childs in get_children_of(newobj):
            tryAppend(childs)
        tryAppend(newobj)
    return child_objects

def find_all_of_type(object_type):
    """ Finds all the objects of an type (eg. 'MESH' or 'ARMATURE') """
    objects = []
    for obj in bpy.data.objects:
        if obj.type == object_type:
            objects.append(obj)
    return objects


def unit_scale_selected(unit_scaling):
    """Scales selected objects to another unit scale"""
    for obj in bpy.context.selected_objects:
        # multiply location to get offsets right
        obj.location = [obj.location.x * unit_scaling, obj.location.y * unit_scaling, obj.location.z * unit_scaling]
        obj.scale = [obj.scale.x * unit_scaling, obj.scale.y * unit_scaling, obj.scale.z * unit_scaling]

def apply_transform_to_selected():
    """Apply tranform to selected objects"""
    current_active = get_active()
    for obj in bpy.context.selected_objects:
        set_active(obj)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True, properties=True)
    if current_active:
        set_active(current_active)

def apply_scale_and_rotation_to_selected():
    """Apply tranform to selected objects"""
    current_active = get_active()
    for obj in bpy.context.selected_objects:
        set_active(obj)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True, properties=True)
    if current_active:
        set_active(current_active)

def auto_uv_selected():
    """ Unwraps selected objects """
    if not bpy.context.active_object:
        return
    og_mode = bpy.context.active_object.mode
    switch_to_edit_mode()

    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project( island_margin=0.01)
    
    # switch back
    bpy.ops.object.mode_set(mode=og_mode)

def is_in_current_Scene(object):    
    current_scene = bpy.context.scene 
    return current_scene in object.users_scene

def is_linked(collection):
    """If the collection is linked form another blend file"""
    return collection.library

def resolve_atlas_uv_from_selected():
    """ Fix names from Decal Machine """
    # renames Atlas UVs so the join dose not break the UVs
    # (when joining all UVs need to have the same name)
    for obj in bpy.context.selected_objects:
        for uvmap in  obj.data.uv_layers :
            if uvmap.name == "Atlas UVs":
                uvmap.name = "UVMap"
                print("UV name missmatch detected and resolved")

def ensure_selection_has_active():
    """Selects the first of the selected objects if none is active"""
    if not bpy.context.selected_objects or get_active():
        return
    set_active(bpy.context.selected_objects[0])

def delete(obj):
    """Deletes an object"""
    bpy.data.objects.remove(obj, do_unlink=True)

def convert_selected_to_mesh():
    """ Converts selected objects to mesh """
    with SelectionContext():
        switch_to_object_mode()
        selection = get_selected()
        for obj in selection:
            if obj.type != "CURVE" and obj.type != "GPENCIL" and obj.type != "MESH":
                remove_from_selection(obj)
        if get_selected():
            ensure_selection_has_active()
            # converts all selected to mesh (not only the active one)
            bpy.ops.object.convert(target='MESH')


def smart_join_selected(name = None):
    """ Join selected objects in a duplicate object """
    from . import modifiers
    from ..core import set_selection_priority_object_as_active, unselect_unwanted_objects_for_export
        
    if not bpy.context.selected_objects:
        return

    unselect_none_solid()
    unselect_unwanted_objects_for_export()
    # select best to use its config (eg. auto smooth)
    set_selection_priority_object_as_active() 

    # duplicate selected objects
    bpy.ops.object.duplicate()

    # convert eg. curves to mesh
    convert_selected_to_mesh()

    # because issues with decalMachine
    resolve_atlas_uv_from_selected()
            
    # apply modifiers (done with convert)
    # modifiers.apply_modifiers(bpy.context.selected_objects)
        
    # set duplicate of priority object as active (or if null any other)
    ensure_selection_has_active()

    # join selected objects
    bpy.ops.object.join()
        
    joined_object = bpy.context.selected_objects[0]
    if name:
        # rename joined object
        joined_object.name = name
    return joined_object

class SelectionContext():
    ''' Utility class to revert selection to previous state '''
    selected_objects = None
    active_object = None

    def __enter__(self):
        ''' Save current selection '''
        self.selected_objects = get_selected()
        self.active_object = get_active()
        return self

    def __exit__(self, type, value, traceback):
        ''' Revert selection to original '''
        deselect()
        for obj in self.selected_objects:
            add_to_selection(obj)
        if self.active_object:
            set_active(self.active_object)