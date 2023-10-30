import bpy
from bpy.types import Operator
from bpy.props import StringProperty, BoolProperty

import json
import sys
import os

from . import (sofa_directory_importer)
 
class RemoveSofaSimulation(Operator):
    """Blender operator that remove all the stored sofa simulation"""
    bl_idname = "scene.remove_sofa_simulations"
    bl_label = "Detach all simulations"
    bl_options = {'REGISTER'}

    def execute(self, context):
        sofa_scene_collection = bpy.context.scene.sofa_scene_collection    
        sofa_scene_collection.clear()
        sofa_directory_importer.remove_baked_simulation()            
        return {'FINISHED'}

class ImportSofaSimulation(Operator):
    """Create collection for all characters"""
    bl_idname = "scene.import_sofa_simulations"
    bl_label = "Import all simulations"
    bl_options = {'REGISTER'}

    def execute(self, context):        
        blend_dir = os.path.dirname(bpy.data.filepath)
        if blend_dir not in sys.path:
            sys.path.append(blend_dir)
 
        sofa_scene_collection = bpy.context.scene.sofa_scene_collection
        for item in sofa_scene_collection:            
            sofa_directory_importer.load_bake_directory(item.sofa_path)    
            
        return {'FINISHED'}

class SelectSofaDirectory(Operator):
    """Select a directory to import"""
    bl_idname = "scene.add_sofa_simulation"
    bl_label = "Add Sofa directory ..."
    bl_options = {'REGISTER'}

    # Define this to tell 'fileselect_add' that we want a directoy
    directory: StringProperty(
        name="Outdir Path",
        description="Where I will save my stuff"
        # subtype='DIR_PATH' is not needed to specify the selection mode.
        # But this will be anyway a directory path.
        )

    # Filters folders
    filter_folder: BoolProperty(
        default=True,
        options={"HIDDEN"}
        )

    def execute(self, context):
        sofa_scene_collection = bpy.context.scene.sofa_scene_collection
        item  = sofa_scene_collection.add()
        
        d = json.load(open(self.directory+"/scene.json"))
        dname = os.path.basename(os.path.normpath(self.directory))
        item.sofa_name = dname
        item.sofa_path = str(self.directory)
            
        return {'FINISHED'}

    def invoke(self, context, event):
        # Open browser, take reference to 'self' read the path to selected
        # file, put path in predetermined self fields.
        # See: https://docs.blender.org/api/current/bpy.types.WindowManager.html#bpy.types.WindowManager.fileselect_add
        context.window_manager.fileselect_add(self)
        
        # Tells Blender to hang on for the slow user input
        return {'RUNNING_MODAL'}

def register():
    bpy.utils.register_class(SelectSofaDirectory)
    bpy.utils.register_class(RemoveSofaSimulation)  
    bpy.utils.register_class(ImportSofaSimulation)  

def unregister():
    bpy.utils.unregister_class(SelectSofaDirectory)
    bpy.utils.unregister_class(RemoveSofaSimulation)
    bpy.utils.unregister_class(ImportSofaSimulation)

