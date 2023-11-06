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