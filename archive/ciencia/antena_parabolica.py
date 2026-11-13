import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from render2 import SCENES as _S
from engine import run
SCENES = list(_S)
SCENES[14] = SCENES[14] + (440,)

if __name__ == "__main__":
    run(SCENES)
