bl_info = {
    "name": "Ghost Master Helper",
    "blender": (4, 2, 0),  # Updated to Blender 4.2
    "category": "Object",
    "author": "Patatifique",
    "description": "Plugin for Blender 4.2, various functions to help working with Ghost Master.",
}

import bpy
from . import panels
from . import armature
from . import flags
from . import map_editing

def register():
    panels.register()
    armature.register()
    flags.register()
    map_editing.register()
    
    
def unregister():
    panels.unregister()
    armature.unregister()
    flags.unregister()
    map_editing.unregister()