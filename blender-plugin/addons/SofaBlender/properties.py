import bpy

class SofaSceneSimulation(bpy.types.PropertyGroup):
    sofa_name: bpy.props.StringProperty()
    sofa_path: bpy.props.StringProperty()

def register():
    bpy.utils.register_class(SofaSceneSimulation)

    # Groups of properties to attach to blender object
    bpy.types.Scene.sofa_scene_collection = bpy.props.CollectionProperty(type=SofaSceneSimulation)    
    bpy.types.Object.sofa_type = bpy.props.StringProperty()
    bpy.types.Object.sofa_name = bpy.props.StringProperty()
    bpy.types.Object.sofa_pathname = bpy.props.StringProperty()
    bpy.types.Collection.sofa_type = bpy.props.StringProperty()
    bpy.types.Collection.sofa_name = bpy.props.StringProperty()
    bpy.types.Collection.sofa_pathname = bpy.props.StringProperty()


def unregister():
    bpy.utils.unregister_class(SofaSceneSimulation)
