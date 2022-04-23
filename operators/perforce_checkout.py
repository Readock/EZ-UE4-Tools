"""Open the addon's output path in explorer"""

import bpy
from ..core import preferences
from ..utils import addon
import os
import subprocess

FILEBROWSER_PATH = os.path.join(os.getenv('WINDIR'), 'explorer.exe')

class PerforceCheckout(bpy.types.Operator):
    """Open the addon's output path in explorer"""

    bl_label = "P4 Checkout"
    bl_idname = "screen.ezue4_p4_checkout"
    bl_description = "Checks out the blend file"
    custom_icon = 'UNLOCKED'

    def execute(self, context):
        """Checks out the blend file"""
        filepath = addon.get_blend_file_path()
        subprocess.run(["p4", "edit", filepath])
        return {'FINISHED'}


REGISTER_CLASSES = (
    PerforceCheckout,
)
