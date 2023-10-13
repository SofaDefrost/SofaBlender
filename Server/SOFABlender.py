bl_info = {
    "name": "SOFA Server",
    "description": "A server receiving data from SOFA.",
    "author": "Alexandre Bilger",
    "blender": (2, 80, 0),
    "category": "Object",
}

import bpy
from bpy.props import BoolProperty, StringProperty, IntProperty
from bpy.types import AddonPreferences, Operator


import socket
import threading
import json

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

is_server_started = False
is_server_connected = False


def read_json(json_data):
    # Find the index of the last '}'
    last_brace_index = json_data.rfind('}')

    # Check if '}' was found
    if last_brace_index != -1:
        # Slice the string to keep only the part before the last '}'
        json_data = json_data[:last_brace_index + 1]

    try:
        data = json.loads(json_data)
        iteration = data["iteration"]
        print(f"Iteration #{iteration}")

    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e} {json_data}")


# Function to handle incoming client connections
def handle_client(client_socket):
    while True:
        try:
            # Receive data from the client
            data = client_socket.recv(4096)
            if not data:
                break

            s = data.decode()
            all_data = s
            if "<SOFABlender>" in s:

                while True:
                    data = client_socket.recv(4096)
                    s = data.decode()
                    all_data += s
                    if "</SOFABlender>" in s:

                        all_data = all_data.replace('<SOFABlender>', '')
                        all_data = all_data.replace('</SOFABlender>', '')
                        read_json(all_data)

                        break

        except KeyboardInterrupt:
            global is_server_connected
            is_server_connected = False
            print("[SOFABlender] Server connection to client shutting down.")
            break


# Function to accept incoming connections
def accept_connections():
    while True:
        try:
            # Accept a client connection
            client_sock, addr = server_socket.accept()
            print(f"[SOFABlender] Accepted connection from {addr[0]}:{addr[1]}")

            # Create a new thread to handle the client
            client_handler = threading.Thread(target=handle_client, args=(client_sock,))
            client_handler.start()

            global is_server_connected
            is_server_connected = True

        except KeyboardInterrupt:
            global is_server_started
            is_server_started = False
            print("[SOFABlender] Server shutting down.")
            break


def start_server(host, port):
    global is_server_started
    if is_server_started:
        print("[SOFABlender] Server is already started")
        return False

    server_address = (host, port)
    server_socket.bind(server_address)

    # Listen for incoming connections
    server_socket.listen(1)

    print(f"[SOFABlender] Waiting for a connection on {host}:{port}...")

    # Create a thread for accepting connections
    connection_thread = threading.Thread(target=accept_connections)
    connection_thread.start()

    is_server_started = True

    return True


def stop_server():
    global is_server_started
    if not is_server_started:
        return False

    is_server_started = False
    server_socket.close()

    return True


class Start(Operator):
    bl_idname = "sofa_blender.start"
    bl_label = "Start SOFA server"

    def execute(self, context):
        addon_prefs = context.preferences.addons[__name__].preferences
        if not start_server(str(addon_prefs.host), int(addon_prefs.port)):
            self.report({"ERROR"}, "The server is already started.")
            return {"CANCELLED"}
        return {"FINISHED"}


class Stop(Operator):
    bl_idname = "sofa_blender.stop"
    bl_label = "Stop SOFA server"

    def execute(self, context):
        if not stop_server():
            self.report({"ERROR"}, "The server is not started.")
            return {"CANCELLED"}
        return {"FINISHED"}


class SOFABlenderSettings(AddonPreferences):
    bl_idname = __name__

    auto_start: BoolProperty(
        name="Start automatically",
        description="Automatically start the server when loading the add-on",
        default=True
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

        if is_server_started:
            col.operator(Stop.bl_idname, icon='QUIT', text="Stop server")
        else:
            col.operator(Start.bl_idname, icon='QUIT', text="Start server")


def shutdown():
    stop_server()


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
