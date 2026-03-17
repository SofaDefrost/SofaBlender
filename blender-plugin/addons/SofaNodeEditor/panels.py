import bpy

class SofaSimulationPanel(bpy.types.Panel):
    """Creates a new panel in the object properties window"""
    bl_label = "Sofa Prefab"
    bl_idname = "OBJECT_PT_SOFA_PREFAB"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_context = "object"
    bl_category = "SOFA"
    
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
        box.label(text="Import scene")
        row = box.row()
        row.prop(node_tree, "filename")
        
        row = box.row()
        row.operator("sofa.scene_import", text="Import XML")


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

def socket_name_exists(name, sockets):
    return any(s.name == name for s in sockets)

class NODE_PT_SOFA_SOCKET_LIST(bpy.types.Panel):
    bl_label = "Sofa Sockets"
    bl_idname = "NODE_PT_SOFA_SOCKET_LIST"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Node"

    #@classmethod
    #def poll(cls, context):
    #    return context.space_data and context.space_data.type == 'NODE_EDITOR'

    def draw(self, context):
        layout = self.layout
        node = context.active_node

        if not node:
            layout.label(text="No selected node", icon='INFO')
            return

        box = layout.box()
        box.label(text="Input sockets")
        for index, socket in enumerate(node.inputs):
            if socket.name in ["self",""]:
                continue 

            row = box.row(align=True)
            row.label(text=socket.name, icon='DOT')
            op = row.operator("NODE_OT_panel_remove_socket", text="", icon='X')
            op.socket_index = index
            op.socket_type = "INPUT"

        box = layout.box()
        box.label(text="Output sockets")
        for index, socket in enumerate(node.outputs):
            if socket.name in ["self",""]:
                continue 

            row = box.row()
            row.label(text=socket.name, icon='DOT')
            op = row.operator("NODE_OT_panel_remove_socket", text="", icon='X')
            op.socket_index = index
            op.socket_type = "OUTPUT"
        
        layout.separator()
        layout.operator("NODE_OT_panel_add_socket", icon='ADD')

def register():
    bpy.utils.register_class(SofaSimulationPanel)
    bpy.utils.register_class(NODE_PT_SOFA_SOCKET_LIST)

def unregister():
    bpy.utils.unregister_class(SofaSimulationPanel)
    bpy.utils.unregister_class(NODE_PT_SOFA_SOCKET_LIST)

