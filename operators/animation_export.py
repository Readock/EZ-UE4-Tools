# import bpy
# import os
# import fnmatch

# from sys import path
# path.append(bpy.path.abspath("//"))
# from common import *

# def GetChildsOneDepth(obj):
#     # Get all direct childs of a object

#     ChildsObj = []
#     for childObj in bpy.data.objects:
#         if childObj.library is None:
#             pare = childObj.parent
#             if pare is not None:
#                 if pare.name == obj.name:
#                     ChildsObj.append(childObj)

#     return ChildsObj

# def GetRecursiveChilds(obj):
#     # Get all recursive childs of a object

#     saveObjs = []

#     def tryAppend(obj):
#         if obj.name in bpy.context.scene.objects:
#             saveObjs.append(obj)

#     for newobj in GetChildsOneDepth(obj):
#         for childs in GetRecursiveChilds(newobj):
#             tryAppend(childs)
#         tryAppend(newobj)
#     return saveObjs

# def SelectParentAndDesiredChilds(obj):
#     # Selects only all child objects that must be exported with parent object
#     selectedObjs = []
#     bpy.ops.object.select_all(action='DESELECT')
#     for selectObj in GetRecursiveChilds(obj):
#         if selectObj.name in bpy.context.view_layer.objects:
#             if obj.type == "ARMATURE":
#                 # With skeletal mesh the socket must be not exported,
#                 # ue4 read it like a bone
#                 if not fnmatch.fnmatchcase(selectObj.name, "SOCKET*"):
#                     selectObj.select_set(True)
#                     selectedObjs.append(selectObj)
#             else:
#                 selectObj.select_set(True)
#                 selectedObjs.append(selectObj)

#     obj.select_set(True)

#     selectedObjs.append(obj)
#     bpy.context.view_layer.objects.active = obj
#     return selectedObjs

# def exportArmature(armatureName):
#     print("==========================")
#     print("Exporting Armature: "+armatureName)
#     print("==========================")

#     bpy.ops.object.select_all(action='DESELECT')
#     armature = bpy.context.scene.objects.get(armatureName)
#     SelectParentAndDesiredChilds(armature)
    
#     projectName, _ = os.path.splitext(bpy.path.basename(bpy.context.blend_data.filepath))
#     exportName = projectName + "_" + armatureName

#     bpy.ops.export_scene.fbx(
#         filepath=bpy.path.abspath("//" + exportName + ".fbx"),
#         object_types={'ARMATURE', 'EMPTY', 'MESH'},
#         axis_forward='X',
#         axis_up ='Z',
#         global_scale= 1.0,
#         use_armature_deform_only=True,
#         bake_anim=True,
#         bake_anim_use_all_bones=True,
#         bake_anim_use_nla_strips=True,
#         bake_anim_use_all_actions=False,
#         bake_anim_force_startend_keying=True,
#         use_selection=True)

# def exportArmatures(exportArmatures):
#     for export in exportArmatures:
#         exportArmature(export)

#     print("==========================")
#     print("Export complete")
#     print("==========================")

# # =============================
# #           Example
# # =============================
# #from sys import path
# #path.append(bpy.path.abspath("//")+'/../Scripts')
# #from fbx_animation_export import exportAnimation
# ## =======================
# ## - one Root bone and all other bones attached
# ## - exports animations from the NonLinear Animation Strips ('N' -> Strip to change the name) 
# ## - avoid the name "Armature"
# ## - set to rest pose when exporting
# #animation_exports = [ 
# #    "BladeRailArmature"
# #]
# ## =======================
# #exportArmature(animation_exports)