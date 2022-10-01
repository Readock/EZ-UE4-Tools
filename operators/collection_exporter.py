"""Export operator for faster and more consistent export Workflow"""

import bpy
import os
import re
from bpy.props import BoolProperty, EnumProperty
from ..core import find_exportable_collections, unselect_unwanted_objects_for_export, preferences
from ..utils import collections, modifiers, objects, export, addon, modes

BUNDLE_SUFFIX = '_bundle'

class CollectionExporter(bpy.types.Operator):
    """ Export collections """

    bl_idname = "screen.ezue4_export"
    bl_label = "Export Collections"
    bl_description = "Export collections"
    custom_icon = 'OUTLINER_OB_GROUP_INSTANCE'

    fix_scale_on_export: BoolProperty(name="Fix Scale", description="Scale x100 to fix unreal scaling issues", default=True)
    auto_uv_unwrap_export: BoolProperty(name="Force AutoUV Unwrap", description="Force Automated unwrapping after merging objects for all collections", default=False)
    clean_up_export: BoolProperty(name="Clean-Up Export", description="Clean-Up will delete the meshes generated for export", default=True)
    child_bundle_export: BoolProperty(name="Bundle Children", description="Merges child collections seperate and exports them as one fbx (not joined together)", default=True)

    should_export_other: BoolProperty(name="Other", default=True)
    should_export_lp: BoolProperty(name="LP", default=True)
    should_export_hp: BoolProperty(name="HP", default=True)
    should_export_ucx: BoolProperty(name="UCX", default=True)

    should_export_disabled: BoolProperty(name="Export Excluded Collections", default=False)

    display_exportable: BoolProperty(name="Export Output", description="Should display the output result", default=False)

    def execute(self, context):
        """Exports the Export Collections"""        

        # change to object mode
        modes.switch_to_object()
        modes.exit_local_view()

        collections_to_export = self.find_filtered_exportable_collections()
        if not collections_to_export:
            self.report({'WARNING'}, "No matching collections to export!")
            return {'FINISHED'}

        try:
            self.export_collections(collections_to_export)
        except Exception as ex: 
            self.report({'WARNING'}, "Export Failed! See console for more information")
            print(f"Error: Failed to export, reason: {ex}")
            import traceback
            traceback.print_exc()

        return {'FINISHED'}

    def find_filtered_exportable_collections(self):
        """ Applies user filter to exportable collections """
        exportable_collections = find_exportable_collections()
        filtered_exportable_collections = []
        for collection in exportable_collections:
            if collections.find_layer_collection_with_name(collection.name).exclude and not self.should_export_disabled:
                continue # ignore excluded collection if desired
            if self.is_collection_hp(collection):
                if self.should_export_hp:
                    filtered_exportable_collections.append(collection)
            elif self.is_collection_lp(collection):
                if self.should_export_lp:
                    filtered_exportable_collections.append(collection)
            elif self.should_export_other:
                filtered_exportable_collections.append(collection)
        return filtered_exportable_collections
        

    def invoke(self, context, event):
        if preferences.show_export_dialog:
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

        row = box.row(align=True)
        row.label(icon="FILTER")
        row.prop(self, "should_export_disabled", toggle=True)

        row = box.row(align=True)
        row.label(icon="FILTER")
        row.prop(self, "should_export_other", text="Other", toggle=True)
        row.prop(self, "should_export_lp", text="LP", toggle=True)
        row.prop(self, "should_export_hp", text="HP", toggle=True)
        row.prop(self, "should_export_ucx", text="UCX", toggle=True, icon="MESH_CUBE")

        row = box.row()
        row.prop(self, "fix_scale_on_export")
        row.prop(self, "auto_uv_unwrap_export")
        row = box.row()
        row.prop(self, "clean_up_export")

        if self.has_any_export_collection_children():
            row.prop(self, "child_bundle_export")

        export_collections = self.find_filtered_exportable_collections()

        box2 = self.layout.box()
        box2.prop(self, "display_exportable", icon="TRIA_DOWN" if self.display_exportable else "TRIA_RIGHT", text=f"Output ({len(export_collections)})")

        if self.display_exportable:
            for collection in export_collections:
                row = box2.row()
                row.alignment = 'LEFT'
                row.label(icon="EXPORT")
                if self.should_export_ucx and self.get_collections_ucx(collection):
                    row.label(icon="MESH_CUBE")
                if self.auto_uv_unwrap_export or self.is_collection_with_auto_uv_export(collection):
                    row.label(icon="TEXTURE")
                row.label(text=self.get_export_name_of_collection(collection))
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

        # join objects of collection into one object
        joined_object = objects.smart_join_selected(joinedMeshName)
        
        # move to export collection
        collections.move_to_collection_with_name(joined_object, preferences.export_collection_name())
        collections.find_layer_collection_with_name(collection.name).exclude = was_excluded

    def is_collection_with_auto_uv_export(self, collection):
        """Should collection use auto uv when exporting"""
        if collection:
            return collection.name.startswith(preferences.export_prefix() + preferences.autouv_prefix())
        return False

    def get_export_name_of_collection(self, collection):
        """Gets the export name of an collection"""
        name = preferences.collection_export_name_template()
        collection_name = collection.name.removeprefix(preferences.export_prefix())
        collection_name = collection_name.removeprefix(preferences.autouv_prefix())
        name = name.replace("$(collection)", collection_name)
        name = name.replace("$(file)", addon.get_project_name())
        return name

    def get_bundle_export_name_of_collection(self, collection):
        """Gets the bundle export name of an collection"""
        return self.get_export_name_of_collection(collection) + BUNDLE_SUFFIX
   
    def set_up_export_collection_with_name(self, collectionName):
        """ Creates the export collection or deletes all objects inside if it alredy exists """
        # create Export Collection if not exist
        collections.create_collection(collectionName)
        
        # make shure the collection is included
        collections.find_layer_collection_with_name(collectionName).exclude = False

        bpy.ops.object.select_all(action='DESELECT')

        #select all objects in Export and delete them
        collections.select_objects_of_collection_with_name(collectionName)
        bpy.ops.object.delete()

    def export_collection_children_as_bundle(self, collection):
        if not collection.children:
            return
        objects.deselect()
        # join individual collections
        for childCollection in collection.children:
            self.join_collection(childCollection, self.get_export_name_of_collection(childCollection))

        # auto uv
        if self.auto_uv_unwrap_export or self.is_collection_with_auto_uv_export(collection):
            for childCollection in collection.children:
                objects.deselect()
                objects.set_active_with_name(self.get_export_name_of_collection(childCollection))
                objects.auto_uv_selected()

        # select joined
        for childCollection in collection.children:
            objects.set_active_with_name(self.get_export_name_of_collection(childCollection))

        # move to export collection
        for selected_object in bpy.context.selected_objects:
            collections.move_to_collection_with_name(selected_object, preferences.export_collection_name())
        
        if not bpy.context.selected_objects:
            return

        #export as bundle
        parentExportName = self.get_export_name_of_collection(collection) + BUNDLE_SUFFIX
        export_path = os.path.join( preferences.source_path() , parentExportName + ".fbx")
        export.selected_objects_as_fbx(fix_scale = self.fix_scale_on_export, export_path=export_path)
        objects.deselect()

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

        # select joined mesh
        mesh = bpy.context.scene.objects.get(exportName)
        objects.set_active(mesh)

        # auto UV
        if self.auto_uv_unwrap_export or self.is_collection_with_auto_uv_export(collection):
            objects.auto_uv_selected()

        # prepare and select ucx (colliders)
        has_ucx = False
        was_ucx_excluded = False
        if self.should_export_ucx:
            ucx_collection = self.get_collections_ucx(collection)
            if ucx_collection:                
                has_ucx = True
                # makes shure the collection is included (else we cant select objects of this collection)
                was_ucx_excluded = collections.find_layer_collection_with_name(ucx_collection.name).exclude
                collections.find_layer_collection_with_name(ucx_collection.name).exclude = False

                self.rename_ucx_collection_objects(ucx_collection.name, exportName)
                collections.select_objects_of_collection(ucx_collection)
                unselect_unwanted_objects_for_export()
        
        # set joined mesh as active
        objects.set_active(mesh)

        #export fbx
        export_path = os.path.join( preferences.source_path() , exportName + ".fbx")
        export.selected_objects_as_fbx(fix_scale=self.fix_scale_on_export, export_path=export_path)

        # reset ucx exclude state
        if has_ucx:
            collections.find_layer_collection_with_name(ucx_collection.name).exclude = was_ucx_excluded

    def is_collection_lp(self, collection):
        """ If a collection is marked as low poly """
        return re.search(preferences.lowpoly_regex(), collection.name)

    def is_collection_hp(self, collection):
        """ If a collection is marked as high poly """
        return re.search(preferences.highpoly_regex(), collection.name)

    def get_ucx_collections(self):
        """ Finds the ucx (ue collision collection) for an collection """
        collections = []
        for c in bpy.data.collections:
            if c.name.startswith(preferences.collision_prefix()):
                collections.append(c)
        return collections

    def get_collections_ucx(self, collection):
        """ Finds the ucx (ue collision collection) for an collection """
        clean_name = collection.name.removeprefix(preferences.export_prefix())
        for c in self.get_ucx_collections():
            if c.name.removeprefix(preferences.collision_prefix()) == clean_name:
                return c
        return None
        
    def export_collections(self, exportCollections):
        """Exports all exportCollections to a fbx file"""
        self.set_up_export_collection_with_name(preferences.export_collection_name())
        for export in exportCollections:
            self.export_collection(export)
        if self.clean_up_export:
            collections.delete_collection_with_name(preferences.export_collection_name())
    
        self.report({'INFO'}, f"Export Completed")
        print("==========================")
        print("Export complete")
        print("==========================")

    @classmethod
    def poll(cls, context):
        """Only allows this operator to execute if there is a valid selection."""
        return find_exportable_collections() and bpy.data.is_saved
    
def menu_draw(self, context):
    """Create the menu item."""
    export_objects = find_exportable_collections()
    menu_text="No Export Collections in scene!"
    if not bpy.data.is_saved:
        menu_text = "Save file first!"
    if export_objects:
        menu_text = f"Export Collections ({len(export_objects)})"
    self.layout.operator(CollectionExporter.bl_idname, text=menu_text, icon=CollectionExporter.custom_icon)

REGISTER_CLASSES = (
    CollectionExporter,
)
