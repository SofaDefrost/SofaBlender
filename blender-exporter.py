import Sofa
import SofaRuntime
import importlib
import hashlib
import os
import sys
import signal
try:
    import orjson as json
except:
    print("Unable to load orjson, fallback to 'json' python implementation (slower)")
    import json
import shutil
import time

import argparse

def get_hash_digest(value):
    m = hashlib.md5()
    m.update(value.encode())
    return m.hexdigest()

def get_filepath(value, frame, basedir):
    md5 = get_hash_digest(value)
    outfilename = f"{md5}_{frame}.json"

    return os.path.join(basedir, outfilename)

def save_object(object):
    base_data = {
        "name" : object.name.value,
        "path" : str(object.linkpath),
        "class" : object.getClassName(),
        "type" : object.getTemplateName()
    }
    if object.getClassName() == "BlenderMaterial":
        base_data["blend_file"] = object.getData("blend_file").value
        base_data["material_name"] = object.getData("material_name").value
        base_data["target_path"] = object.getData("target_path").value

    if object.getClassName() == "OglModel":
        material_data = {}

        material_fields = ["material", "diffuse", "specular", "ambient", "emissive",
                           "shininess", "transparency", "texture"]

        for field in material_fields:
            if field in object.__data__:
                material_data[field] = object.getData(field).value

        if "material" in material_data and isinstance(material_data["material"], str):
            material_data = parse_sofa_material_string(material_data["material"])

        if material_data:
            base_data["material"] = material_data

    return base_data

def parse_sofa_material_string(mat_str):
    """
    Parses a string containing the material information of a basic material from Sofa
    This is used as a fallback when there is no BlenderMaterial, as such it contains less information than a full PBR material

    e.g. : We have "MyMaterial Material Diffuse 1 1.0 0.5 0.0 1.0 Shininess 128.0 1.0" as input
           We return {'name': 'MyMaterial', 'diffuse': [1.0, 0.5, 0.0, 1.0], 'shininess': [128.0, 1.0]} as a python dictionnary, ready to be exported in JSON format
    """
    
    parts = mat_str.split()
    result = {}

    if not parts:
        return result
    result['name'] = parts[0]                   # We assume the first token to be the Material name
    i = 1

    # This map contains a tuple for each key : (<output dictionnary key>, <the number of floats to read>)
    prop_map = {
        "Diffuse 1": ("diffuse", 4),            # [R, G, B, A]
        "Ambient 1": ("ambient", 4),            # [R, G, B, A]
        "Specular 1": ("specular", 4),          # [R, G, B, A]
        "Emissive": ("emissive", 4),            # [R, G, B, A]
        "Shininess": ("shininess", 2),          # [value, exponent]
        "Transparency": ("transparency", 1)
    }

    # The actual parser logic
    while i < len(parts):
        matched = False

        if i + 1 < len(parts):
            key = f"{parts[i]} {parts[i+1]}"
            if key in prop_map:
                out_key, n_vals = prop_map[key]                              # We output the key name and the number of floats in variables
                vals = [float(parts[i + 2 + j]) for j in range(n_vals)]      # List comprehension to convert the next 'n_vals' tokens into floats
                result[out_key] = vals                                       
                i += 2 + n_vals                                              # We advance the index past the 2 words of the key + the data values read
                matched = True
        if not matched:                                                      # If our key doesn't exist in the map, it means we have a 1-word key
            if parts[i] in prop_map:
                out_key, n_vals = prop_map[parts[i]]
                vals = [float(parts[i+1+j]) for j in range(n_vals)]          # List comprehension to convert the next 'n_vals' token into floats
                result[out_key] = vals                                       
                i += 1 + n_vals                                              # We advance the index past the only word of the key + the data values read
                matched = True
        if not matched:                                                      # If we don't match with a key from 'prop_map', then we skip this token and continue
            i += 1

    return result


def save_node(node):
    n = {
        "name" : node.name.value,
        "path" : str(node.linkpath),
        "class" : "Node",
        "children" : [],
        "objects" : []
    }
    for child in node.children:
        n["children"].append(save_node(child))

    for object in node.objects:
        n["objects"].append(save_object(object))

    return n

def save_config(root, basedir):
    destfile = os.path.join(basedir, "scene.json")
    with open(destfile, "wb") as w:
        w.write(json.dumps(save_node(root)))

def save_sofa_state(frame, object_rule, basedir):
    object, datafields = object_rule
    fullpathname = get_filepath(str(object.linkpath), frame, basedir)

    if datafields == "*":
        vertices = object.position.value
        edges = []
        triangles = []
        quads = []

        if "vertices" in object.__data__ and len(object.vertices) != 0:
            vertices = object.vertices.value

        if "edges" in object.__data__:
            edges = object.edges.value

        if "triangles" in object.__data__:
            triangles = object.triangles.value

        if "quads" in object.__data__:
            quads = object.quads.value

        with open(fullpathname, "wb") as f:
            f.write(json.dumps({
              "frame": frame,
              "position": vertices.tolist() if hasattr(vertices, "tolist") else vertices,
              "edges": edges.tolist() if hasattr(edges, "tolist") else edges,
              "triangles": triangles.tolist() if hasattr(triangles, "tolist") else triangles,
              "quads": quads.tolist() if hasattr(quads, "tolist") else quads
            }))
    else:
        tmp = {"frame" : frame}
        datafields = datafields.replace(" ","")
        for datafield in datafields.split(','):
            if datafield in object.__data__:
                tmp[datafield] = object.getData(datafield).value
            else:
                raise Exception("Unable to find data field named ", datafield, " in ", object.getPathName())

        with open(fullpathname, "wb") as f:
            f.write(json.dumps(tmp, option=json.OPT_SERIALIZE_NUMPY))

def get_all_objects(selection_rule, node, out):
    typename, pathname, datafields = selection_rule
    for object in node.objects:
        if object.getClassName() == typename:
            if pathname == "*" or object.getPathName() == pathname:
                if object.getPathName() not in out:
                    out[object.getPathName()] = (object, datafields)
    for child in node.children:
        get_all_objects(selection_rule, child, out)
    return out

def bake_sofa_simulation(sofa_root, objects_to_bake, current_frame, basedir):
    for object in objects_to_bake:
        save_sofa_state(current_frame, object, basedir)

    print("    - sofa simulation terminated at {}".format({sofa_root.time.value}))

class BlenderExporter(Sofa.Core.Controller):
    def __init__(self, *args, **kwargs):
        Sofa.Core.Controller.__init__(self, *args, **kwargs)
        self.objects = kwargs.get("objects", [])
        self.root = kwargs.get("root", [])
        self.delta_time = 1.0 / kwargs.get("fps", 24)
        self.timing = kwargs.get("timing", "simulation")
        self.current_frame = 0
        self.current_time = 0
        self.time_last_frame_was_emitted = 0
        self.base_dir = kwargs.get("base_dir", [])
        self.start_time = time.time()

        if os.path.exists(self.base_dir):
            shutil.rmtree(self.base_dir)

        if not os.path.exists(self.base_dir):
            os.mkdir(self.base_dir)
        save_config(self.root, self.base_dir)

    def dump_at_time(self, dt):
        if self.current_time >= self.time_last_frame_was_emitted + self.delta_time :
            print("Saving animation step ", self.current_time)
            bake_sofa_simulation(self.root, self.objects, self.current_frame, self.base_dir)
            self.current_frame +=1
            self.time_last_frame_was_emitted += self.delta_time
        self.current_time += dt

    def onAnimateEndEvent(self, params):
        dt = params["dt"]
        if self.timing == "simulation":
            self.dump_at_time(dt)
        else :
            self.dump_at_time(time.time() - self.start_time - self.current_time)

def load_in(root, file):
    oroot = Sofa.Simulation.load(file)

    chlds = list(oroot.children)
    for child in chlds:
        root.addChild(child)

    objs = list(oroot.objects)
    for object in objs:
        oroot.removeObject(object)
        root.addObject(object)

    for child in chlds:
        oroot.removeChild(child)

    for name in oroot.__data__:
        root.getData(name).value = oroot.getData(name).value

    return root

class CommandLineParse(object):
    def __init__(self):
        self.args = {}

    def add_argument(self, name, default_value, help_message):
        self.args[name] = [default_value, help_message]

    def print_help(self):
        print("USAGE: runSofa.py blender-exporter.py --argv filename=sofa_scene.scn [--argv option_name=value] ...")
        print("")
        print("Available options:")
        for name, (value, help) in self.args.items():
            print(" "+name+"="+repr(value)+"     "+help)

    def parse(self, args):
        for arg in args:
            name, value = arg.split("=")
            if name not in self.args:
                print("Invalid argument: "+name)
                self.print_help()
                os.kill(os.getpid(),signal.SIGKILL)
            self.args[name][0] = value

    def __getitem__(self, key):
        return self.args[key][0]

def createScene(root):
    parser = CommandLineParse()
    parser.add_argument("filename", "", "The file name for the scene to export")
    parser.add_argument("fps", 24, "Number of frame per second")
    parser.add_argument("timing", "simulation", "Indicate the time used, it can either 'simulation' time or 'realtime' ")
    parser.add_argument("basedir", "sofa_export", "The directory to bake the simulation into")
    parser.add_argument("selection", None, "The filtering used to dump that scene, use this to select the object/field to export")
    parser.parse(sys.argv[1:])

    print("TEST EXPORTER... ", sys.argv)

    sourcefile =  parser["filename"]
    fps = float(parser["fps"])
    timing = parser["timing"]
    selection_file = parser["selection"]

    filename, ext = os.path.splitext(sourcefile)
    if ext in [".py", ".pyscn"]:
        sys.path.append(os.path.dirname(filename))
        SofaRuntime.SofaRuntime.DataRepository.addLastPath(os.path.dirname(filename))
        m = importlib.import_module(os.path.basename(filename))
        m.createScene(root)
    else:
        load_in(root, sourcefile)

    if selection_file is None:
        selection_rules = [{
            "classname" : "MechanicalObject",
            "pathname" : "*",
            "datafield" : "*"
            },{
            "classname" : "OglModel",
            "pathname" : "*",
            "datafield" : "*"
            }]
    else:
        selection_rules = json.loads(open(selection_file, "rt").read())

    objects = {}
    for rule in selection_rules:
        objects = get_all_objects(rule.values(), root, objects)

    print("Exporting ")
    for key, object_sel in objects.items():
        object, datafields = object_sel
        print("  object ", object.getPathName())

    root.addObject(BlenderExporter(name="BlenderExporter", root=root, objects=objects.values(),
                                                           fps=fps, timing=parser["timing"],
                                                           base_dir=parser["basedir"]))
