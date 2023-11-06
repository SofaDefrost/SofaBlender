bl_info = {
    "name": "SOFANodeEditor",
    "description": "A plugin to design SOFA simulations in blender.",
    "author": "Damien Marchal",
    "blender": (3, 4, 0),
    "category": "Object",
}

import bpy
from bpy.props import BoolProperty, StringProperty, IntProperty
from bpy.types import AddonPreferences, Operator

from . import (
    panels,
    operators,
    sofanodes
)

class SOFANodeEditorSettings(AddonPreferences):
    bl_idname = __name__

def register():
    bpy.utils.register_class(SOFANodeEditorSettings)
    panels.register()
    operators.register()
    sofanodes.register()

def unregister():
    bpy.utils.unregister_class(SOFANodeEditorSettings)
    panels.unregister()
    operators.unregister()
    sofanodes.unregister()

