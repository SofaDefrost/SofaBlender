bl_info = {
    "name": "SOFABlender",
    "description": "A plugin to import SOFA simulation.",
    "author": "Alexandre Bilger & Damien Marchal",
    "blender": (3, 4, 0),
    "category": "Object",
}

import bpy
from bpy.props import BoolProperty, StringProperty, IntProperty
from bpy.types import AddonPreferences, Operator

from . import (
    server 
)

class Start(Operator):
    bl_idname = "sofa_blender.start"
    bl_label = "Start SOFA server"

    def execute(self, context):
        addon_prefs = context.preferences.addons[__name__].preferences
        if not server.start_server(str(addon_prefs.host), int(addon_prefs.port)):
            self.report({"ERROR"}, "The server is already started.")
            return {"CANCELLED"}
        return {"FINISHED"}

class Stop(Operator):
    bl_idname = "sofa_blender.stop"
    bl_label = "Stop SOFA server"

    def execute(self, context):
        if not server.stop_server():
            self.report({"ERROR"}, "The server is not started.")
            return {"CANCELLED"}
        return {"FINISHED"}


class SOFABlenderSettings(AddonPreferences):
    bl_idname = __name__

    auto_start: BoolProperty(
        name="Start automatically",
        description="Automatically start the server when loading the add-on",
        default=False
    )

    host: StringProperty(
        name="Host",
        description="Listen on host:port",
        default="localhost"
    )

    port: IntProperty(
        name="Port",
        description="Listen on host:port",
        default=12345,
        min=0,
        max=65535,
        subtype="UNSIGNED"
    )

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        split = row.split(factor=0.3)

        col = split.column()
        col.prop(self, "host")
        col.prop(self, "port")
        col.separator()

        col.prop(self, "auto_start")

        if server.is_server_started:
            col.operator(Stop.bl_idname, icon='QUIT', text="Stop server")
        else:
            col.operator(Start.bl_idname, icon='QUIT', text="Start server")


def shutdown():
    server.stop_server()

def register():
    bpy.utils.register_class(SOFABlenderSettings)
    bpy.utils.register_class(Start)
    bpy.utils.register_class(Stop)

def unregister():
    shutdown()
    bpy.utils.unregister_class(SOFABlenderSettings)
    bpy.utils.unregister_class(Start)
    bpy.utils.unregister_class(Stop)

if __name__ == "__main__":
    register()
