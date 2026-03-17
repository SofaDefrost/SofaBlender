#!/usr/bin python 
import os
import json

if not os.path.exists(".sofa_blender"):
    print("Create a new sofa blender project")    

    if not os.path.exists(".sofa_blender/components_descriptions.json"):
        pathname = ".sofa_blender/components_descriptions.json"
        with open(pathname,"w") as file:
            json.dumps(file, {})

    os.mkdir(".sofa_blender")
else:
    print("Current directory already contains a sofa blender project.")    
    
