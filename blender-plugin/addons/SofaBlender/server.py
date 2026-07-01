bl_info = {
    "name": "SOFA Server",
    "description": "A server receiving data from SOFA.",
    "author": "Alexandre Bilger",
    "blender": (3, 4, 0),
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

sofa_collection_name = 'SOFA Collection'

def process_object(object_data, collection, iteration):
    object_name = object_data["name"]

    if "position" in object_data and len(object_data["position"]) > 0:
        if "faces" in object_data and len(object_data["faces"]) > 0:

            if collection.objects.find(object_name) == -1:
                new_mesh = bpy.data.meshes.new(object_name)
                new_mesh.clear_geometry()

                new_mesh.from_pydata(object_data["position"], {}, object_data["faces"])
                new_mesh.update()

                new_object = bpy.data.objects.new(object_name, new_mesh)
                collection.objects.link(new_object)
            else:
                print(object_name)
                if object_name in collection.objects:
                    obj = collection.objects[object_name]

                    obj.data.clear_geometry()
                    obj.data.from_pydata(object_data["position"], {}, object_data["faces"])
                    obj.data.update()

                    # for v in obj.data.vertices:
                    #     v.keyframe_insert("co", frame=iteration)


def process_node(node_data, collection, iteration):

    if "node_name" not in node_data:
        print("No name for this node")
        return

    node_name = node_data["node_name"]
    if collection.children.find(node_name) == -1:
        new_sofa_collection = bpy.data.collections.new(node_name)
        collection.children.link(new_sofa_collection)

    node_collection = collection.children[node_name]

    if "objects" in node_data:
        for obj in node_data["objects"]:
            process_object(obj, node_collection, iteration)

    if "children" in node_data:
        for child in node_data["children"]:
            process_node(child, node_collection, iteration)


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
        print("iteration #", iteration)

        bpy.context.scene.frame_start = 0
        bpy.context.scene.frame_end = iteration

        c = sofa_collection_name

        if bpy.data.collections.find(c) == -1:
            print('[SOFABlender] Creating SOFA Collection')
            new_sofa_collection = bpy.data.collections.new(c)
            bpy.context.scene.collection.children.link(new_sofa_collection)

        process_node(data, bpy.data.collections[c], iteration)

    except json.JSONDecodeError as e:
        print(f"[SOFABlender] Error decoding JSON: {e} {json_data[:100]}...")
        raise e


header_tag = "<SOFABlender>"
footer_tag = "</SOFABlender>"


# Function to handle incoming client connections
def handle_client(client_socket):
    remainder = ""
    while True:
        try:
            # Receive data from the client
            data = client_socket.recv(4096)
            if not data:
                break

            s = remainder + data.decode()
            remainder = ""
            if header_tag in s:

                index_header = s.find(header_tag)
                all_data = s[index_header + len(header_tag):]

                while True:
                    data = client_socket.recv(4096)
                    s = data.decode()
                    all_data += s

                    if footer_tag in s:
                        index_footer = all_data.find(footer_tag)
                        all_data = all_data[:index_footer]
                        remainder = all_data[index_footer + len(footer_tag):]

                        try:
                            read_json(all_data)
                        except json.JSONDecodeError:
                            print("[SOFABlender] Skipping iteration", all_data[:100])

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
