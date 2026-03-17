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

def addObject(self, type, **kwargs):
    tmp = {}
    for name, value in kwargs.items():
        if value is not None:
            tmp[name] = value
    return self.addObject(type, **tmp)


import zmq
import threading
import queue

message_queue = queue.Queue()

def zmq_listener():

    context = zmq.Context()
    socket = context.socket(zmq.PULL)
    socket.bind("tcp://*:5555")

    while True:
        data = socket.recv_json()
        message_queue.put(data)

thread = threading.Thread(target=zmq_listener, daemon=True)
thread.start()

class SofaBlenderLiveHook(Sofa.Core.Controller):
    def __init__(self, *args, **kwargs):
        Sofa.Core.Controller.__init__(self, *args, **kwargs)
    
    def onEvent(self, event):
        print("EVENT RECEIVED:", event)

    def onIdleEvent(self, event):
        while True:
            try:
                msg = message_queue.get_nowait()
                print("Processing:", msg)
            except queue.Empty:
                pass