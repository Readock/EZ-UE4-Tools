"""Operators for help and documentation about the Addon."""


import webbrowser
import bpy


class AddonDocumentation(bpy.types.Operator):
    """Open the addon's online documentation in a web browser."""

    bl_label = "Documentation"
    bl_idname = "screen.ezue4_documentation"
    bl_description = "Open help documentation for the Addon"

    _help_url = "https://github.com/"

    def execute(self, context):
        """Open the default web browser to the help URL."""
        webbrowser.open(self._help_url)
        return {'FINISHED'}


def menu_draw(self, context):
    """Create the menu item."""
    self.layout.operator(AddonDocumentation.bl_idname, icon="URL")


REGISTER_CLASSES = (
    AddonDocumentation,
)
