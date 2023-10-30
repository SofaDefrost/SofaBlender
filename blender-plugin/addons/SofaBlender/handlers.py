import bpy
from bpy.app.handlers import persistent
from . import (sofa_directory_importer)

@persistent
def load_baked_sofa_simulation_at_frame(scene, _):
    frame = scene.frame_current

    if len(bpy.context.scene.sofa_scene_collection):
        print("Load sofa simulation's data for frame:", frame)
    
    for item in bpy.context.scene.sofa_scene_collection:
        name=item.sofa_name    
        path=item.sofa_path
        blender_root = bpy.data.collections.get(name)

        cache = sofa_directory_importer.blender_sofa_tree(blender_root, {})        
        sofa_directory_importer.load_baked_objects_at_frame(frame, blender_root, cache, path)

def register():
    listeners = bpy.app.handlers.frame_change_pre
    listeners.clear()  
    listeners.append(load_baked_sofa_simulation_at_frame)

def unregister():
    listeners = bpy.app.handlers.frame_change_pre
    listeners.clear()  

