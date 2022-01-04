import bpy

def has_collection_with_name(name):
    """ Checks if a collection exists """
    for o in bpy.data.collections:
        if o.name == name:
            return True
    return False

def recur_layer_collection_with_name(layerCollection, name):
    """ Recursivly transverse layer_collection for a particular name """
    found = None
    if (layerCollection.name == name):
        return layerCollection
    for layer in layerCollection.children:
        found = recur_layer_collection_with_name(layer, name)
        if found:
            return found

def find_layer_collection_with_name(name):
    """ Find layer collection by name """
    # Collection and layer collection are not the same thing!
    root = bpy.context.view_layer.layer_collection
    return recur_layer_collection_with_name(root, name)

def select_objects_of_collection(collection):
    """ Select all Objects of a collection """
    bpy.ops.object.select_all(action='DESELECT')
    for obj in collection.all_objects:
        if obj and obj.type == 'MESH':
            obj.select_set(True)

def select_objects_of_collection_with_name(collectionName):
    """ Select all Objects of a collection by name"""
    collection = bpy.data.collections[collectionName]
    select_objects_of_collection(collection)

def move_to_collection(object, collection):  
    """ Move object to the export collection"""   
    for c in object.users_collection:
        c.objects.unlink(object)
    collection.objects.link(object)

def move_to_collection_with_name(object, collectionName):     
    for collection in object.users_collection:
        collection.objects.unlink(object)
    bpy.data.collections[collectionName].objects.link(object)

def delete_collection(collection):
    """ Deletes a collection with the objects in it """
    if not collection:
        return
    # delete objects of collection
    bpy.ops.object.select_all(action='DESELECT')
    select_objects_of_collection(collection)
    bpy.ops.object.delete()

    bpy.data.collections.remove(collection)

def delete_collection_with_name(collectionName):
    """ Deletes a collection by name with the objects in it """
    collection = bpy.data.collections[collectionName]
    if not collection:
        return
    delete_collection(collection)

def unhide_collection(collection):
    collection.hide_viewport = False
    for obj in collection.all_objects:
        if obj.type == 'MESH':
            obj.hide_set(False)

def is_linked(collection):
    """If the collection is linked form another blend file"""
    return collection.library

def is_in_current_Scene(collection):
    """If collection is in the current scene"""
    current_scene = bpy.context.scene    
    return all(current_scene in obj.users_scene for obj in collection.all_objects)