import bpy


def set_active(obj):
    """ Sets the object as active """
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj