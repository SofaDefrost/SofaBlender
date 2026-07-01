import bpy
import os

def export_to_sofa():
    "this function export the model from Blender to sofa"
    export_dir = os.path.join(os.path.dirname(bpy.data.filepath), "sofa_export")
    os.makedirs(export_dir, exist_ok=True)

    obj_path = os.path.join(export_dir, "model.obj")

    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    bpy.ops.export_scene.obj(
        filepath=obj_path,
        use_triangles=True
    )

    return obj_path

