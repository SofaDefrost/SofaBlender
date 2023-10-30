# SOFABlender

A project about having co-operation between Sofa and Blender. 

Once the blender plugin is activated in the blender interface. 
User has the choice between to way to have sofa and blender to interact. 

# Mode 1:  
Bake simulation data to disk space, no binary plugin, works with binary release of Sofa. 

The general workflow consist in 
- starting blender-activating the blender plugin
- start the sofa simulation using the following command, this command add to the scene a python controller in charge of 
saving the simulation data for later import in blender. 
- in blender, load the dedicated pannel, and import the directory containing the wanted simulation data & click on the import button. 

features:
- can export the meshes from simulation (OGLModel, Container) as well as other data fields (forces, stiffness) 
- control of the simulation framerate: wall clock (real)time, 24 fps, 
- precise control of the type, object and data field to bake. 


# Mode 2: 
In case you don't want and can't store the simulation data on disk or found that the saving performance 
using python component is too slow... a client-server solution is proposed.
This solution transmit the data over a network connexion.
A dedicated component must be added to the scene in charge of streaming the simulation data over the network. 

