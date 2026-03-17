import json
import os
from pathlib import Path
import bpy

def search_description_locations(filename):
    path = Path(os.getcwd())

    found_files = []
    for parent in list(reversed(path.parents)) + [path]:
        config_file = os.path.join(parent, filename)
        if os.path.exists(config_file):
            found_files.append(config_file)

    return found_files

def initialize_node2data():
    filenames = search_description_locations(".sofa_blender/component_descriptions.json")

    result = {}
    data_infos = {}
    
    for filename in filenames: 
        print(f"Loading SOFA field database from {filename}")
        nodes_description = json.load(open(filename,"r"))
    
        for object  in nodes_description:
            classname = object["className"]
            result[classname] = []

            selected_set = set() 
            for template, creator in object["creator"].items():    
                for data in creator["object"]["data"]:
                    if data["name"] not in selected_set:
                        selected_set.add(data["name"]) 
                        result[classname].append(
                            (data["name"], data["name"], f"({data['help']})")
                        )
                        uid = classname + "." + data["name"]
                        data_infos[uid ] = {
                            "name" : data["name"],
                            "help" : data["help"],
                            "type" : data["type"],
                            "group" : data["group"],
                            "default_value" : data["defaultValue"]
                        }
                for link in creator["object"]["link"]:
                    if link["name"] not in selected_set:
                        selected_set.add(link["name"]) 
                        result[classname].append(
                            (link["name"], link["name"], f"({link['help']})")
                        )
                        uid = classname + "." + link["name"]
                        data_infos[uid] = {
                            "name" : link["name"],
                            "help" : link["help"],
                            "type" : "link",
                            "group" : None,
                            "default_value" : None
                        }                     
    return result, data_infos 

node2data, sofa_data_infos = initialize_node2data()

def get_components():
    return node2data.keys()

def get_creator(class_name):
    return node2data.get(class_name, None)

def get_datatype(class_name, data_name):
    global sofa_data_infos 
    uid = class_name + "." + data_name

    if uid not in sofa_data_infos:
        print(f"WARNING: Unable to find real type for '{uid}' falling back to type 'string'")
        return "string"  
    
    return sofa_data_infos[uid]["type"]

def get_default_value(class_name, data_name):
    global sofa_data_infos 
    uid = class_name + "." + data_name

    if uid not in sofa_data_infos:
        print(f"WARNING: Unable to find real type for '{uid}' falling back to type 'string'")
        return "string"  
    
    type = sofa_data_infos[uid]["type"]
    if type in ["f","d"]:
        return float(sofa_data_infos[uid]["default_value"])
    elif type in ["I","i"]:
        return int(sofa_data_infos[uid]["default_value"])
    elif type == "bool":
        return bool(sofa_data_infos[uid]["default_value"])
    elif type == "string":
        return sofa_data_infos[uid]["default_value"]
    
    print(f"Type {uid} does not support default value ... please improve")
    return None 
