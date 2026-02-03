# -*- coding: utf-8 -*-
import Sofa
import json

def createScene(root):
    with open("dump.json","w+t", encoding="utf-8") as file:
        file.write(Sofa.Core.ObjectFactory.dump_json())