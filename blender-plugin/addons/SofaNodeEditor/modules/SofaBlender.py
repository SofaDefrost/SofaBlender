# SofaBlender version 1.0 
import Sofa

python2sofa = {
    "<class 'str'>" : "string",
    "<class 'float'>" : "float"
}

class ConstantValue(Sofa.Core.Controller):
    def __init__(self, *args, **kwargs):
        Sofa.Core.Controller.__init__(self, *args, **kwargs)

        for k,v in kwargs.items():
            if k not in ["name"]:
               self.addData(name=k, type=python2sofa[str(type(v))], help="TODO", default=v) 