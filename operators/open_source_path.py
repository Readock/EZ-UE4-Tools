"""Open the addon's output path in explorer"""

import bpy
from ..core import preferences
import os
import subprocess

FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')

class OpenSourcePath(bpy.types.Operator):
    """Open the addon's output path in explorer"""

    bl_label = "Open Output Folder"
    bl_idname = "screen.ezue4_open_source_path"
    bl_description = "Open the explorer at the source path"
    custom_icon = 'FILE_FOLDER'

    def execute(self, context):
        """Open the default web browser to the help URL."""
        self.explore(preferences.source_path())
        return {'FINISHED'}

    
    def explore(self, path):
        # explorer would choke on forward slashes
        path = os.path.normpath(path)

        if os.path.isdir(path):
            subprocess.run([FILEBROWSER_PATH, path])
        elif os.path.isfile(path):
            subprocess.run([FILEBROWSER_PATH, '/select,', os.path.normpath(path)])


def menu_draw(self, context):
    """Create the menu item."""
    self.layout.operator(OpenSourcePath.bl_idname, icon=OpenSourcePath.custom_icon)
# find icons here https://gist.github.com/eliemichel/251731e6cc711340dfefe90fe7e38ac9
# or here https://media.blenderartists.org/uploads/default/original/4X/d/0/a/d0a3a276bee9db75153f7a67613f307654a7a063.png

REGISTER_CLASSES = (
    OpenSourcePath,
)
