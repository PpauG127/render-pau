"""Load a story: python engine/<tool>.py <story> ...  ->  sets INK_STORY and imports its scenes.py"""
import os, sys, importlib
HERE = os.path.dirname(os.path.abspath(__file__))
def load(name):
    d = os.path.join(os.path.dirname(HERE), "stories", name)
    os.environ["INK_STORY"] = d
    sys.path.insert(0, HERE); sys.path.insert(0, d)
    return importlib.import_module("scenes"), d
