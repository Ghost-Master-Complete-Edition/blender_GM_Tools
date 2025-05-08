import bpy

class OBJECT_OT_SetSpecularTintToBlack(bpy.types.Operator):
    """Set specular tint to black for materials of selected objects if the specular tint is white"""
    bl_idname = "object.set_specular_tint_to_black"
    bl_label = "Set Specular Tint to Black"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = context.selected_objects
        for obj in selected_objects:
            if obj.type == 'MESH':
                for mat_slot in obj.material_slots:
                    mat = mat_slot.material
                    if mat and mat.use_nodes:
                        for node in mat.node_tree.nodes:
                            if node.type == 'BSDF_PRINCIPLED':
                                specular_tint = node.inputs['Specular Tint'].default_value
                                print(f"Specular Tint: {specular_tint}")
                                # Check if Specular Tint is white
                                if (specular_tint[0] == 1.0 and
                                    specular_tint[1] == 1.0 and
                                    specular_tint[2] == 1.0):
                                    # Set the tint to black
                                    node.inputs['Specular Tint'].default_value = (0.0, 0.0, 0.0, 1.0)  # RGBA
        return {'FINISHED'}
        
def register():
    bpy.utils.register_class(OBJECT_OT_SetSpecularTintToBlack)
    
def unregister():
    bpy.utils.register_class(OBJECT_OT_SetSpecularTintToBlack)
    
if __name__ == "__main__":
    register()