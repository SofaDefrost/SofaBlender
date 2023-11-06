# SOFABlender

A project about having co-operation between Sofa and Blender. 

Once the blender plugin is activated in the blender interface. 
User has the choice between to way to have sofa and blender to interact. 

# Client-server's mode 
This solution transmit the data over a network connexion.
A dedicated component must be added to the scene in charge of streaming the simulation data over the network.
This component is implemented in c++ and compiled as a binary plugin for Sofa.  

# Disk baking solution. 
Instead to transmit data over a network connexion between Sofa and Blender it is alternatively 
possible to bake (compute) Sofa simulation and store the simulation data on disk. 
The current implementation is using python and thus works with the binary releases of Sofa 23.12. 

features:
- export meshes from simulation (OGLModel) as well as other data fields (eg: forces, stiffness, vonMisesStress), 
- control of the exported objects by type and scene graph path  
- control of the simulation framerate: eg 24 fps,
- control of the time reference used: wall-clock time (runtime/real time) or simulation time

In order to have best performances it is recommended to install the orjson python library. 
If the library is not available on the system, then the default python json library will be used. 

Baking a simulation
-------------------
To bake the "TetrahedronFEMForceField.scn" into the 'output_dir' you need to start Sofa the following way
```
runSofa blender-exporter.py --argv filename=/path/to/scene/TetrahedronFEMForceField.scn --argv basedir=output_dir 
```

Extra parameters are possible as in:
```
runSofa blender-exporter.py --argv filename=/home/dmarchal/projects/dev/sofa1/sofa/examples/Component/SolidMechanics/FEM/TetrahedronFEMForceField.scn --argv fps=24 --argv basedir=caduceus2  --argv selection=tetrahedronforcefield.json
```

The extra parameters are the following:
- fps=24 to specify the framerate to use for the baking. It is recommended to use the same framerate as the one used in blender. 
- selection=tetrahedronforcefield.json to specifiy the configuration file describing the field to bake. 

Configuration files looks likes the following:
```json
[
    {
        "classname" : "MechanicalObject",
        "pathname" : "*",
        "datafield" : "*"
    },
    {
        "classname" : "TetrahedronFEMForceField",
        "pathname" : "*",
        "datafield" : "vonMisesPerNode, vonMisesStressColors"
    },
    {
        "classname" : "TetrahedronSetTopologyContainer",
        "pathname" : "*",
        "datafield" : "triangles"
    }
]
```
This files specify that the baking process will save:
- all the MechanicalObject's position datafields, 
- all the TetrahedronFEMForceField's vonMisesPerNode and vonMisesStressColors datafields
- all the TetrahedronSetTopologyContainer's triangles datafields. 

When the selection parameter is not provided in the command line the following filtering rules are used: 
```json
 [{
            "classname" : "MechanicalObject",
            "pathname" : "*",
            "datafield" : "*"
            },{
            "classname" : "OglModel",
            "pathname" : "*",
            "datafield" : "*"
            }]
```

When the simulation is done, a directory "output_dir" should be created, ready for import in blender. 


Importing a simulation in blender
---------------------------------
To import a simulation in blender you first need to activate the SofaBlender plugins.
Then go the "scene" panel to select and import the directories containing the simulation datas, multiple simulation's can be imported. 

