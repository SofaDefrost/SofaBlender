import bpy
import graphlib
import subprocess

class MESH_OT_sofa_prefab_export(bpy.types.Operator):
    """Export a sofa prefab"""

    bl_idname = "sofa.prefab_export"
    bl_label = "Export the selected model to sofa"
    
    def get_controller_name(self, name):
        if name.endswith(".py"):
            return name[:-3]
        return name
    
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
    
    def build_dag(self, node_tree, node):

        # Build a name without . because Sofa is not supposed to use that kind of name        
        py_nodename = node_tree.name.replace(".","_") 
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
            if current_node.bl_idname == "BlenderController":
                controller_instances.append(current_node)
                    
        imports = ""
        already_imported = {}
        for prefab_instance in prefab_instances:
            prefab_name = prefab_instance.type
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
        f.write(imports)
        f.write("\n")

        kwargs=""        
        for inputs in node_tree.inputs:
            kwargs += " {}={},".format(inputs.name, repr(inputs.default_value[:]))  
                
        f.write("def {}(name='{}',{}):\n".format(py_nodename, py_nodename, kwargs[:-1]))
        f.write("    self = Sofa.Core.Node(name)\n")

        for current_node in sorted_list_of_nodes:
            if current_node.bl_idname == "Prefab Input":
                for output_socket in current_node.outputs:
                    type = "string"
                    if output_socket.bl_idname == "NodeSocketVector":
                        type = "Vec3d" 
                    if output_socket.bl_idname != "SofaObjectSocket":                       
                        f.write("    self.addData(name='{}', type='{}', help='', default={})\n".format(output_socket.name, type, output_socket.name))     
                    print("===>",output_socket.bl_idname)    
            if current_node.bl_idname == "Prefab Output":
                for input_socket in current_node.inputs:
                    f.write("    self.addData(name='{}', type='{}', help='')\n".format(input_socket.name, "string"))     
            
        for current_node in sorted_list_of_nodes:
            if current_node.bl_idname == "Prefab Input":
                continue

            if current_node.bl_idname == "Prefab Output":
                continue 

            if current_node.bl_idname == "BlenderController":
                blender_name = self.get_controller_name(current_node.type)
                print("Generating sofa controller from blender ",blender_name)
                self.export_controller_to(blender_name) 
                
            if current_node.bl_idname == "BlenderObject":
                blender_name = current_node.inputs["blender object"].default_value
                blender_object = bpy.context.scene.objects[blender_name]
                
                bpy.ops.object.select_all(action='DESELECT')
                bpy.data.objects[blender_name].select_set(True)
                
                filename = blender_name+".obj"
                bpy.ops.export_scene.obj(filepath=filename, use_selection=True, use_uvs=True, use_materials=True)
                
                for o in current_node.outputs:
                    print("NODE OUTPUTE ", o) 
                
                current_node.outputs["filename"].value = filename
                current_node.outputs["location"].default_value = blender_object.location
                current_node.outputs["orientation"].default_value = blender_object.rotation_euler
                current_node.outputs["scale"].default_value = blender_object.scale                
                
                print("        save special blender object values is ", current_node.outputs["filename"].value)
                continue
                
            args = ""
            for input in current_node.inputs:
                if len(input.links) > 0:
                    for link in input.links:
                        if link.from_socket.bl_idname != "SofaBlenderSocket":
                            if link.from_socket.bl_idname == "SofaSelfSocket":
                                args += ", " + input.name + "=" + str(link.from_node.name) + ".linkpath"
                            elif link.from_socket.node.bl_idname == "BlenderObject":
                                args += ", {}={}".format(input.name, repr(list(link.from_socket.default_value)))                                                    
                            else:
                                args += ", " + input.name + "=" + str(link.from_node.name) + "." + str(link.from_socket.name) + ".linkpath"        
                        else:
                            print("         DUMPING BlenderSocket", dir(link.from_socket))
                            args += ", {}='{}'".format(input.name, str(link.from_socket.value))                        
                else:        
                    if hasattr(input, "default_value"):
                        if input.default_value != "":
                            args += ", " + input.name + "=" + repr(input.default_value[:]) 
                            
            #print("TEST" , dir(current_node))
            #for input in current_node.properties:
            #    for link in input.links:
            #        args += ", " + input.name + "=" + str(link.from_node.name) + ".linkpath"

            if current_node.bl_idname == "BlenderController":
                name = self.get_controller_name(controller_instance.type) 
                name1 = name+"1"
                args=""
                f.write("    {} = self.addObject({}(name='{}' {}))\n".format(
                    name1,
                    name,
                    name1,
                    args))                
            
            # Faites ici ce que vous voulez avec le nœud
            # Par exemple, imprimer son nom :
            elif current_node.bl_idname == "Prefab":
                f.write("    {} = self.addChild({}(name='{}' {}))\n".format(
                    current_node.name+"01",
                    current_node.type,
                    current_node.name,
                    args))                
            else:
                f.write("    {} = self.addObject('{}', name='{}' {})\n".format(
                    current_node.name,
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
        subprocess.Popen(["runSofa", output_filename, "-i"]) 
            
        return {"FINISHED"}

class MESH_OT_firefox_open(MESH_OT_sofa_prefab_export):
    """Open firefox"""

    bl_idname = "firefox.open"
    bl_label = "Open firefox on the corresponding help page"

    def execute(self, context):
        subprocess.Popen(["firefox", "-new-tab", "https://sofapython3.readthedocs.io/en/latest/content/modules/Sofa/index.html#"]) 
        return {"FINISHED"}
        
def register():
    bpy.utils.register_class(MESH_OT_sofa_export)
    bpy.utils.register_class(MESH_OT_sofa_prefab_export)
    bpy.utils.register_class(MESH_OT_sofa_prefab_run)
    bpy.utils.register_class(MESH_OT_firefox_open)

def unregister():
    bpy.utils.unregister_class(MESH_OT_sofa_prefab_export)
    bpy.utils.unregister_class(MESH_OT_sofa_prefab_run)
    bpy.utils.unregister_class(MESH_OT_firefox_open)


