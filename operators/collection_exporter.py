"""Export operator for faster and more consistent export Workflow"""

import bpy
import os
from bpy.props import BoolProperty
from ..core import find_exportable_collections, get_export_collection_name, get_export_prefix, get_project_name, get_source_path, get_show_export_dialog
from ..utils import collections, modifiers, objects

GROUPS_ICON = 'OUTLINER_OB_GROUP_INSTANCE'
BUNDLE_SUFFIX = '_bundle'

class CollectionExporter(bpy.types.Operator):
    """ Export collections """

    bl_idname = "screen.ezue4_export"
    bl_label = "Export Collections"
    bl_description = "Export collections"

    clean_up_export: BoolProperty(name="Clean-Up Export", description="Clean-Up will delete the meshes generated for export", default=True)
    child_bundle_export: BoolProperty(name="Bundle Children", description="Merges child collections seperate and exports them as one fbx (not joined together)", default=True)

    display_exportable: BoolProperty(name="Export Output", description="Should display the output result", default=False)

    def execute(self, context):
        """Exports the Export Collections"""        

        exportable_collections = find_exportable_collections()

        # change to object mode
        objects.switch_to_object_mode()
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
        return self.execute(context)
    
    def has_any_export_collection_children(self):
        export_collections = find_exportable_collections()
        for collection in export_collections:
            if collection.children:
                return True
        return False

    def draw(self, context):
        """ Draw List of collections to export """
        box = self.layout.box()
        row = box.row()
        row.prop(self, "clean_up_export")

        if self.has_any_export_collection_children():
            row.prop(self, "child_bundle_export")

        export_collections = find_exportable_collections()

        box2 = self.layout.box()
        box2.prop(self, "display_exportable", icon="TRIA_DOWN" if self.display_exportable else "TRIA_RIGHT", text="Output")

        if self.display_exportable:
            for collection in export_collections:
                box2.row().label(text=self.get_export_name_of_collection(collection), icon="EXPORT")
                if collection.children and self.child_bundle_export:
                    box2.row().label(text=self.get_bundle_export_name_of_collection(collection), icon="EXPORT")       


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

        objects.unselect_none_solid()
        
        if not bpy.context.selected_objects:
            return

        # duplicate selected objects
        bpy.ops.object.duplicate()

        # because issues with decalMachine
        self.resolve_atlas_uv()
                
        # apply modifiers
        modifiers.apply_modifiers(bpy.context.selected_objects)
        
        objects.set_active(bpy.context.selected_objects[0])

        # join selected objects
        bpy.ops.object.join()
            
        # rename joined object
        bpy.context.selected_objects[0].name = joinedMeshName
        
        collections.move_to_collection_with_name(bpy.context.selected_objects[0], get_export_collection_name())
        collections.find_layer_collection_with_name(collection.name).exclude = was_excluded

    def get_export_name_of_collection(self, collection):
        return get_project_name() + "_" + collection.name.removeprefix(get_export_prefix())

    def get_bundle_export_name_of_collection(self, collection):
        return self.get_export_name_of_collection(collection) + BUNDLE_SUFFIX
   
    def set_up_export_collection_with_name(self, collectionName):
        """ Creates the export collection or deletes all objects inside if it alredy exists """
        # create Export Collection if not exist
        if not collections.has_collection_with_name(collectionName):
            collection = bpy.data.collections.new(collectionName)
            bpy.context.scene.collection.children.link(collection)
        bpy.ops.object.select_all(action='DESELECT')
        
        # make shure the collection is included
        collections.find_layer_collection_with_name(collectionName).exclude = False

        #select all objects in Export and delete them
        collections.select_objects_of_collection_with_name(collectionName)
        bpy.ops.object.delete()

    def export_collection_children_as_bundle(self, collection):
        if not collection.children:
            return
        bpy.ops.object.select_all(action='DESELECT')
        # join individual collections
        for childCollection in collection.children:
            self.join_collection(childCollection, self.get_export_name_of_collection(childCollection))
        # select joined
        for childCollection in collection.children:
            objects.set_active_with_name(self.get_export_name_of_collection(childCollection))
        # move to export collection
        for selected_object in bpy.context.selected_objects:
            collections.move_to_collection_with_name(selected_object, get_export_collection_name())
        
        if not bpy.context.selected_objects:
            return

        #export as bundle
        parentExportName = self.get_export_name_of_collection(collection) + BUNDLE_SUFFIX
        self.export_selected_as_fbx(parentExportName)
        bpy.ops.object.select_all(action='DESELECT')

    def export_collection(self, collection):
        """ Export objects of a collection to a FBX """
        if not collection:
            return

        self.report({'INFO'}, f"Exporting collection '{collection.name}'")
        print("==========================")
        print("Exporting: "+collection.name)
        print("==========================")
        collections.unhide_collection(collection)
        exportName = self.get_export_name_of_collection(collection)
        
        if self.child_bundle_export:
            self.export_collection_children_as_bundle(collection)            

        # join mesh to one
        self.join_collection(collection, exportName)

        ucxCollectionName = "UCX_" + collection.name
        # select objects to export
        if collections.has_collection_with_name(ucxCollectionName):
            self.rename_ucx_collection_objects(ucxCollectionName, exportName)
            collections.select_objects_of_collection_with_name(ucxCollectionName)
        mesh = bpy.context.scene.objects.get(exportName)
        objects.set_active(mesh)
        
        #export fbx
        self.export_selected_as_fbx(exportName)
    
    
    def export_selected_as_fbx(self, export_name):    
        """ Exports selected objects as fbx """
        export_path = os.path.join( get_source_path() , export_name + ".fbx")
        bpy.ops.export_scene.fbx(filepath=export_path, use_selection=True, mesh_smooth_type="FACE")

        
    def export_collections(self, exportCollections):
        """Exports all exportCollections to a fbx file"""
        self.set_up_export_collection_with_name(get_export_collection_name())
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
    export_objects = find_exportable_collections()
    menu_text="No Export Collections in scene!"
    if export_objects:
        menu_text = f"Export Collections ({len(export_objects)})"
    self.layout.operator(CollectionExporter.bl_idname, text=menu_text, icon=GROUPS_ICON)

REGISTER_CLASSES = (
    CollectionExporter,
)
