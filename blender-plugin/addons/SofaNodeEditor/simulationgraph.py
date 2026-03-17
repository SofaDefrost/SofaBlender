class Data(object):
    name: str
    value : str 
    parent : Data | None 

class Entity(object):
    datas : list[object]
    links : list[Entity] 

class Component(Entity):
    pass 

class Node(Entity):
    children : list[Node]
    objects : list[Component]

def serialize_python(graph):
    return False

