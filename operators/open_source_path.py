"""Open the addon's output path in explorer"""

import bpy
from ..core import get_source_path
import os
import subprocess

FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')

class OpenSourcePath(bpy.types.Operator):
    """Open the addon's output path in explorer"""

    bl_label = "Open Output Folder"
    bl_idname = "screen.ezue4_open_source_path"
    bl_description = "Open the explorer at the source path"

    def execute(self, context):
        """Open the default web browser to the help URL."""
        self.explore(get_source_path())
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
    self.layout.operator(OpenSourcePath.bl_idname, icon="FILE_FOLDER")
# find icons here https://gist.github.com/eliemichel/251731e6cc711340dfefe90fe7e38ac9

REGISTER_CLASSES = (
    OpenSourcePath,
)
