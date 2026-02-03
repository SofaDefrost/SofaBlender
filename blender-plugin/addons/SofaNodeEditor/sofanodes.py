import bpy
from bpy.types import NodeTree, Node, NodeSocket

socket_from_type = {
                "template" : "SofaTemplateSocket",
                "string" : "NodeSocketString",
                "object" : "SofaObjectSocket",
                "data" : "SofaDataSocket",
                "blender_data" : "SofaBlenderSocket",
                "vector" : "NodeSocketVector",
                "float" : "NodeSocketFloat",
                "blender_object" : "NodeSocketObject",
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

    # Optional function for drawing the socket input value
    def draw(self, context, layout, node, text):
        layout.label(text=text)
   
    # Socket color
    def draw_color(self, context, node):
        return (1.0, 0.0, 0.9, 0.5)

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

    my_enum_prop: bpy.props.EnumProperty(
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
            layout.prop(self, "my_enum_prop", text=text)

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

    def draw(self, context, layout, node, text):
        # Affiche juste un label et le nombre d'items
        split = layout.split(factor=0.2)
        split.label(icon='MESH_CUBE')  # icône à droite
        split.label(text=text)
        
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
        op.node_classname = self.node.bl_idname
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

        selected_item: bpy.props.StringProperty(name="Selected Item")
        
        canAddInput : bpy.props.BoolProperty(name="canAddInput")  = True
        canAddOutput : bpy.props.BoolProperty(name="canAddOutput") = True

        # === Custom Properties ===
        # These work just like custom properties in ID data blocks
        # Extensive information can be found under
        # http://wiki.blender.org/index.php/Doc:2.6/Manual/Extensions/Python/Properties
        #name: bpy.props.StringProperty(default=default_name)
      
        def update(self):
            self.sync_any_socket()

        def sync_any_socket(self):
            if self.canAddInput and hasattr(self, "inputs"):
                if len(self.inputs) == 0:
                    return 
                last = self.inputs[-1]

                # sécurité
                if last.bl_idname != "NodeSocketAny":
                    n = self.inputs.new("NodeSocketAny", "")
                    n.is_input = True
                    return

                # 🔌 connecté → créer un vrai socket
                if self.canAddInput and last.is_linked:
                    links = list(last.links)
                    n = links[0].from_socket.name
                    if n == "self":
                        n = "src"
                    t = links[0].from_socket.bl_idname
                
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

            if self.canAddOutput and hasattr(self, "outputs"):
                if len(self.outputs) == 0:
                    return 

                last = self.outputs[-1]

                # sécurité
                if self.canAddOutput and last.bl_idname != "NodeSocketAny":
                    n = self.outputs.new("NodeSocketAny", "")
                    n.is_input = False
                    return

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

        def init(self, context):
            self.name = default_name

            if "Prefab" not in node_name:
                self.outputs.new('SofaSelfSocket', "self")
            else:
                self.use_custom_color = True
                self.color = (0.5,0.5,0.5) 
                
            for type, name in outputs:
                self.outputs.new(socket_from_type[type], name)
        
            for type, name in inputs:
                self.inputs.new(socket_from_type[type], name)
        
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
           
        #def draw_context_menu(self, context, layout):
        #    layout.operator(
        #        "node.remove_socket",
        #        text="Remove Socket"
        #    ).socket_name = self.name

        def draw_buttons(self, context, layout):
            
            # Si le socket est connecté, afficher le champ pour saisir la valeur
            for socket in self.outputs:
                row = layout.row(align=True)
                if socket.name in self.keys():  
                    row.prop(self, f'["{socket.name}"]', text=socket.name)
                
        # Optional: custom label
        # Explicit user label overrides this, but here we can define a label dynamically
        def draw_label(self):
            return node_name 

        def draw_color(self):
            return (0.5, 0.4, 0.216, 1.0)
      
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
            #self.inputs.new('SofaTemplateSocket', "template")
            self.outputs.new('SofaSelfSocket', "self")
            #self.inputs.new('SofaSelfSocket', "context")
            
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
    class SofaPythonMethodNode(MyCustomTreeNode, Node):
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
        type: bpy.props.StringProperty(default="Node")
      
        def init(self, context):
            self.use_custom_color = True
            self.color = (0.1,0.1,0.1) 
            
        def update(self):
            if self.type in bpy.data.node_groups:
                ng = bpy.data.node_groups[self.type]
                    
        def draw_buttons_ext(self, context, layout):
            layout.prop(self, "name")
    
        def draw_buttons(self, context, layout):
            if self.type in bpy.data.texts:
                text = bpy.data.texts[self.type].as_string()
                
                cname = self.type                
                if cname.endswith(".py"):
                    cname = cname[:-3]
                
                p = import_module_from_string("test", text)
                a = inspect.getfullargspec(p.__dict__[cname])
                
                for i in range(len(a.args)):
                    arg = a.args[i]
                    value = a.defaults[i]
                    if arg not in self.inputs and arg != "name":                
                        blenderTypes = {
                            float : "NodeSocketFloat",
                            str : "NodeSocketString",
                            list : "NodeSocketVector",
                        }
                        if type(value) in blenderTypes:
                            s = self.inputs.new(blenderTypes[type(value)], arg)
                        else:
                            s = self.inputs.new("NodeSocketString", arg)
                #for output_socket in ng.outputs:
                #    if output_socket.name not in self.outputs:
                #        self.outputs.new(output_socket.bl_socket_idname, output_socket.name)
           
            layout.prop(self, "type")
      
        def draw_color(self):
            return (0.1, 0.4, 0.216, 0.5)
      
        def draw_label(self):
            return self.type + " ("+self.name+")"

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
    node_categories["Prefab"]=["Prefab", "NodeGroupInput", "NodeGroupOutput"]
    node_categories["Node"] = ["NodeFrame"]

    flat_categories = []
    for k,v in node_categories.items():
        print("REGISTERING ", k)
        flat_categories.append( MyNodeCategory(k, k, items=[NodeItem(n) for n in v] ) )

    print("UNREGISTERED")
    my_unregister_node_categories(flat_categories)
    print("RRREGISTERED")
    nodeitems_utils.register_node_categories('SOFA_NODES', flat_categories)
    print("UNREGISTERED 2")

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
    bpy.utils.unregister_class(MyCollectionItem)
    bpy.utils.unregister_class(MyCollectionSocket)
    bpy.utils.unregister_class(NodeSocketAny)
    bpy.utils.unregister_class(MyCustomNode)
    bpy.utils.unregister_class(PrefabGroupNode)

