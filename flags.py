import bpy

def get_next_render_flag_index(obj):
    """Finds the next available index for the RENDER_FLAGS property."""
    index = 0
    while f"RENDER_FLAGS{index}" in obj:
        index += 1
    return index
    
    
class OBJECT_OT_AddLightableProperty(bpy.types.Operator):
    """Set RUNTIME_LIGHTABLE Render Flag"""
    bl_idname = "object.add_lightable_property"
    bl_label = "Lightable"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = context.selected_objects
        for obj in selected_objects:
            index = get_next_render_flag_index(obj)
            obj[f"RENDER_FLAGS{index}"] = "RUNTIME_LIGHTABLE"
        return {'FINISHED'}
        
        
class OBJECT_OT_AddDoubleSidedProperty(bpy.types.Operator):
    """Set DOUBLE_SIDED Render Flag"""
    bl_idname = "object.add_double_sided_property"
    bl_label = "Double Sided"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = context.selected_objects
        for obj in selected_objects:
            index = get_next_render_flag_index(obj)
            obj[f"RENDER_FLAGS{index}"] = "DOUBLE_SIDED"
        return {'FINISHED'}
        
def register():
    bpy.utils.register_class(OBJECT_OT_AddLightableProperty)
    bpy.utils.register_class(OBJECT_OT_AddDoubleSidedProperty)
    
def unregister():
    bpy.utils.unregister_class(OBJECT_OT_AddLightableProperty)
    bpy.utils.unregister_class(OBJECT_OT_AddDoubleSidedProperty)
    
if __name__ == "__main__":
    register()