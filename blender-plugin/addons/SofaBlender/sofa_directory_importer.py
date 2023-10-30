import bpy 
try:
    import orjson as json
except:
    print("Unable to import orsjson, fallbacking to the python 'json' library. ")
    import json
import hashlib
import os
from math import sin, cos, atan2

def sofa_get_new_path(old_pathname):
    return old_pathname[1:].replace("/",".")

def load_sofa_object(object):
    sname = object["name"]
    sclass = object["class"]
    
    bname = "{} ({})".format(sname, sclass)
    bmesh = bpy.data.meshes.new(sname)    
    bobject = bpy.data.objects.new(bname, bmesh) 
    bobject.name = bname
    bobject["sofa_name"] = sname
    bobject["sofa_type"] = sclass
    bobject["sofa_pathname"] = object["path"]
    
    return bobject

def get_hash_digest(value):
    m = hashlib.md5()
    m.update(value.encode())
    return m.hexdigest()

def get_filepath(value, frame, basedir):
    md5 = get_hash_digest(value)
    outfilename = f"{md5}_{frame}.json"
    
    if not os.path.exists(basedir):
        os.mkdir(basedir)
    
    return os.path.join(basedir, outfilename)
    
def load_sofa_node(node, blendernode, cache):
    name = node["name"]
    path = node["path"]
    
    if path in cache:
        new_node = cache[path]
    else:          
        new_node = bpy.data.collections.new(name)
        new_node.name = name
        new_node["sofa_name"] = node["name"]
        new_node["sofa_pathname"] = node["path"]
        blendernode.children.link(new_node)
    
    for child in node["children"]:
        load_sofa_node(child, new_node, cache)
    
    for object in node["objects"]:
        if object["path"] not in cache:
            child_object = load_sofa_object(object)
            new_node.objects.link(child_object)
    return new_node

def blender_sofa_tree(collection, out):
    if not collection:
        return out
    
    if "sofa_pathname" in collection:
        out[collection["sofa_pathname"]] = collection
    
    for child in collection.children:
        if "sofa_pathname" in child:
            out[child["sofa_pathname"]] = child
            blender_sofa_tree(child, out) 
        
    for object in collection.objects:
        if "sofa_pathname" in object:
            out[object["sofa_pathname"]] = object
            
    return out

def remove_collection(collection):
    if not collection:
        return

    # Will collect meshes from delete objects
    meshes = set()

    # Get objects in the collection if they are meshes
    for obj in [o for o in collection.objects if o.type == 'MESH']:
        # Store the internal mesh
        meshes.add( obj.data )

        # Delete the object
        bpy.data.objects.remove( obj )

    # Look at meshes that are orphean after objects removal
    for mesh in [m for m in meshes if m.users == 0]:
        # Delete the meshes
        bpy.data.meshes.remove( mesh )

    for child in collection.children:
        remove_collection(child)
        bpy.data.collections.remove(child) 

def remove_baked_simulation():
    name = "SOFA Collections"
    collection = bpy.data.collections.get(name)
    remove_collection(collection)

def load_bake_directory(pathdir="__sofa_cache__"):
    scenefilename = os.path.join(pathdir, "scene.json")
    directoryname = os.path.basename(os.path.normpath(pathdir))

    name = "SOFA Collections"
    blenderroot = bpy.data.collections.get(name)
    if not blenderroot:
        blenderroot = bpy.data.collections.new(name)
    
    if not bpy.context.scene.collection.children.get(name):
        bpy.context.scene.collection.children.link(blenderroot)

    sceneroot = blenderroot.children.get(directoryname)
    if not sceneroot:
        sceneroot = bpy.data.collections.new(directoryname)
        blenderroot.children.link(sceneroot)

    rootnode = json.loads(open(scenefilename, "rb").read())
    
    cache = blender_sofa_tree(sceneroot, {})
    load_sofa_node(rootnode, sceneroot, cache)
    
    cache = blender_sofa_tree(sceneroot, {})
    load_baked_objects_at_frame(0, sceneroot, cache, pathdir)

def load_baked_object_at_frame(frame, mesh, basedir):
    if "sofa_pathname" not in mesh:
        raise Exception("Missing sofa_pathname property in a blender object")
    
    fullpathname = get_filepath(mesh["sofa_pathname"], frame, basedir)
    if not os.path.exists(fullpathname):
        return
        
    with open(fullpathname, "rb") as f:
        data = json.loads(f.read())    
        mesh.data.clear_geometry()
            
        if len(data["position"][0]) != 3:
            data["position"] = [[a[0],a[1],a[2]] for a in data["position"] ]

        if "edges" in data:
            mesh.data.from_pydata(data["position"], data["edges"], data["triangles"]+data["quads"])
            mesh.data.validate()
            mesh.data.update(calc_edges=True)
        else:
            mesh.data.from_pydata(data["position"], [], [])
            mesh.data.validate()
            for name in data:
                if name != "position" and name != "frame":
                    if not mesh.data.attributes.get(name):
                        mesh.data.attributes.new(name=name, type='FLOAT_VECTOR', domain='POINT')
                        #mesh.data.attributes.new(name=’myAttributeFloat’, type=’FLOAT’, domain=’POINT’)
        
                    sofa_data = data[name]
                    attribute = mesh.data.attributes[name].data
                    for i in range(len(attribute)):
                        t = attribute[i]
                        t.vector.xyz = sofa_data[i]
        
def load_baked_objects_at_frame(frame, blender_root, cache, basedir):
    for object in cache.values():
        load_baked_object_at_frame(frame, object, basedir)
    
