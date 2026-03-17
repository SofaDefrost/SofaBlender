import bpy
from bpy.types import NodeTree, Node, NodeSocket
import zmq 
import inspect
# Implementation of custom nodes from Python
socket = None
zmq_context = None

    #socket = zmq_context.socket(zmq.PUB)
    #socket.bind("tcp://*:7134")           
import queue
q=queue.Queue()

import sys, importlib.util

def import_module_from_string(name: str, source: str):
  """
  Import module from source string.
  Example use:
  import_module_from_string("m", "f = lambda: print('hello')")
  m.f()
  """
  spec = importlib.util.spec_from_loader(name, loader=None)
  module = importlib.util.module_from_spec(spec)
  exec(source, module.__dict__)
  #sys.modules[name] = module
  #globals()[name] = module
  return module

# Derived from the NodeTree base type, similar to Menu, Operator, Panel, etc.
class SofaSimulationTree(NodeTree):
    # Description string
    '''A sofa simulation'''
    # Label for nice name display
    bl_label = "Sofa Simulation Editor"
    
    # Icon identifier
    bl_icon = 'NODETREE'

    filename : bpy.props.StringProperty(name="filename", default="")

 
class SofaNodeGroup(bpy.types.NodeTree): 
    '''My custom node group''' 
    bl_label = 'Sofa node group' 
    bl_icon = 'NODETREE' 

    #filename : bpy.props.StringProperty(name ="filename", default="XX")

    def init(self): 
        # initialize node group n
        #self.nodes.new('MechanicalObject') 
        #self.nodes.new('SpringFieldForceField') 
        #self.nodes.new('SofaNode') 
        pass
 
    def update(self): 
        # update node group when input changes 
        print("COUCOU")
        pass

    def draw_button(self):
        for inputs in self.inputs:
            prin("COUCOUT")    

# Custom socket type
class SofaSelfSocket(NodeSocket):
    # Description string
    '''Sofa self socket type'''
    # Optional identifier string. If not explicitly defined, the python class name is used.
    # bl_idname = 'CustomSocketType'
    
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

def object_class_generator(node_name, default_name, inputs, outputs):
    class SofaObjectNode(MyCustomTreeNode, Node):
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
      
        def init(self, context):
            #self.inputs.new('SofaTemplateSocket', "template")
            
            if "Prefab" not in node_name:
                self.outputs.new('SofaSelfSocket', "self")
                self.inputs.new('SofaSelfSocket', "context")
            else:
                self.use_custom_color = True
                self.color = (0.5,0.5,0.5) 
                
            socket_from_type = {
                "template" : "SofaTemplateSocket",
                "string" : "NodeSocketString",
                "object" : "SofaObjectSocket",
                "data" : "SofaDataSocket",
                "blender_data" : "SofaBlenderSocket",
                "vector" : "NodeSocketVector",
                "float" : "NodeSocketFloat"
            }
            for type, name in outputs:
                print("CREATE AN OUTPUT... for ", name)
                self.outputs.new(socket_from_type[type], name)
        
            for type, name in inputs:
                self.inputs.new(socket_from_type[type], name)
           
        def socket_value_update(context):
            print("Value update...", context)
                     
        def draw_buttons_ext(self, context, layout):
            layout.prop(self, "name")

        def draw_buttons(self, context, layout):
            if "Prefab Output" in node_name: 
                node_group = self.id_data                                
                for input_socket in node_group.outputs:
                    if input_socket.name not in self.inputs:
                        self.inputs.new(input_socket.bl_socket_idname, input_socket.name)
                        
                    
            if "Prefab Input" in node_name:
                node_group = self.id_data 
                for output_socket in self.outputs: 
                    if output_socket.name not in node_group.inputs:
                        self.outputs.remove(output_socket)
                               
                for input_socket in node_group.inputs:
                    if input_socket.name not in self.outputs:
                        self.outputs.new(input_socket.bl_socket_idname, input_socket.name)
                
        # Optional: custom label
        # Explicit user label overrides this, but here we can define a label dynamically
        def draw_label(self):
            return node_name 

        def draw_color(self):
            return (0.5, 0.4, 0.216, 1.0)
      
    return SofaObjectNode

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
        type: bpy.props.StringProperty(default="Node")
      
        def init(self, context):
            #self.inputs.new('SofaTemplateSocket', "template")
            #self.outputs.new('SofaSelfSocket', "self")
            #self.inputs.new('SofaSelfSocket', "context")
            
            self.use_custom_color = True
            self.color = (0.1,0.1,0.1) 
            socket_from_type = {
                "template" : "SofaTemplateSocket",
                "string" : "NodeSocketString",
                "object" : "SofaObjectSocket",
                "data" : "SofaDataSocket",
                "blender_data" : "SofaBlenderSocket",
                "vector" : "NodeSocketVector",
                "float" : "NodeSocketFloat"
            }
            
            #for type, name in outputs:
            #    self.outputs.new(socket_from_type[type], name)
        
            #for type, name in inputs:
            #    self.inputs.new(socket_from_type[type], name)
    
        def update(self):
            if self.type in bpy.data.node_groups:
                ng = bpy.data.node_groups[self.type]
                    
        def draw_buttons_ext(self, context, layout):
            layout.prop(self, "name")
    
        def draw_buttons(self, context, layout):
            if self.type in bpy.data.node_groups:
                ng = bpy.data.node_groups[self.type]
                
                for input_socket in ng.inputs:
                    if input_socket.name not in self.inputs:
                        s = self.inputs.new(input_socket.bl_socket_idname, input_socket.name)
                                         
                for output_socket in ng.outputs:
                    if output_socket.name not in self.outputs:
                        self.outputs.new(output_socket.bl_socket_idname, output_socket.name)
           
            layout.prop(self, "type")
      
        def draw_color(self):
            return (0.1, 0.4, 0.216, 0.5)
      
        # Optional: custom label
        # Explicit user label overrides this, but here we can define a label dynamically
        def draw_label(self):
            return self.type + " ("+self.name+")"

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
            socket_from_type = {
                "template" : "SofaTemplateSocket",
                "string" : "NodeSocketString",
                "object" : "SofaObjectSocket",
                "data" : "SofaDataSocket",
                "blender_data" : "SofaBlenderSocket",
                "vector" : "NodeSocketVector",
                "float" : "NodeSocketFloat"
            }
            
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
        pass
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

def my_unregister_node_categories():
    for cat_types in nodeitems_utils._node_categories.values():
        try:
            unregister_node_cat_types(cat_types)
        except:
            pass
    nodeitems_utils._node_categories.clear()

def generate_all_nodes():
    from bpy.utils import register_class
    
    m = {
        "classname" : "MechanicalObject",
        "category" : "Mechanics",
        "default_name" : "state", 
        "inputs"   : [("object", "src"),("string","position")],
        "outputs"  : [("template", "type")],
        }
    n = {
        "classname" : "MeshObjLoader",
        "category" : "Loader",
        "default_name" : "loader", 
        "inputs"   : [("string", "filename")],
        "outputs"  : [("data", "position"),("data", "edges"), ("data", "triangles")],
        }
    f = {
        "classname" : "UniformMass",
        "category" : "Mechanics",
        "default_name" : "mass", 
        "inputs"   : [("object", "mstate"),("object", "src")],
        "outputs"  : [],
        }
    s  = {
        "classname" : "StiffSpringForceField",
        "category" : "Mechanics",
        "default_name" : "forcefield", 
        "inputs"   : [("object", "mstate"),("object", "src")],
        "outputs"  : [],
        }               
    g = {
        "classname" : "IdentityMapping",
        "category" : "Mapping",
        "default_name" : "mapping", 
        "inputs"   : [("object", "input"), ("object", "output")],
        "outputs"  : [],
        }
    h    = {
        "classname" : "OglModel",
        "category" : "Visual",
        "default_name" : "rendering", 
        "inputs"   : [("object", "src"),("string","filename"),("string","texturename")],
        "outputs"  : [],
        }
    i    = {
        "classname" : "Prefab",
        "category" : "Node",
        "default_name" : "prefab", 
        "inputs"   : [()],
        "outputs"  : [()],   
        }        
    j = {
        "classname" : "BlenderObject",
        "category" : "Geometry ",
        "default_name" : "geom", 
        "inputs"   : [("string", "blender object")],
        "outputs"  : [("blender_data", "filename"),
                      ("vector", "location"),
                      ("vector", "orientation"),
                      ("vector", "scale")],
        }    
    blender_controller = {
        "classname" : "BlenderController",
        "category" : "Controller ",
        "default_name" : "controller", 
        "inputs"   : [],
        "outputs"  : [],
        }
    
    k = {
        "classname" : "Prefab Input",
        "category" : "Prefab",
        "default_name" : "self", 
        "inputs"   : [],
        "outputs"  : [],
        }     
    l = {
        "classname" : "Prefab Output",
        "category" : "Prefab",
        "default_name" : "self", 
        "inputs"   : [],
        "outputs"  : [],
        }
    math_matrix = {
        "classname" : "Matrix",
        "category" : "Math",
        "default_name" : "self", 
        "inputs"   : [("vector", "translation"),
                      ("vector", "rotation"),
                      ("vector", "scale"),
        ],
        "outputs"  : [("object", "transform"),
        ],
        }    
                
        
    math_op = {
        "classname" : "Transform",
        "category" : "Math",
        "default_name" : "self", 
        "inputs"   : [("object", "transform A"),
                      ("object", "transform B"),
        ],
        "outputs"  : [("object", "transform"),
        ],
        }    
    math_op_rst = {
        "classname" : "MatrixToTRS",
        "category" : "Math",
        "default_name" : "matrixtrs1", 
        "inputs"   : [("object", "transform")],
        "outputs"  : [("vector", "location"),
                      ("vector", "rotation"),
                      ("vector", "scale")],
        }            
    zz    = {
        "classname" : "TransformEngine",
        "category" : "Transform",
        "default_name" : "engine", 
        "inputs"   : [("string","input_position"), 
                      ("string", "translation"), 
                      ("vector", "rotation"),
                      ("vector", "scale")],
        "outputs"  : [("string", "output_position")],   
        }
    ts    = {
        "classname" : "EulerImplicitSolver",
        "category" : "Simulation",
        "default_name" : "timeintegration", 
        "inputs"   : [],
        "outputs"  : [],   
        }
    ts0    = {
        "classname" : "SparseLDLSolver",
        "category" : "Simulation",
        "default_name" : "numericalsolver", 
        "inputs"   : [],
        "outputs"  : [],   
        }
    ts1    = {
        "classname" : "CGLinearSolver",
        "category" : "Simulation",
        "default_name" : "numericalsolver", 
        "inputs"   : [],
        "outputs"  : [],   
        }
    objects = [m, n, f, g, h, s, i, j,k,l, zz, 
               blender_controller, math_op, math_matrix, math_op_rst, ts, ts0, ts1]
    
    print("Registering class... ")
    
    node_categories = {}
    
    for object  in objects:
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
        
    flat_categories = []
    for k,v in node_categories.items():
        flat_categories.append( MyNodeCategory(k, k, items=[NodeItem(n) for n in v] ) )
    
    my_unregister_node_categories()
    nodeitems_utils.register_node_categories('SOFA_NODES', flat_categories)


from bpy.utils import register_class
register_class(SofaSimulationTree)
register_class(SofaNodeGroup)
register_class(SofaTemplateSocket)
register_class(SofaSelfSocket)
register_class(SofaObjectSocket)
register_class(SofaDataSocket)
register_class(SofaBlenderSocket)
register_class(MyCustomNode)

generate_all_nodes()


import threading        
import queue

def register():
    zmq_context = zmq.Context()



    
    def sofa_msg(socket, q):
        while True:
            m = q.get()
            print("SENDING") 
            socket.send_string("sofa",zmq.SNDMORE)
            #socket.send_pyobj({"MyModel.prefab1" :  {"target":input_socket.name, "value":[p,0.0,0.0]}})
   
if __name__ == "__main__":
    register()