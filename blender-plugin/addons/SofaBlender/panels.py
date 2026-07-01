import bpy

class SofaBakingPanel(bpy.types.Panel):
    """Creates a Panel in the scene context of the properties editor"""
    bl_label = "Sofa Simulations"
    bl_idname = "SCENE_PT_layout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        layout = self.layout

        scene = context.scene

        row = layout.row()
        row.label(text="Simulations:")
        row = layout.row()
        self.layout.prop(bpy.context.scene,"sofa_scene_collection", expand=True)
        for item in list(bpy.context.scene.sofa_scene_collection):
            row = layout.row()
            row.label(text=str(item.sofa_name))
            row.label(text=str(item.sofa_path))
            
        row = layout.row()    
        row.operator("scene.add_sofa_simulation")

        row = layout.row()    
        row.operator("scene.import_sofa_simulations")

        row = layout.row()    
        row.operator("scene.remove_sofa_simulations")

        
        # Create a simple row.
        layout.label(text=" Simulation properties:")

        row = layout.row()
        row.prop(scene, "frame_start")
        row.prop(scene, "frame_end")

        row = layout.row()
        #row.prop(scene, "delta time")

        # Big render button
        layout.label(text="Bake")
        row = layout.row()
        row.scale_y = 2.0
        row.operator("render.render")

class UIListPanelObject(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Sofa properties"
    bl_idname = "OBJECT_PT_ui_list_example_1"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context):
        self.layout.prop(bpy.context.object,"sofa_type")
        self.layout.prop(bpy.context.object,"sofa_name")
        self.layout.prop(bpy.context.object,"sofa_pathname")

class UIListPanelCollection(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Sofa properties"
    bl_idname = "OBJECT_PT_ui_collect_sofa"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "collection"

    def draw(self, context):
        self.layout.prop(bpy.context.collection,"sofa_type")
        self.layout.prop(bpy.context.collection,"sofa_name")
        self.layout.prop(bpy.context.collection,"sofa_pathname")

def register():
    bpy.utils.register_class(SofaBakingPanel)
    bpy.utils.register_class(UIListPanelObject)
    bpy.utils.register_class(UIListPanelCollection)

def unregister():
    bpy.utils.unregister_class(SofaBakingPanel)
    bpy.utils.unregister_class(UIListPanelObject)
    bpy.utils.unregister_class(UIListPanelCollection)

