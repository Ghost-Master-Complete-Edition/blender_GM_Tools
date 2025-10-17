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

class OBJECT_OT_SetupAlphaClipMaterial(bpy.types.Operator):
    """Setup a simple alpha clip material from the active object's texture"""
    bl_idname = "object.setup_alpha_clip_material"
    bl_label = "Setup Alpha Clip Material"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj or not obj.active_material:
            self.report({'WARNING'}, "No object with a material selected.")
            return {'CANCELLED'}

        mat = obj.active_material
        mat.use_nodes = True
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        # Find the first image texture node
        tex_node = None
        for node in nodes:
            if node.type == 'TEX_IMAGE':
                tex_node = node
                break

        if not tex_node or not tex_node.image:
            self.report({'WARNING'}, "No image texture found.")
            return {'CANCELLED'}

        img = tex_node.image

        # Check for alpha channel
        if not img.has_data or img.depth < 32:
            self.report({'WARNING'}, "The selected texture has no alpha channel.")
            return {'CANCELLED'}

        # Optional: clear everything except the texture node
        for node in list(nodes):
            if node != tex_node:
                nodes.remove(node)

        # Create new nodes
        bsdf = nodes.new("ShaderNodeBsdfPrincipled")
        bsdf.location = (400, 0)
        less_than = nodes.new("ShaderNodeMath")
        less_than.operation = 'LESS_THAN'
        less_than.location = (0, -200)
        less_than.inputs[1].default_value = 0.5

        subtract = nodes.new("ShaderNodeMath")
        subtract.operation = 'SUBTRACT'
        subtract.location = (200, -200)
        subtract.inputs[0].default_value = 1.0

        output = nodes.new("ShaderNodeOutputMaterial")
        output.location = (600, 0)

        # Link nodes
        links.new(tex_node.outputs['Color'], bsdf.inputs['Base Color'])
        links.new(tex_node.outputs['Alpha'], less_than.inputs[0])
        links.new(less_than.outputs[0], subtract.inputs[1])
        links.new(subtract.outputs[0], bsdf.inputs['Alpha'])
        links.new(bsdf.outputs[0], output.inputs['Surface'])

        self.report({'INFO'}, f"Alpha clip setup created for {img.name}")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(OBJECT_OT_SetSpecularTintToBlack)
    bpy.utils.register_class(OBJECT_OT_SetupAlphaClipMaterial)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_SetSpecularTintToBlack)
    bpy.utils.unregister_class(OBJECT_OT_SetupAlphaClipMaterial)

if __name__ == "__main__":
    register()