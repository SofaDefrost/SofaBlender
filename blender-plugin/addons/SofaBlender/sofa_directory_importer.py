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

        position = []
        orientation = None 
        extra_vertex_data = []
        topology = {
            "edges" : [],
            "triangles" : [],
            "quads" : []
        }

        for name, values in data.items():
            if name == "frame": 
                continue 
            elif name == "position" and len(values) > 0:
                if len(values[0]) == 1:
                    position = [[a[0], 0, 0] for a in values]
                elif len(values[0]) == 2:
                    position = [[a[0], a[1], 0] for a in values]
                elif len(values[0]) == 3:
                    position = [[a[0], a[1], a[2]] for a in values]
                elif len(values[0]) == 7:
                    position = [[a[0],a[1],a[2]] for a in values]
                    orientation = [[a[3],a[4],a[5],a[6]] for a in values] 
            elif name == "edges":
                topology["edges"] = values
            elif name == "triangles":
                topology["triangles"] = values
            elif name == "quads":
                topology["quads"] = values
            else: 
                # https://docs.blender.org/api/current/bpy_types_enum_items/attribute_type_items.html#rna-enum-attribute-type-items
                if isinstance(values[0], list): 
                    if len(values[0]) == 2:
                        extra_vertex_data.append({"name" : name,
                                                  "type" : "FLOAT2",
                                                  "domain" : "POINT",
                                                  "data" : values
                                                  })
                    elif len(values[0]) == 3:
                        extra_vertex_data.append({"name" : name,
                                                  "type" : "FLOAT_VECTOR",
                                                  "domain" : "POINT",
                                                  "data" : values
                                                  })
                    elif len(values[0]) == 4:
                        extra_vertex_data.append({"name" : name,
                                                  "type" : "FLOAT_COLOR",
                                                  "domain" : "POINT",
                                                  "data" : values
                                                  })    
                    else:
                        print("Unsupported type structure. Please report: ", name, values[0])
                else:
                    extra_vertex_data.append({"name" : name,
                                              "type" : "FLOAT",
                                              "domain" : "POINT",
                                              "data" : values
                                              })

        if len(position) == 0:
            max_idx = -1
            for t in ["edges","triangles","quads"]:
                for indices in topology[t]:            
                    for index in indices:
                        if index > max_idx:
                            max_idx = index              
            if max_idx >= 0:
                position = [[0,0,0]]*(max_idx+1)

        mesh.data.from_pydata(position, topology["edges"], topology["triangles"]+topology["quads"])
        mesh.data.validate()
        mesh.data.update(calc_edges=True)

        if orientation:
            mesh.data.attributes.new(name="qx", type='FLOAT', domain='POINT')
            mesh.data.attributes.new(name="qy", type='FLOAT', domain='POINT')
            mesh.data.attributes.new(name="qz", type='FLOAT', domain='POINT')
            mesh.data.attributes.new(name="qw", type='FLOAT', domain='POINT')
            
            for i in range(4):
                cname = ["qx, qy, qz, qw"][i]
                attribute = mesh.data.attributes[cname].data
                for j in range(len(attribute)):
                    t = attribute[j]
                    t.value =  orientation[j][i]

        for field in extra_vertex_data:
            mesh.data.attributes.new(name=field["name"], type=field["type"], domain=field["domain"])

            num_vertices = len(mesh.data.vertices)            
            if num_vertices == 0:
                mesh.data.from_pydata([[0,0,0]]*len(field["data"]), [], [])
                mesh.data.validate()
                mesh.data.update()
                num_vertices = len(field["data"])

            sofa_data = field["data"]
            attribute = mesh.data.attributes[field["name"]].data
            for i in range(num_vertices):
                t = attribute[i]

                if field["type"] == "FLOAT_COLOR":      
                    t.color.foreach_set(sofa_data[i])
                elif field["type"] == "FLOAT_VECTOR":      
                    t.vector.xyz = sofa_data[i]
                #elif field["type"] == "FLOAT2":
                #    t.value.xy = sofa_data[i]
                elif field["type"] == "FLOAT":
                    t.value = sofa_data[i]
                else:
                    print("INVALID DATA TYPE", sofa_data[i])
        
def load_baked_objects_at_frame(frame, blender_root, cache, basedir):
    for object in cache.values():
        load_baked_object_at_frame(frame, object, basedir)
    
