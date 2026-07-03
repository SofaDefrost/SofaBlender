import os
import Sofa
import Sofa.Core
import Sofa.Simulation

class BlenderMaterial(Sofa.Core.Controller):
    """
    Custom Controller to describe a Blender Material inside a Sofa scene.
    It is mandatory to define this class inside every python scene you want to make with Blender Materials
    """
    def __init__(self, *args, **kwargs):
        Sofa.Core.Controller.__init__(self, *args, **kwargs)
        
        # This data contains the name of the blend file, when the scene has been exported,
        # you need to add the .blend file in your sofa_export folder WITH THE SAME NAME
        self.addData(
            name="blend_file",
            type="string",
            value=kwargs.get("blend_file", ""),
            help="Path to the .blend file"
        )

        # This data contains the name of the material inside the .blend file
        # e.g. "plastic_01", you don't need the whole Material/plastic_01 path
        self.addData(
            name="material_name",
            type="string",
            value=kwargs.get("material_name", ""),
            help="Name of the material"
        )

        # This data contains the SOFA path of the object you want to apply your material to
        # It shouldn't contain the @ at the beginning as it makes Sofa segfault for some reason
        self.addData(
            name="target_path",
            type="string",
            value=kwargs.get("target_path", ""),
            help="Path of the target model"
        )

def createScene(root):
    root.name = "RootNode"

    # We load the .scn scene if needed
    base_dir = os.environ.get("SOFA_ROOT")
    scene_filename = os.path.join(base_dir, "share", "sofa", "examples", "Demos", "liver.scn")

    try:
        liver_node = Sofa.Simulation.load(scene_filename)
        if liver_node is None:
            print(f"[Warning] Cannot find the scene : {scene_filename}")
        else:
            liver_node.name = "LiverImport"
            root.addChild(liver_node)
    except Exception as e:
        print(f"[Error] {e}")

    # We add the BlenderMaterial object inside the scene
    material_component = BlenderMaterial(
        name="plastic",                                          # The name of the BlenderMaterial object inside sofa
        path="@/Liver/BlenderMaterial",                          # The path of the BlenderMaterial object
        blend_file="library.blend",                              # The name of your .blend file
        material_name="plastic_01",                              # The name of the material in the .blend file
        target_path="/LiverImport/Liver/Visu/VisualModel"        # The path to the object where you want to apply the material without the @
    )

    root.addObject(material_component)

    return root
