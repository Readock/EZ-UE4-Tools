"""UI functionality including menus and icon management."""


from os import listdir, path
from bpy.types import Menu
from bpy.utils import previews, register_class, unregister_class
from ..operators.animation_export import AnimationExporter
from ..operators.collection_exporter import CollectionExporter
from ..core import find_exportable_armatures, find_exportable_collections


__icon_manager__ = None


class IconManager(): 
    """Singleton class for handling icons in the Blender previews system."""
    icons = None
    _supported_formats = ('.png')

    def __init__(self):
        self.icons = previews.new()

        icons_dir = path.normpath(path.join(path.dirname(__file__), "../icons"))
        for icon_file in sorted(listdir(icons_dir)):
            name_tokens = path.splitext(icon_file)
            filepath = path.join(icons_dir, icon_file)
            if name_tokens[1] in self._supported_formats:
                self.icons.load(name_tokens[0], filepath, 'IMAGE')
            else:
                print(f"Error: Unsupported icon format '{name_tokens[1]}': {filepath}")

    def unregister(self):
        """Remove the icon previews from Blender"""
        previews.remove(self.icons)
        self.icons = None


def get_icon(name):
    """Get an internal Blender icon ID from an icon name."""
    try:
        return __icon_manager__.icons[name].icon_id
    except KeyError:
        print(f"Error: Failed to find icon named '{name}'!")
        return None


class EZUE4Menu(Menu):
    """A menu for any registered functionality that should be accessible in any context."""
    bl_idname = "TOPBAR_MT_EZUE4"
    bl_label = " EZ-UE4"

    def draw(self, context):
        """Draw the menu."""


def menu_draw(self, context):
    """Draw the addon menus."""
    self.layout.menu(EZUE4Menu.bl_idname, text=EZUE4Menu.bl_label, icon_value=get_icon('unreal'))

class PieSave(Menu):
    bl_idname = "PIESAVE_MT_EZUE4"
    bl_label = "EZ-Export/Import"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()

        # 4 - LEFT
        pie.operator("wm.open_mainfile", text="Open...", icon_value=get_icon('open'))

        # 6 - RIGHT
        pie.operator("machin3.save", text="Save", icon_value=get_icon('save'))

        # 2 - BOTTOM
        pie.operator("wm.save_as_mainfile", text="Save As..", icon_value=get_icon('save_as'))

        # 8 - TOP
        box = pie.split()
        # box = pie.box().split()

        column = box.column()
        b = column.box()
        self.draw_right_column(b)

        b = column.box()
        self.draw_center_column_top(context, b)

        b = column.box()
        self.draw_center_column_bottom(b)


        # 7 - TOP - LEFT
        pie.separator()

        # 9 - TOP - RIGHT
        pie.separator()


    def draw_center_column_top(self, context, layout):
        column = layout.column(align=True)

        row = column.split(factor=0.25, align=True)
        row.label(text="OBJ")
        r = row.row(align=True)
        r.operator("import_scene.obj", text="Import", icon_value=get_icon('import'))
        r.operator("export_scene.obj", text="Export", icon_value=get_icon('export')).use_selection = True if context.selected_objects else False

        row = column.split(factor=0.25, align=True)
        row.label(text="FBX")
        r = row.row(align=True)
        r.operator("import_scene.fbx", text="Import", icon_value=get_icon('import'))
        op = r.operator("export_scene.fbx", text="Export", icon_value=get_icon('export'))
        op.use_selection = True if context.selected_objects else False
        op.apply_scale_options='FBX_SCALE_ALL'

    def draw_center_column_bottom(self, layout):
        column = layout.column(align=True)

        row = column.split(factor=0.5, align=True)
        row.scale_y = 1
        row.scale_x = 1
        
        export_objects = find_exportable_armatures()
        if export_objects:
            collection_text = f"Export Armatures ({len(export_objects)})"
            row.operator(AnimationExporter.bl_idname, text=collection_text, icon='OUTLINER_OB_ARMATURE')
        else:
            row.label(text="No Export Armatures", icon='OUTLINER_OB_ARMATURE')
        

        export_objects = find_exportable_collections()
        collection_text="No Export Collections in scene!"
        if export_objects:
            collection_text = f"Export Collections ({len(export_objects)})"
            row.operator(CollectionExporter.bl_idname, text=collection_text, icon='OUTLINER_OB_GROUP_INSTANCE')
        else:
            row.label(text="No Export Collections", icon='OUTLINER_OB_GROUP_INSTANCE')

    def draw_right_column(self, layout):
        column = layout.column(align=True)

        row = column.split(factor=0.25, align=True)
        row.label(text="Blender")
        row = row.split(factor=0.5, align=True)
        row.operator("wm.append", text="Append", icon_value=get_icon('append'))
        row.operator("wm.link", text="Link", icon_value=get_icon('link'))

__classes__ = (
    EZUE4Menu,
    PieSave,
)


def register():
    """Load the icons, register the menus and add them to the Blender UI."""
    global __icon_manager__ 
    if __icon_manager__ is None:
        __icon_manager__ = IconManager()

    for cls in __classes__:
        register_class(cls)


def unregister():
    """Remove the menus and Load the icons, register the menus and add them to the Blender UI."""
    for cls in reversed(__classes__):
        unregister_class(cls)

    global __icon_manager__ 
    __icon_manager__.unregister()
    __icon_manager__ = None
