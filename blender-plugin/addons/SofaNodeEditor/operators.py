import bpy
import graphlib
import subprocess
from . import sofaerrors
from . import sofainfos

SOCKET_TYPES = [
    ('NodeSocketFloat',   "float",   ""),
    ('NodeSocketString',  "string",  ""),
    ('NodeSocketInt',     "int",     ""),
    ('NodeSocketBool',    "bool", ""),
    ('NodeSocketVector',  "vec3",  ""),
    ('NodeSocketColor',   "RGBAColor",   ""),
    ('SofaTemplateSocket', "template",""),
    ('SofaObjectSocket', "Sofa Object",""),
    ("SofaBlenderSocket", "Blender Object",""),
    ("NodeSocketStringFilepath", "filename","")
]

TEMPLATE_TYPES = [
    ('SofaTemplateSocket', "Vec3d, Rigid3d",""),
    ('NodeSocketString',  "other",  ""),
]

def node_generate_new_socket_name(node, name, is_input):
    target = node.inputs if is_input else node.outputs    
    i = 0 
    newname = name
    while newname in target:
        i+=1
        newname = f"{name}{i}"
    return newname

def datatype_to_sockettype(sofa_data_type):
    types = {
        "f" : "NodeSocketFloat",
        "d" : "NodeSocketFloat",
        "string" : "NodeSocketString",
        "bool" : "NodeSocketBool",
        "I" : "NodeSocketInt",
        "i" : "NodeSocketInt",
        "Vec3" : "NodeSocketVector",
    }
    if sofa_data_type in types:
        return types[sofa_data_type]
    
    if "vector<" in sofa_data_type:
        return "MyCollectionSocket"

    return "NodeSocketString"

def socket_name_exists(name, sockets):
    return any(s.name == name for s in sockets)

def node_create_socket(name, is_input, type, value, node):
    if is_input:
        target = node.inputs
    else: 
        target = node.outputs

    if socket_name_exists(name, target): 
        return False
    
    socket = target.new(type=type, name=name)
    
    if value:
        socket.default_value = value
    target.move(len(target)-1, len(target)-2)
    return True 


def get_full_parent_path(node):
    if node.parent:
        return f"{get_full_parent_path(node.parent)}/{node.name}"
    return f"{node.name}"

def sanitize_name(name):
    return name.replace(".","_") 

def build_dag(self, node_tree, node):
        # Build a name without . because Sofa is not supposed to use that kind of name        
        py_nodename = sanitize_name(node_tree.name)
        outfilename = py_nodename+".py"
        
        # In case there is no filename provided we use the default one
        if node_tree.filename == "":
            node_tree.filename = outfilename
        outfilename = node_tree.filename
        
        graph = {}
        for node in node_tree.nodes:
            print("    Node ", node.name)
            graph[node] = set()
            for input in node.inputs:
                for link in input.links:
                    print("      linked to ", link.from_node.name)
                    graph[node].add(link.from_node)  
            if node.parent:
                graph[node].add(node.parent)

        # Sorts the nodes to match the graph predecessor's ordering.                     
        ts = graphlib.TopologicalSorter(graph)
        sorted_list_of_nodes=list(ts.static_order())
                    
        f = open(outfilename, "w")

        # Handles imports for both Prefab and Controller
        prefab_instances = []
        controller_instances = []
        for current_node in sorted_list_of_nodes:
            if current_node.bl_idname == "Prefab":
                prefab_instances.append(current_node)
            elif current_node.bl_idname == "BlenderController":
                controller_instances.append(current_node)
                    
        imports = ""
        already_imported = {}
        for prefab_instance in prefab_instances:
            prefab_name = prefab_instance.type.name
            if prefab_name not in already_imported:
                imports += "from {} import {}\n".format(prefab_name, prefab_name)
                already_imported[prefab_name] = True
        
        already_imported = {}
        for controller_instance in controller_instances:
            controller_name = self.get_controller_name(controller_instance.type)
            if controller_name not in already_imported:
                imports += "from {} import {}\n".format(controller_name, controller_name)
                already_imported[controller_name] = True
                
        f.write("import Sofa\n")
        f.write("from SofaBlender import ConstantValue\n")    
        f.write(imports)
        f.write("\n")

        kwargs=""        
        for item in node_tree.interface.items_tree:
            if item.item_type == "SOCKET":
                if item.in_out == "INPUT" and item.name:
                    kwargs += " {}={},".format(item.name, repr(item.default_value))  
                
        f.write("def {}(name='{}',{}):\n".format(py_nodename, py_nodename, kwargs[:-1]))
        f.write("    self = Sofa.Core.Node(name)\n")

        # Process input to generated the Data field
        for current_node in sorted_list_of_nodes:
            if current_node.bl_idname == "NodeGroupInput":
                for output_socket in current_node.outputs:
                    type = "string"
                    if output_socket.bl_idname == "NodeSocketVector":
                        type = "Vec3d" 
                    elif output_socket.bl_idname == "NodeSocketFloat":
                        type = "float"
                    elif output_socket.bl_idname == "NodeSocketString":
                        type = "string"
                    elif output_socket.bl_idname == "NodeSocketBool":
                        type = "bool"
                    else:
                        print(f"SOCKET TYPE UNSUPPORTED {output_socket.bl_idname}")        
                    if output_socket.bl_idname not in ["SofaObjectSocket","NodeSocketVirtual"]:                       
                        f.write("    self.addData(name='{}', type='{}', help='', default={})\n".format(output_socket.name, type, output_socket.name))     
                    else:
                        print(f"NodeGroupInput::socket unsupported '{output_socket.bl_idname}'")    
            if current_node.bl_idname == "NodeGroupOutput":
                for input_socket in current_node.inputs:
                    if input_socket.bl_idname not in ["NodeSocketVirtual"]:
                        f.write("    self.addData(name='{}', type='{}', help='')\n".format(input_socket.name, "string"))     

        local_context = {"self" : {}} 
        node2path = {}
        for current_node in sorted_list_of_nodes:
            if current_node.bl_idname == "NodeGroupInput":
                continue

            if current_node.bl_idname == "NodeGroupOutput":
                continue 

            if current_node.bl_idname == "BlenderController":
                blender_name = self.get_controller_name(current_node.type)
                print("Generating sofa controller from blender ",blender_name)
                self.export_controller_to(blender_name) 
                
            if current_node.bl_idname == "BlenderObject":
                try:
                    blender_object = current_node.inputs["blender object"].object
                    blender_name = blender_object.name
                except Exception as e:
                    print(f"ERROR, missing object in a BlenderObject with error {e}",)

                    current_node.errors = ["blender object"]
                    sofaerrors.errors[current_node.name] = {"blender object"}
                    continue
                    #current_node.nodes.inputs["blender object"].alert = True

                bpy.ops.object.select_all(action='DESELECT')
                bpy.data.objects[blender_name].select_set(True)
                
                filename = blender_name+".obj"
                bpy.ops.wm.obj_export(filepath=filename, 
                                      export_selected_objects=True,  
                                      export_uv=True, export_materials=True, path_mode='COPY')
                
                if "filename" in current_node.outputs:
                    current_node.outputs["filename"].default_value = filename
                if "location" in current_node.outputs:
                    current_node.outputs["location"].default_value = blender_object.location
                if "orientation" in current_node.outputs:
                    current_node.outputs["orientation"].default_value = blender_object.rotation_euler
                if "scale" in current_node.outputs:
                    current_node.outputs["scale"].default_value = blender_object.scale                
                
                print("        save special blender object values is ", current_node.outputs["filename"].default_value)
                continue

            parent = "self"
            prefix = "_"
            base_name = sanitize_name(current_node.name)
            if current_node.parent:
                prefix += "_"+get_full_parent_path(current_node.parent).replace("/","_")

            i = 1
            local_name = prefix + "_" + base_name + "__"
            while local_name in local_context:
                incr_name = local_name+str(i)
                if incr_name in local_context:
                    continue
                else: 
                    local_name = local_name+str(i)+"__"
                    current_node.name = base_name+str(i)+"__"
                    break
            local_context[local_name] = True

            if current_node.parent:
                parent = "__"+get_full_parent_path(current_node.parent).replace("/","_")+"__"

            node2path[current_node] = local_name

            args = ""
            for input in current_node.inputs:
                print(f"Processing edge: {current_node.name}.{input.name}")
                        
                if input.bl_idname == "NodeSocketAny":
                    continue
                if len(input.links) > 0:
                    for link in input.links:
                        print(f" - connecting: {current_node.name}.{input.name} <- {link.from_node.name}.{link.from_socket.name} ({link.from_socket.bl_idname})")
                        if link.from_socket.bl_idname != "SofaBlenderSocket":
                            if link.from_socket.node.bl_idname == "BlenderObject":
                                if link.from_socket.bl_idname == "SofaSelfSocket":
                                    if link.to_socket.name in link.from_node.outputs:
                                        args += ", {}={}".format(input.name, repr(link.from_node.outputs[link.to_socket.name].default_value))                                                    
                                    else:
                                        args += ", {}={}.{}.linkpath".format(input.name, link.from_node.name, input.name)
                                else:
                                    depil = list if link.from_socket.bl_idname == "NodeSocketVector" else lambda x:x
                                    args += ", {}={}".format(input.name, repr(depil(link.from_socket.default_value)))                                                    
                            elif link.from_socket.bl_idname == "SofaSelfSocket":
                                if input.bl_idname == "SofaObjectSocket":
                                    args += ", " + input.name + "=" + node2path[link.from_node] + ".linkpath"
                                else: 
                                    args += ", " + input.name + "=" + node2path[link.from_node] + "." + input.name + ".linkpath"
                            else:
                                source_name = str(link.from_node.name)
                                if link.from_node.bl_idname == "NodeGroupInput":
                                    source_name = "self"
                                if link.from_node in node2path:
                                    source_name = node2path[link.from_node]
                                target_name = input.name
                                if target_name == "src" and link.from_socket.name != "self":
                                    target_name = link.from_socket.name 

                                mode = ".value" if input.name == "template" else ".linkpath"

                                args += ", " + target_name + "=" + source_name + "." + str(link.from_socket.name) + mode        
                        else:
                            print("         Dumping BlenderSocket", dir(link.from_socket))
                            args += ", {}='{}'".format(input.name, str(link.from_socket.value))                        
                else:        
                    if hasattr(input, "default_value") and input.default_value != "":
                        print(f" - setting value: {current_node.name}.{input.name} = {input.default_value}")                        
                        args += ", " + input.name + "=" + repr(input.default_value) 
                    elif hasattr(input, "value"):
                        print(f" - setting value: {current_node.name}.{input.name} = {input.value}")                        
                        args += ", " + input.name + "=" + repr(input.value) 
                    else:
                        print(f"    Unsupported socket saving {current_node.name}.{input.name} (type = {input.bl_idname})")    
            if current_node.bl_idname == "ConstantValue":
                for socket in current_node.outputs:
                    if socket.name not in ["","self"]:
                        args += ", " + socket.name + "=" + repr(current_node[socket.name]) 
                    
            if current_node.bl_idname == "BlenderController":
                name = self.get_controller_name(controller_instance.type) 
                name1 = name+"1"
                args=""
                f.write("    {} = self.addObject({}(name='{}' {}))\n".format(
                    local_name,
                    name,
                    name1,
                    args))                            
            elif current_node.bl_idname == "CustomObject":
                f.write("    {} = {}.addObject('{}', name='{}' {})\n".format(
                    local_name,
                    parent, 
                    current_node.type,
                    current_node.name,
                    args))                
            elif current_node.bl_idname == "ConstantValue":
                f.write("    {} = {}.addObject({}(name='{}' {}))\n".format(
                    local_name,
                    parent, 
                    "ConstantValue",
                    current_node.name,
                    args))                            
            elif current_node.bl_idname == "Prefab":
                f.write("    {} = {}.addChild({}(name='{}' {}))\n".format(
                    local_name,
                    parent, 
                    current_node.type.name,
                    current_node.name,
                    args))                
            elif current_node.bl_idname == "NodeFrame":
                f.write("    {} = {}.addChild('{}')\n".format(
                    local_name,
                    parent, 
                    current_node.name))                
            else:
                f.write("    {} = {}.addObject('{}', name='{}' {})\n".format(
                    local_name,
                    parent, 
                    current_node.bl_idname,
                    current_node.name,
                    args))

        for current_node in sorted_list_of_nodes:
            if current_node.bl_idname == "Prefab Output":
                for input_socket in current_node.inputs:
                    f.write("    self.findData('{}').setParent({}.{}.linkpath)\n".format(input_socket.name, input_socket.links[0].from_socket.node.name, input_socket.links[0].from_socket.name))     

        f.write("    return self\n")
        f.write("\n")
        f.write("""def createScene(root):
    root.addChild({}())""".format(py_nodename))

        f.close()
        return outfilename

class MESH_OT_sofa_prefab_export(bpy.types.Operator):
    """Export a sofa prefab"""

    bl_idname = "sofa.prefab_export"
    bl_label = "Export the selected model to sofa"
    
    def get_controller_name(self, name):
        if name.endswith(".py"):
            return name[:-3]
        return name
    
    def build_dag(self, node_tree, node):
        try:
            return build_dag(self, node_tree, node)
        except Exception as e:
            def draw_error(self, context):
                self.layout.label(text=f"Error: {str(e)}")
            bpy.context.window_manager.popup_menu(draw_error, title="Erreur", icon='ERROR')
            raise e

    def export_controller_to(self, name):
        """Export a controller from the Blender text panel. 
           The filename is deduced from the name"""
        if name in bpy.data.texts:
            text = bpy.data.texts[name].as_string()
        elif name+".py" in bpy.data.texts:
            text = bpy.data.texts[name+".py"].as_string()
        
        if name.endswith(".py"):
            filename = name
        else:
            filename = name+".py"
                        
        with open(filename,"wt") as w:
            w.write(text)

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
class NODE_OT_sofa_scene_import(bpy.types.Operator, ImportHelper):
    """Import a SOFA scene"""

    bl_idname = "sofa.scene_import"
    bl_label = "Import a SOFA scene"
    
    filename_ext = ".scn"
    filter_glob: bpy.props.StringProperty(default="*.scn", options={'HIDDEN'})

    def execute(self, context):        
        self.report({'INFO'}, 'New SOFA model has been loaded in {}'.format(context.filepath))
        return {"FINISHED"}
  

class MESH_OT_sofa_export(MESH_OT_sofa_prefab_export):
    """Open firefox"""

    bl_idname = "sofa.export"
    bl_label = "Export"

    def execute(self, context):
        node_tree = context.space_data.node_tree
        output_filename = self.build_dag(node_tree, node_tree.nodes.active)            
        
        self.report({'INFO'}, 'Current Sofa model has been saved in {}'.format(output_filename))
        
        return {"FINISHED"}

class MESH_OT_sofa_prefab_run(MESH_OT_sofa_prefab_export):
    """Run the prefab in runSofa"""

    bl_idname = "sofa.prefab_run"
    bl_label = "Execute the prefab in sofa"

    def execute(self, context):
        node_tree = context.space_data.node_tree
        output_filename = self.build_dag(node_tree, node_tree.nodes.active)            
        
        self.report({'INFO'}, 'Starting: runSofa {} -i'.format(output_filename))
        #subprocess.Popen(["runSofa", "-l", "SofaImGui,SofaPython3",  output_filename, "-i"]) 
        subprocess.Popen(["runSofa", "-l", "SofaImGui,SofaPython3", output_filename]) 
            
        return {"FINISHED"}

class MESH_OT_firefox_open(MESH_OT_sofa_prefab_export):
    """Open firefox"""

    bl_idname = "firefox.open"
    bl_label = "Open firefox on the corresponding help page"

    def execute(self, context):
        subprocess.Popen(["firefox", "-new-tab", "https://sofapython3.readthedocs.io/en/latest/content/modules/Sofa/index.html#"]) 
        return {"FINISHED"}

class NODE_OT_add_dynamic_input(bpy.types.Operator):
    bl_idname = "node.add_dynamic_input"
    bl_label = "Open firefox on the corresponding help page"

    def execute(self, context):
        node = context.node
        node.inputs.new("NodeSocketFloat", f"Value {len(node.inputs)}")
        return {'FINISHED'}



class NODE_OT_add_dynamic_socket(bpy.types.Operator):
    bl_idname = "node.add_dynamic_socket"
    bl_label = "Add Input"

    node_name: bpy.props.StringProperty()

    def execute(self, context):
        tree = context.space_data.edit_tree
        node = tree.nodes.get(self.node_name)

        if not node:
            return {'CANCELLED'}

        # suppression du "+"
        plus = node.inputs[-1]
        node.inputs.remove(plus)

        # création du vrai socket
        node.inputs.new(
            "NodeSocketFloat",
            f"Value {len(node.inputs)+1}"
        )

        # recréation du "+"
        node.inputs.new("NodeSocketAdd", "")

        return {'FINISHED'}

class NODE_OT_my_search_popup(bpy.types.Operator):
    bl_idname = "node.my_search_popup"
    bl_label = "Search Item"
    bl_property = "value"

    node_classname : bpy.props.StringProperty()
    node_name : bpy.props.StringProperty()
    is_input : bpy.props.BoolProperty()

    def get_items(self, context):
        creator = [("CREATE", "New socket ...", "Creates a new socket field")]
        template = [("TEMPLATE", "template", "Specifies the internal type of object")]
        
        node_classname = self.node_classname
        if node_classname is None:
            return creator + template
        classcreator = sofainfos.get_creator(node_classname)
        if classcreator:
            return creator + classcreator + template 
        return creator + template

    def get_non_existing_items(self, context):
        node_tree = context.space_data.edit_tree
        node = node_tree.nodes.get(self.node_name)
        items = NODE_OT_my_search_popup.get_items(self, context)
        filtered = []
        for item in items:
            if item[0] == "CREATE":
                filtered.append(item)
            else:
                name = "template" if item[0] == "TEMPLATE" else item[0] 
                if not socket_name_exists(name, node.inputs if self.is_input else node.outputs):
                    filtered.append(item)
        return filtered
    
    value : bpy.props.EnumProperty(name="value", items=get_non_existing_items)
    

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        node_tree = context.space_data.edit_tree
        node = node_tree.nodes.get(self.node_name)
        if not node:
            return {"FINISHED"} 

        name = node_generate_new_socket_name(node, "new_socket", self.is_input)

        if self.value == "CREATE":
            bpy.ops.node.panel_add_socket('INVOKE_DEFAULT', 
                                          socket_name = name, 
                                          socket_side="INPUT" if self.is_input else "OUTPUT")
            return {'FINISHED'}
        if self.value == "TEMPLATE":
            bpy.ops.node.add_template('INVOKE_DEFAULT',  
                                     socket_side="INPUT" if self.is_input else "OUTPUT")
            return {'FINISHED'}
        
        # Query a sofa data type from a pair composed of (classname,dataname)
        sofa_data_type = sofainfos.get_datatype(self.node_classname, self.value)
        value = sofainfos.get_default_value(self.node_classname, self.value)
        node_create_socket(self.value, self.is_input, datatype_to_sockettype(sofa_data_type), value, node)
        return {'FINISHED'}

    def draw(self, context):
        self.layout.prop(self, "value", text="")

class NODE_OT_search_sofa_type_popup(bpy.types.Operator):
    """Search among the list of available Sofa Component"""
    bl_idname = "node.search_sofa_type_popup"
    bl_label = "Search Component"
    bl_property = "value"

    node_name : bpy.props.StringProperty()
    
    @staticmethod
    def get_items():
        """Returns a dynamic list of component that can be searched from"""
        creator = [("CREATE", "New component ...", "Creates a new component")]
        
        for name in sofainfos.get_components():
            creator.append((name, name, ""))

        return creator
    list_of_items = get_items() 
        
    value : bpy.props.EnumProperty(name="value", items=list_of_items)
    
    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        node_tree = context.space_data.edit_tree
        node = node_tree.nodes.get(self.node_name)

        print("YO LO")
        if not node:
            return {"FINISHED"} 

        print(f"SETTING THE TYPE: {self.value}")
        node.type = self.value

        return {'FINISHED'}

def my_socket_menu(self, context):
    node = context.node
    socket = context.socket
    if not node or not socket:
        return
    # Ajouter une entrée
    op = self.layout.operator("node.remove_socket", text="Remove Socket (Custom)")
    op.node_name = node.name
    op.socket_name = socket.name

# Opérateur pour supprimer le socket
class NODE_OT_remove_socket(bpy.types.Operator):
    bl_idname = "node.remove_socket"
    bl_label = "Remove Socket"

    node_name: bpy.props.StringProperty()
    socket_name: bpy.props.StringProperty()

    def execute(self, context):
        node_tree = context.space_data.edit_tree
        node = node_tree.nodes.get(self.node_name)
        if not node:
            return {'CANCELLED'}
        socket = node.inputs.get(self.socket_name) or node.outputs.get(self.socket_name)
        if socket:
            if socket.is_input:
                node.inputs.remove(socket)
            else:
                node.outputs.remove(socket)
        return {'FINISHED'}

class NODE_OT_panel_remove_socket(bpy.types.Operator):
    bl_idname = "node.panel_remove_socket"
    bl_label = "Remove socket"
    bl_options = {'UNDO'}

    socket_index: bpy.props.IntProperty()
    socket_type : bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        node = context.active_node
        return node and (hasattr(node, "inputs") or hasattr(node, "outputs"))

    def execute(self, context):
        node = context.active_node
        
        if self.socket_type == "INPUT":
            sockets = node.inputs
        else:
            sockets = node.outputs 

        try:
            socket = sockets[self.socket_index]
        except IndexError:
            return {'CANCELLED'}

        if socket.is_linked:
            tree = context.space_data.edit_tree
            for link in list(socket.links):
                tree.links.remove(link)

        sockets.remove(socket)
        return {'FINISHED'}

class NODE_OT_panel_add_socket(bpy.types.Operator):
    bl_idname = "node.panel_add_socket"
    bl_label = "Add Socket"
    bl_options = {'REGISTER', 'UNDO'}

    socket_name: bpy.props.StringProperty(name="Name", default="NewSocket")
    socket_type: bpy.props.EnumProperty(name="Type", items=SOCKET_TYPES, default='NodeSocketFloat')
    socket_side :bpy.props.EnumProperty(name="Direction", 
                                        items=[("INPUT","Input",""),("OUTPUT","Output","")], default="INPUT") 

    @classmethod
    def poll(cls, context):
        node = context.active_node
        return node and hasattr(node, "inputs")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        node = context.active_node

        if self.socket_side == "INPUT":
            target = node.inputs
        else: 
            target = node.outputs

        if socket_name_exists(self.socket_name, target): 
            return {'CANCELLED'}

        target.new(type=self.socket_type, name=self.socket_name)
        target.move(len(target) - 1, len(target) - 2)
        return {'FINISHED'}

class NODE_OT_add_template(bpy.types.Operator):
    bl_idname = "node.add_template"
    bl_label = "Add template"
    bl_options = {'REGISTER', 'UNDO'}

    #socket_name: bpy.props.StringProperty(name="Name", default="NewSocket")
    socket_type: bpy.props.EnumProperty(name="Type", items=TEMPLATE_TYPES, default='SofaTemplateSocket')
    socket_side :bpy.props.EnumProperty(name="Direction", 
                                        items=[("INPUT","Input",""),("OUTPUT","Output","")], default="INPUT") 

    @classmethod
    def poll(cls, context):
        node = context.active_node
        return node and hasattr(node, "inputs")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        node = context.active_node

        if self.socket_side == "INPUT":
            target = node.inputs
        else: 
            target = node.outputs

        if socket_name_exists("template", target): 
            return {'CANCELLED'}

        target.new(type=self.socket_type, name="template")
        target.move(len(target) - 1, len(target) - 2)
        return {'FINISHED'}

def register():
    bpy.utils.register_class(NODE_OT_sofa_scene_import)
    bpy.utils.register_class(MESH_OT_sofa_export)
    bpy.utils.register_class(MESH_OT_sofa_prefab_export)
    bpy.utils.register_class(MESH_OT_sofa_prefab_run)
    bpy.utils.register_class(MESH_OT_firefox_open)
    bpy.utils.register_class(NODE_OT_add_dynamic_input)
    bpy.utils.register_class(NODE_OT_add_dynamic_socket)
    bpy.utils.register_class(NODE_OT_my_search_popup)
    bpy.utils.register_class(NODE_OT_search_sofa_type_popup)
    bpy.utils.register_class(NODE_OT_remove_socket)
    bpy.utils.register_class(NODE_OT_panel_remove_socket)
    bpy.utils.register_class(NODE_OT_panel_add_socket)
    bpy.utils.register_class(NODE_OT_add_template)
    
def unregister():
    bpy.utils.unregister_class(NODE_OT_sofa_scene_import)
    bpy.utils.unregister_class(MESH_OT_sofa_prefab_export)
    bpy.utils.unregister_class(MESH_OT_sofa_prefab_run)
    bpy.utils.unregister_class(MESH_OT_firefox_open)
    bpy.utils.unregister_class(NODE_OT_my_search_popup)
    bpy.utils.unregister_class(NODE_OT_search_sofa_type_popup)
    bpy.utils.unregister_class(NODE_OT_panel_remove_socket)
    bpy.utils.unregister_class(NODE_OT_panel_add_socket)
    bpy.utils.unregister_class(NODE_OT_add_template)
    
