"""Export operator for faster and more consistent export Workflow"""

import bpy
import os
from bpy.props import BoolProperty
from ..core import find_exportable_collections, get_export_collection_name, get_export_prefix, get_project_name, get_source_path, get_show_export_dialog
from ..utils import collections, modifiers

GROUPS_ICON = 'OUTLINER_OB_GROUP_INSTANCE'

class CollectionExporter(bpy.types.Operator):
    """ Export collections """

    bl_idname = "screen.ezue4_export"
    bl_label = "Export Collections"
    bl_description = "Export collections"

    clean_up_export: BoolProperty(name="Clean-Up Export", default=True)

    def execute(self, context):
        """Exports the Export Collections"""        

        exportable_collections = find_exportable_collections()

        if not exportable_collections:
            self.report({'WARNING'}, "No exportable collections found!")
            return {'FINISHED'}

        try:
            self.export_collections(exportable_collections)
        except Exception as ex: 
            self.report({'WARNING'}, "Export Failed! See console for more information")
            print(f"Error: Failed to export, reason: {ex}")        
            

        return {'FINISHED'}

    def invoke(self, context, event):
        if get_show_export_dialog():
            return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        """ Draw List of collections to export """
        box = self.layout.box()
        row = box.row()
        row.prop(self, "clean_up_export")

        export_collections = find_exportable_collections()
        box2 = self.layout.box()
        for collection in export_collections:
            box2.row().label(text=self.get_export_name_of_collection(collection), icon="EXPORT")


    def rename_ucx_collection_objects(self, collectionName, exportName):
        """ Renames all objects of the collection to UCX standard """
        # avoid name intersections
        for obj in bpy.data.collections[collectionName].all_objects:
            if obj.type == 'MESH':
                obj.name = "UCX_rename"
        i = 0
        for obj in bpy.data.collections[collectionName].all_objects:
            if obj.type == 'MESH':
                i += 1 
                obj.name = "UCX_"+exportName+"_{:02d}".format(i)

    
    def resolve_atlas_uv(self):
        """ Fix names from Decal Machine """
        # renames Atlas UVs so the join dose not break the UVs
        # (when joining all UVs need to have the same name)
        for obj in bpy.context.selected_objects:
            for uvmap in  obj.data.uv_layers :
                if uvmap.name == "Atlas UVs":
                    uvmap.name = "UVMap"
                    print("UV name missmatch detected and resolved")

    def selection_non_child_as_active(self):
        """ Set first that has no parent as active """
        # (bug with decals) 
        for obj in bpy.context.selected_objects:
            print("checking: "+obj.name)
            if not obj.parent:
                print("set active Element: "+obj.name)
                bpy.context.view_layer.objects.active = obj
                if not obj.children:
                    print("also no children: "+obj.name)
                    break

    def join_collection(self, collection, joinedMeshName):
        if not collection:
            return
        print("Joining Collection: " + collection.name)
        # makes shure the collection is included (else we cant select objects of this collection)
        was_excluded = collections.find_layer_collection_with_name(collection.name).exclude
        collections.find_layer_collection_with_name(collection.name).exclude = False

        collections.select_objects_of_collection_with_name(collection.name)
        
        # duplicate selected objects
        bpy.ops.object.duplicate()

        # because issues with decalMachine
        self.resolve_atlas_uv()
        
        # apply modifiers
        modifiers.apply_modifiers(bpy.context.selected_objects)
        
        # join selected objects
        bpy.ops.object.join()
            
        # rename joined object
        bpy.context.selected_objects[0].name = joinedMeshName
        
        collections.move_to_collection_with_name(bpy.context.selected_objects[0], get_export_collection_name())
        collections.find_layer_collection_with_name(collection.name).exclude = was_excluded

    def get_export_name_of_collection(self, collection):
        return get_project_name() + "_" + collection.name.removeprefix(get_export_prefix())

    def export_collection(self, collection):
        """ Export objects of a collection to a FBX """
        if not collection:
            return

        self.report({'INFO'}, f"Exporting collection '{collection.name}'")
        print("==========================")
        print("Exporting: "+collection.name)
        print("==========================")
        
        exportName = self.get_export_name_of_collection(collection)

        # join mesh to one
        self.join_collection(collection, exportName)

        ucxCollectionName = "UCX_" + collection.name
        # select objects to export
        if collections.has_collection_with_name(ucxCollectionName):
            self.rename_ucx_collection_objects(ucxCollectionName, exportName)
            collections.select_objects_of_collection_with_name(ucxCollectionName)
        mesh = bpy.context.scene.objects.get(exportName)
        mesh.select_set(True)
        
        #export fbx
        export_path = os.path.join( get_source_path() , exportName + ".fbx")
        bpy.ops.export_scene.fbx(filepath=export_path, use_selection=True)
        
        
    # Exports all exportCollections to a fbx file
    def export_collections(self, exportCollections):
        collections.set_up_export_collection_with_name(get_export_collection_name())
        for export in exportCollections:
            self.export_collection(export)
        if self.clean_up_export:
            collections.delete_collection_with_name(get_export_collection_name())
    
        self.report({'INFO'}, f"Export Completed")
        print("==========================")
        print("Export complete")
        print("==========================")

    @classmethod
    def poll(cls, context):
        """Only allows this operator to execute if there is a valid selection."""
        return  find_exportable_collections()

def menu_draw(self, context):
    """Create the menu item."""
    self.layout.operator(CollectionExporter.bl_idname, icon = GROUPS_ICON)


REGISTER_CLASSES = (
    CollectionExporter,
)
