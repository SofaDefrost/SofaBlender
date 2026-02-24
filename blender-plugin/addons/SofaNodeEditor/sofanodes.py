import bpy
from bpy.types import NodeTree, Node, NodeSocket, NodeSocketObject
from . import sofainfos
from . import  utils
import inspect

socket_from_type = {
                "template" : "SofaTemplateSocket",
                "string" : "NodeSocketString",
                "object" : "SofaObjectSocket",
                "data" : "SofaDataSocket",
                "blender_data" : "SofaBlenderSocket",
                "vector" : "NodeSocketVector",
                "float" : "NodeSocketFloat",
                "int" : "NodeSocketInt",
                "blender_object" : "BlenderObjectSocket",
                "filepath" : "NodeSocketStringFilePath"
            }

# Derived from the NodeTree base type, similar to Menu, Operator, Panel, etc.
class SofaSimulationTree(NodeTree):
    # Description string
    '''A sofa simulation'''
    # Label for nice name display
    bl_label = "Sofa Simulation Editor"
    
    # Icon identifier
    bl_icon = 'NODETREE'

    filename : bpy.props.StringProperty(name="filename", default="")

class SofaSelfSocket(NodeSocket):
    # Description string
    '''Sofa self socket type'''
    
    # Label for nice name display
    bl_label = "Sofa self"

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        layout.label(text=text)
   
    # Socket color
    def draw_color(self, context, node):
        return (1.0, 1.4, 0.216, 0.5)
    
# Custom socket type
class SofaObjectSocket(NodeSocket):
    # Description string
    '''Sofa object socket type'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    #bl_idname = 'SofaObjectSocket'
    
    # Label for nice name display
    bl_label = "Sofa object"

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        layout.label(text=text)
   
    # Socket color
    def draw_color(self, context, node):
        return (1.0, 1.4, 0.216, 0.5)

# Custom socket type
class SofaBlenderSocket(NodeSocket):
    # Description string
    '''Sofa blender socket type'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'SofaBlenderSocket'
    
    # Label for nice name display
    bl_label = "Blender data"

    value : bpy.props.StringProperty(default="COUCOU") 
    is_valid = False

    def init(self):
        self.is_valid = True

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        layout.label(text=text)

    # Socket color
    def draw_color(self, context, node):
        print("DRAW S")
        if self.is_valid:
            return (1.0, 0.0, 0.9, 0.5)
        return (1.0, 0.0, 0.0, 0.5)

# Custom socket type
class BlenderObjectSocket(NodeSocketObject):
    # Description string
    '''Blender Object socket type'''

    # Optional identifier string. If not explicitly defined, the python class name is used.
    bl_idname = 'BlenderObjectSocket'
    
    # Label for nice name display
    bl_label = "Blender object"

    def mesh_poll(self, obj):
        return obj.type == 'MESH' or obj.type == "CURVE"

    object: bpy.props.PointerProperty(name="Object", type=bpy.types.Object, poll=mesh_poll)


    def init(self):
        super().init()

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        if self.object is None:
            layout.alert = True
            layout.prop(self, "object", text=text, icon="ERROR")
            return 

        if self.is_linked:
            layout.label(text=text)
        else:            
            layout.alert = False
            layout.prop(self, "object", text=text)
        
    def draw_color(self, context, node):
        return (0.2, 0.7, 1.0, 1.0)

# Custom socket type
class SofaDataSocket(NodeSocket):
    # Description string
    '''Sofa data socket type'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    # bl_idname = 'CustomSocketType'
    
    # Label for nice name display
    bl_label = "Blender data"

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        layout.label(text=text)
   
    # Socket color
    def draw_color(self, context, node):
        return (1.0, 0.36, 1.3, 0.5)


# Custom socket type
class SofaTemplateSocket(NodeSocket):
    # Description string
    '''Sofa template socket type'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    # bl_idname = 'CustomSocketType'
    
    # Label for nice name display
    bl_label = "Sofa template"

    # Enum items list
    my_items = (
        ('Vec3', "Vec3", "Particles in 3d"),
        ('Rigid3', "Rigid3", "Rigid frame")
    )

    value: bpy.props.EnumProperty(
        name="template",
        description="Just an example",
        items=my_items,
        default='Vec3',
    )

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        if not self.is_output and self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "value", text=text)

    # Socket color
    def draw_color(self, context, node):
        return (1.0, 0.4, 0.216, 0.5)

# Item de la collection
class MyCollectionItem(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(name="Value")

# Socket custom associé à la collection
class MyCollectionSocket(bpy.types.NodeSocket):
    bl_idname = "MyCollectionSocket"
    bl_label = "Collection Socket"

    # Collection pour stocker les données
    items: bpy.props.CollectionProperty(type=MyCollectionItem)
    value : bpy.props.StringProperty()

    def draw(self, context, layout, node, text):
        # Affiche juste un label et le nombre d'items
        #split = layout.split(factor=0.2)
        #split.label(icon='MESH_CUBE')  # icône à droite
        if self.is_linked: 
            layout.label(text=text)
        else:
            layout.prop(self,"value", text=text) 


    def draw_color(self, context, node):
        return (0.2, 0.6, 1.0, 1.0)

class NodeSocketAny(bpy.types.NodeSocket):
    bl_idname = "NodeSocketAny"
    bl_label = "Any"
    is_input : bpy.props.BoolProperty(name="is_input",default=True)
 
    def draw(self, context, layout, node, text):
        row = layout.row()
        op = row.operator(
                "node.my_search_popup",
                text="",
                icon='PLUS',
                emboss=False
        )

        op.node_classname = self.node.type if self.node.bl_idname == "CustomObject" else self.node.bl_idname
        op.node_name = self.node.name
        op.is_input = self.is_input

    def draw_color(self, context, node):
        return (0.6, 0.6, 0.6, 0.6)

    #def draw_context_menu(self, context, layout):
    #    op = layout.operator(
    #        "node.remove_socket",
    #        text="Remove Socket"
    #    )
    #    op.node_classname = self.node.bl_idname
    #    op.node_name = self.node.bl_idname

# Mix-in class for all custom nodes in this tree type.
# Defines a poll function to enable instantiation.
class MyCustomTreeNode:
    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'SofaSimulationTree'

class MyCustomNode(MyCustomTreeNode, Node): 
    '''My custom node''' 
    bl_idname = 'CUSTOM_NODE' 
    bl_label = 'My Custom Node' 
    bl_icon = 'OBJECT_DATA' 
     
    # define inputs and outputs 
    my_input: bpy.props.FloatProperty(name='My Input', default=0.0) 
    my_output: bpy.props.FloatProperty(name='My Output', default=0.0) 
 
    def update(self): 
        # update node when input changes 
        self.my_output = self.my_input * 2.0 

class PrefabGroupNode(MyCustomTreeNode, Node): 
    '''My custom node''' 
    bl_idname = 'PrefabGroupNode' 
    bl_label = 'My Custom Node' 
    bl_icon = 'OBJECT_DATA' 
     
    # define inputs and outputs 
    my_input: bpy.props.FloatProperty(name='My Input', default=0.0) 
    my_output: bpy.props.FloatProperty(name='My Output', default=0.0) 
 
    def update(self): 
        # update node when input changes 
        self.my_output = self.my_input * 2.0 

### Node Categories ###
# Node categories are a python system for automatically
# extending the Add menu, toolbar panels and search operator.
# For more examples see release/scripts/startup/nodeitems_builtins.py
import nodeitems_utils
from nodeitems_utils import NodeCategory, NodeItem
from . import sofaerrors

class MyNodeCategory(NodeCategory):
    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == 'SofaSimulationTree'

def socket_name_exists(name, sockets):
    return any(s.name == name for s in sockets)


def object_class_generator(node_name, default_name, inputs, outputs):
    class SofaObjectNode(MyCustomTreeNode, Node):
        # === Basics ===
        # Description string
        '''A custom node'''
        # Optional identifier string. If not explicitly defined, the python class name is used.
        bl_idname = node_name

        # Label for nice name display
        bl_label = node_name
        bl_icon = 'NODE'

        #selected_item: bpy.props.StringProperty(name="Selected Item")
        
        canAddInput : bpy.props.BoolProperty(name="canAddInput")  = True
        canAddOutput : bpy.props.BoolProperty(name="canAddOutput") = True

        # === Custom Properties ===
        # These work just like custom properties in ID data blocks
        # Extensive information can be found under
        # http://wiki.blender.org/index.php/Doc:2.6/Manual/Extensions/Python/Properties
        #name: bpy.props.StringProperty(default=default_name)
      
        def update(self):
            self.sync_any_socket()

        def sync_any_input(self):
            if self.canAddInput and hasattr(self, "inputs"):
                if len(self.inputs) == 0:
                    return 

                # sécurité
                if self.inputs[-1].bl_idname != "NodeSocketAny":
                    n = self.inputs.new("NodeSocketAny", "")
                    n.is_input = True
                    return

                last = self.inputs[-1]

                # 🔌 connecté → créer un vrai socket
                if self.canAddInput and last.is_linked:
                    links = list(last.links)
                    n = links[0].from_socket.name
                    t = links[0].from_socket.bl_idname
                    if n == "self":
                        n = "src"
                        t = "SofaObjectSocket"

                    # Remove the links form the current socket if there is one with similar name
                    if socket_name_exists(n, self.inputs):
                        tree = bpy.context.space_data.edit_tree
                        for link in list(links):
                           tree.links.remove(link)   
                        return 
                
                    new = self.inputs.new(str(t), n)
                    self.id_data.links.new(links[0].from_socket, new)
                    self.inputs.remove(last)
                    
                    n = self.inputs.new("NodeSocketAny", "")
                    n.is_input = True

        def sync_any_output(self):
            if self.canAddOutput and hasattr(self, "outputs"):
                if len(self.outputs) == 0:
                    return 

                # sécurité
                if self.canAddOutput and self.outputs[-1].bl_idname != "NodeSocketAny":
                    n = self.outputs.new("NodeSocketAny", "")
                    n.is_input = False
                    return

                last = self.outputs[-1]

                # 🔌 connecté → créer un vrai socket
                if self.canAddOutput and last.is_linked:
                    links = list(last.links)
                    n = links[0].to_socket.name
                    t = links[0].to_socket.bl_idname

                    if socket_name_exists(n, self.outputs):
                        tree = bpy.context.space_data.edit_tree
                        for link in list(links):
                            tree.links.remove(link)                    
                        return 

                    new = self.outputs.new(str(t), n)
                    self.id_data.links.new(new, links[0].to_socket)    
                    self[n] = self.outputs[n].default_value

                    self.outputs.remove(last)

                    t = self.outputs.new("NodeSocketAny", "")
                    t.is_input = False

        def sync_any_socket(self):
            self.sync_any_input()
            self.sync_any_output()

        def init(self, context):
            self.name = default_name
            if "Prefab" not in node_name and "BlenderObject" != node_name:
                self.outputs.new('SofaSelfSocket', "self")
                
            for type, name in outputs:                
                s = self.outputs.new(socket_from_type[type], name)
                default_value = sofainfos.get_default_value(node_name, name)
                print(f"ADD OUTPUT {socket_from_type[type]}.{name} to value {default_value}"  )
                #if default_value:
                #    s.default_value = default_value 
        
            for type, name in inputs:
                s = self.inputs.new(socket_from_type[type], name)
                default_value = sofainfos.get_default_value(node_name, name)
                print(f"ADD INPUT {type}.{name} to value {default_value}"  )
                #if default_value:
                #    s.default_value = default_value 
        
            self.canAddInput = True
            self.canAddOutput = True

            if self.bl_idname == "ConstantValue":
                self.canAddInput = False
                self.canAddOutput = True

            # Socket creation must always be at the end of the node.
            if self.canAddInput:
                n = self.inputs.new("NodeSocketAny", "")
                n.is_input = True

            if self.canAddOutput: 
                n = self.outputs.new("NodeSocketAny", "")
                n.is_input = False

        def draw_buttons(self, context, layout): 
            # Si le socket est connecté, afficher le champ pour saisir la valeur
            for socket in self.outputs:
                row = layout.row(align=True)
                if socket.name in self.keys():  
                    row.prop(self, f'["{socket.name}"]', text=socket.name)
                    
            for socket in self.inputs:
                row = layout.row(align=True)
                row.alert = True            
                
                #if socket.name in sofaerrors.errors.get(self.name,{}) :  
                    
        # Optional: custom label
        # Explicit user label overrides this, but here we can define a label dynamically
        def draw_label(self):  
            if node_name != "BlenderObject":
                return node_name       

            selected_object = self.inputs["blender object"].object
            if not selected_object:
                return node_name 

            depsgraph = bpy.context.evaluated_depsgraph_get()
            obj_eval = selected_object.evaluated_get(depsgraph)
            mesh = obj_eval.to_mesh()

            vtx = len(mesh.vertices)
            polys = len(mesh.polygons)
            
            return f"{node_name} (polys: {polys}, vtx:{vtx})"

        
    return SofaObjectNode

def socket_type_name(sock):
    """
    Retourne une chaîne identifiant le type d'un socket,
    qu'il soit NodeSocket ou NodeTreeInterfaceSocket.
    """
    # NodeSocket classique
    if hasattr(sock, "bl_idname"):
        return sock.bl_idname
    # NodeTreeInterfaceSocket (inputs/outputs de Node Group)
    elif hasattr(sock, "type"):
        return sock.type
    elif hasattr(sock, "bl_socket_idname"):
        return sock.bl_socket_idname
    
    # Fallback
    else:
        raise TypeError(f"Type de socket inconnu: {sock}")

def node_class_generator(node_name, default_name, inputs, outputs):
    class SofaPrefabNode(MyCustomTreeNode, Node):
        # === Basics ===
        # Description string
        '''A custom node'''
        # Optional identifier string. If not explicitly defined, the python class name is used.
        bl_idname = node_name

        # Label for nice name display
        bl_label = node_name

        # === Custom Properties ===
        # These work just like custom properties in ID data blocks
        # Extensive information can be found under
        # http://wiki.blender.org/index.php/Doc:2.6/Manual/Extensions/Python/Properties
        name: bpy.props.StringProperty(default=default_name)
        type: bpy.props.PointerProperty(type=bpy.types.NodeTree, 
                                        update=lambda self, context: self.type_changed(),
                                        poll=lambda self, obj: obj != bpy.context.space_data.node_tree)
        
        def init(self, context):
            self.outputs.new('SofaSelfSocket', "self")
            
            self.use_custom_color = True
            self.color = (0.1,0.1,0.1) 
    
        def type_changed(self):
            if self.type is None:
                return 
            
            if self.type.name in bpy.data.node_groups:
                ng = bpy.data.node_groups[self.type.name]
                
                self.inputs.clear()
                self.outputs.clear() 

                for item in ng.interface.items_tree:
                    if item.item_type == "SOCKET":    
                        socket = item 
                        if socket.in_out == "INPUT":
                            if socket.name not in self.inputs:
                                print(f"ADD: {socket.name}")
                                self.inputs.new(socket.bl_socket_idname, socket.name)

                        if socket.in_out == "OUTPUT":
                            if socket.name not in self.outputs:
                                print(f"ADD: {socket.name}")
                                self.outputs.new(socket.bl_socket_idname, socket.name)
                    
        def draw_buttons_ext(self, context, layout):
            layout.prop(self, "name")
    
        def draw_buttons(self, context, layout):
            layout.prop(self, "type")
      
        def draw_color(self):
            return (0.1, 0.4, 0.216, 0.5)
      
        # Optional: custom label
        # Explicit user label overrides this, but here we can define a label dynamically
        def draw_label(self):
            if self.type:   
                return self.name+" ("+self.type.name +")"
            return self.name +"(undefined)"

    return SofaPrefabNode

def python_class_generator(node_name, default_name, inputs, outputs):
    class SofaPythonMethodNode(object_class_generator(node_name,node_name,[],[]), Node):
        # === Basics ===
        # Description string
        '''A custom node'''
        # Optional identifier string. If not explicitly defined, the python class name is used.
        bl_idname = node_name

        # Label for nice name display
        bl_label = node_name

        # === Custom Properties ===
        # These work just like custom properties in ID data blocks
        # Extensive information can be found under
        # http://wiki.blender.org/index.php/Doc:2.6/Manual/Extensions/Python/Properties
        
        type: bpy.props.PointerProperty(type=bpy.types.Text, 
                                        update=lambda self, context: self.type_changed())
        
        def type_changed(self):
            if self.type is None:
                return 
            
        def init(self, context):
            super().init(context)
            self.use_custom_color = True
            self.color = (0.1,0.1,0.1) 
               
        def draw_buttons(self, context, layout):
            layout.prop(self, "type")
            
        def draw_label(self):
            return self.type.name + " ("+self.name+")"

    return SofaPythonMethodNode


def unregister_node_cat_types(cats):
    from bpy.utils import unregister_class

    try:
        bpy.types.NODE_MT_add.remove(cats[1])
    except:
        print("REMOVE CATEGORy: ", cats[1])
        pass

    print("CATEGORy: ", cats)
    for mt in cats[2]:
        try:
            bpy.utils.unregister_class(mt)
        except:
            pass
    for pt in cats[3]:
        try:
            bpy.utils.unregister_class(pt)
        except:
            pass

def my_unregister_node_categories(categories):
    for cat_types in categories:
        try:
            unregister_node_cat_types(cat_types)
        except:
            pass
    nodeitems_utils._node_categories.clear()


def generate_all_nodes():
    from bpy.utils import register_class
    
    import json, os
    path = os.path.abspath(os.path.dirname(__file__))
    nodes_description = json.load(open(os.path.join(path,"nodes.json"),"r"))
    
    node_categories = {}    
    for object  in nodes_description:
        name = object["classname"]
        category = object["category"]
        default_name = object["default_name"]
        
        if category in ["Node"]:
            node_class = node_class_generator(name, default_name, object["inputs"], object["outputs"])
        elif name in ["BlenderController"]:
            node_class = python_class_generator(name, default_name, object["inputs"], object["outputs"])
        else:
            node_class = object_class_generator(name, default_name, object["inputs"], object["outputs"])
        
        register_class(node_class)
        
        if category not in node_categories:
            node_categories[category] = []
                 
        node_categories[category].append(name) 

    #print("Categories -> ", node_categories.keys() )
    register_class(node_class_generator("Prefab","Prefab",[],[]))
    
    class CustomObject(object_class_generator("Custom","Custom",[],[])):
         # === Basics ===
        # Description string
        '''A custom node'''

        # Optional identifier string. If not explicitly defined, the python class name is used.
        bl_idname = "CustomObject"

        # Label for nice name display
        bl_label = "Object"

        bl_width_default = 300
        bl_width_min = 300

        type: bpy.props.StringProperty(default="", 
                                       update=lambda self, context: self.type_changed())
        
        def init(self, context):      
            self.color = (0.1,0.1,0.1) 
            super().init(context)
            
        def type_changed(self):
            if self.type == "":
                self.name = "" 
                return 

            self.name = self.type.lower()

        def draw_buttons(self, context, layout): 
            is_empty = (self.type == "") 
            if is_empty:
                split = layout.split(factor=0.3) 
                split.alert = True
                split.label(text="type")
                op = split.operator(
                    "node.search_sofa_type_popup",
                    text="Name",
                    icon='ERROR',
                    emboss=True)
                op.node_name = self.name
            else:
                icon = "ASSET_MANAGER" if sofainfos.get_creator(self.type) else "PLUS"

                row = layout.row()
                row.prop(self, "type", icon=icon)
      
            layout.separator()
            super().draw_buttons(context, layout)
            
        # Optional: custom label
        # Explicit user label overrides this, but here we can define a label dynamically
        def draw_label(self):
            if self.type == "":   
                return f"undefined (CustomObject)"             
            return f"{self.type} (CustomObject)"

    register_class(CustomObject)
    node_categories["Object"]=["CustomObject"]    
    node_categories["Prefab"]=["Prefab", "NodeGroupInput", "NodeGroupOutput"]
    node_categories["Node"] = ["NodeFrame"]

    flat_categories = []
    for k,v in node_categories.items():
        flat_categories.append( MyNodeCategory(k, k, items=[NodeItem(n) for n in v] ) )

    my_unregister_node_categories(flat_categories)
    nodeitems_utils.register_node_categories('SOFA_NODES', flat_categories)

from bpy.app.handlers import persistent

@persistent
def auto_node_on_link(scene):
    print("AUTO_NODE_ON_LINK")

def register():
    bpy.utils.register_class(SofaSimulationTree)
    bpy.utils.register_class(SofaTemplateSocket)
    bpy.utils.register_class(SofaSelfSocket)
    bpy.utils.register_class(SofaObjectSocket)
    bpy.utils.register_class(SofaDataSocket)
    bpy.utils.register_class(SofaBlenderSocket)
    bpy.utils.register_class(BlenderObjectSocket)
    bpy.utils.register_class(MyCollectionItem)
    bpy.utils.register_class(MyCollectionSocket)
    
    bpy.utils.register_class(NodeSocketAny)
    bpy.utils.register_class(MyCustomNode)
    bpy.utils.register_class(PrefabGroupNode)
    
    
    if auto_node_on_link not in bpy.app.handlers.depsgraph_update_post:
        print("REGISTER... ")
        bpy.app.handlers.depsgraph_update_post.append(auto_node_on_link)

    generate_all_nodes()

def unregister():
    bpy.utils.unregister_class(SofaSimulationTree)
    bpy.utils.unregister_class(SofaTemplateSocket)
    bpy.utils.unregister_class(SofaSelfSocket)
    bpy.utils.unregister_class(SofaObjectSocket)
    bpy.utils.unregister_class(SofaDataSocket)
    bpy.utils.unregister_class(SofaBlenderSocket)
    bpy.utils.unregister_class(BlenderObjectSocket)
    bpy.utils.unregister_class(MyCollectionItem)
    bpy.utils.unregister_class(MyCollectionSocket)
    bpy.utils.unregister_class(NodeSocketAny)
    bpy.utils.unregister_class(MyCustomNode)
    bpy.utils.unregister_class(PrefabGroupNode)

