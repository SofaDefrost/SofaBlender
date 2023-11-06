import bpy

class SofaSimulationPanel(bpy.types.Panel):
    """Creates a new panel in the object properties window"""
    bl_label = "Sofa Prefab"
    bl_idname = "OBJECT_PT_SOFA_PREFAB"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_context = "object"
    
    def draw(self, context):
        layout = self.layout

        node_tree = context.space_data.node_tree

        if not node_tree:
            return 
    
        row = layout.row()
        row.prop(node_tree, "name")

        box = layout.box()
        box.label(text="Execute")
        row = box.row()
        row.operator("sofa.prefab_run", text="Run in Sofa")

        box = layout.box()
        box.label(text="Export")
        row = box.row()
        row.prop(node_tree, "filename")
        
        row = box.row()
        row.operator("sofa.export", text="Export to Sofa")

        box = layout.box()
        box.label(text="WTF (I need help)")
        row = box.row()
        row.operator("firefox.open", text="Sofa doc")
        
        row = box.row()
        row.operator("firefox.open", text="Sofa Python3 doc")
        
        row = box.row()
        row.operator("firefox.open", text="Prefab")

        row = box.row()        
        row.operator("firefox.open", text="Ask chatGPT")

        row = box.row()
        row.operator("firefox.open", text="Ask sofa community")
        
def register():
    bpy.utils.register_class(SofaSimulationPanel)

def unregister():
    bpy.utils.unregister_class(SofaSimulationPanel)

