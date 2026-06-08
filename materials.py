from blender_exporter import BlenderMaterial
def add_materials(root, objects):
    for object, datafields in objects.values():

        root.addObject(
            BlenderMaterial(
                name=object.getName(),
                target_path=object.getPathName(),
                blend_file="library.blend",
                material_name="plastic_03"
            )
        )