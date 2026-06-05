MATERIALS = {
    "plastic_02": {
        "diffuse": [0.8, 0.2, 0.2, 1.0],
        "specular": [1.0, 1.0, 1.0, 1.0],
        "shininess": 80
    }
}

def onLoaded(root):

    node = root.getChild("VisualModel2")
    visual = node.getObject("OglModel")

    mat = MATERIALS["plastic_02"]

    visual.diffuse = mat["diffuse"]
    visual.specular = mat["specular"]
    visual.shininess = mat["shininess"]