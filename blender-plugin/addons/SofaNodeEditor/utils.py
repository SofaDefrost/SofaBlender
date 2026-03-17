import inspect
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
  return module

import re

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

class PathType(Enum):
    ABSOLUTE = "absolute"
    RELATIVE = "relative"

@dataclass
class Address:
    path_type: PathType
    segments: List[str]
    up_levels: int = 0        # nombre de ../
    data: Optional[str] = None

from pathlib import PurePosixPath
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class PathType(Enum):
    ABSOLUTE = "absolute"
    RELATIVE = "relative"


@dataclass
class Address:
    path_type: PathType
    segments: List[str]
    data: Optional[str] = None

def resolve_absolute_adress(tree, address):
    todo
    print("RESOLUTE ABSOLUTE ", address)

def resolve_relative_adress(node, address):
    todo
    print("RESOLUTE ABSOLUTE ", address)

def resolver_adress(tree, node, address : Address):
    if address.path_type == PathType.ABSOLUTE:
        return resolve_absolute_adress(tree, address)
    return resolve_relative_adress(node, address)

class AddressParser:
    def parse(self, text: str) -> Address:
        if not text.startswith("@"):
            raise ValueError("Address must start with '@'")

        body = text[1:]

        # normalisation avec PurePosixPath
        normalized = PurePosixPath(body)

        if normalized.is_absolute():
            path_type = PathType.ABSOLUTE
        else:
            path_type = PathType.RELATIVE

        # collapse des . et ..
        normalized = normalized.resolve() if False else normalized

        # ATTENTION : PurePosixPath ne collapse pas vraiment sans filesystem
        # Donc on force via .parts en reconstruisant

        collapsed = PurePosixPath("/").joinpath(normalized).relative_to("/")

        segments = [p for p in collapsed.parts if p not in (".",)]

        data = None
        if "." in segments[-1]:
            segments[-1], data = segments[-1].rsplit(".", 1)
            
        return Address(
            path_type=path_type,
            segments=segments,
            data=data
        )

class MockNode(object):
    pass

class MockTree(object):
  def __init__(self):
      self.storage = {}

  def add_content(self, path):
      elements = path.split("/")

      tmp = self.storage
      for element in elements:
        if element not in tmp:
          tmp[element] = {}
        tmp = tmp[element]    

if __name__ == "__main__":
  parser = AddressParser()
  print(parser.parse("@/theroot/child1/object"))
  print(parser.parse("@./object1"))
  print(parser.parse("@../../object2"))
  print(parser.parse("@../../object2.position"))

  fake_tree = MockTree()
  fake_tree.add_content("/theroot/child1/object")
  fake_tree.add_content("/theroot/child1/object2")
  fake_tree.add_content("/theroot/child2/object")
  fake_tree.add_content("/child4/object")

  print(fake_tree.storage)

  resolve_absolute_adress(fake_tree, parser.parse("@/theroot/child1/object"))