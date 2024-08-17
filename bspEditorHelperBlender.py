bl_info = {
    "name": "BSP Editor Helper",
    "blender": (4, 2, 0),  # Updated to Blender 4.2
    "category": "Object",
    "author": "Patatifique",
    "description": "Adds dynamically named render flags and armature flags to selected objects and bones.",
}

import bpy

def get_next_render_flag_index(obj):
    """Get the next available render flag index for the given object."""
    index = 1
    while f"RENDERFLAGS{index}" in obj:
        index += 1
    return index

class OBJECT_OT_AddLightableProperty(bpy.types.Operator):
    """Add the next available RENDERFLAGS property with the value RUNTIME_LIGHTABLE"""
    bl_idname = "object.add_lightable_property"
    bl_label = "Lightable"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = context.selected_objects
        for obj in selected_objects:
            index = get_next_render_flag_index(obj)
            obj[f"RENDERFLAGS{index}"] = "RUNTIME_LIGHTABLE"
        return {'FINISHED'}

class OBJECT_OT_AddDoubleSidedProperty(bpy.types.Operator):
    """Add the next available RENDERFLAGS property with the value DOUBLE_SIDED"""
    bl_idname = "object.add_double_sided_property"
    bl_label = "Double Sided"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = context.selected_objects
        for obj in selected_objects:
            index = get_next_render_flag_index(obj)
            obj[f"RENDERFLAGS{index}"] = "DOUBLE_SIDED"
        return {'FINISHED'}

class ARMATURE_OT_SetHeadbone(bpy.types.Operator):
    """Rename the selected bone to MDL-jnt-HEADBONE"""
    bl_idname = "armature.set_headbone"
    bl_label = "Set Headbone"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        if obj and obj.type == 'ARMATURE' and context.active_bone:
            bone = context.active_bone
            bone.name = "MDL-jnt-HEADBONE"
        else:
            self.report({'WARNING'}, "No active bone selected in Pose or Edit mode")
        return {'FINISHED'}

class BSP_EDITOR_HELPER_PT_Panel(bpy.types.Panel):
    """Creates a Panel in the Top Bar next to Item, Tool, View"""
    bl_label = "BSP Editor Helper"
    bl_idname = "BSP_EDITOR_HELPER_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BSP Editor"

    # Define properties
    bpy.types.Scene.use_render_flags = bpy.props.BoolProperty(name="Render Flags", default=False)
    bpy.types.Scene.use_armature_flags = bpy.props.BoolProperty(name="Armature", default=False)

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Render Flags Panel
        row = layout.row()
        row.prop(scene, "use_render_flags", text="Render Flags", icon="TRIA_DOWN" if scene.use_render_flags else "TRIA_RIGHT", emboss=False)
        if scene.use_render_flags:
            col = layout.column(align=True)
            col.operator("object.add_lightable_property", text="Lightable")
            col.operator("object.add_double_sided_property", text="Double Sided")

        # Armature Panel
        row = layout.row()
        row.prop(scene, "use_armature_flags", text="Armature", icon="TRIA_DOWN" if scene.use_armature_flags else "TRIA_RIGHT", emboss=False)
        if scene.use_armature_flags:
            col = layout.column(align=True)
            col.operator("armature.set_headbone", text="Set Headbone")

def register():
    bpy.utils.register_class(OBJECT_OT_AddLightableProperty)
    bpy.utils.register_class(OBJECT_OT_AddDoubleSidedProperty)
    bpy.utils.register_class(ARMATURE_OT_SetHeadbone)
    bpy.utils.register_class(BSP_EDITOR_HELPER_PT_Panel)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_AddLightableProperty)
    bpy.utils.unregister_class(OBJECT_OT_AddDoubleSidedProperty)
    bpy.utils.unregister_class(ARMATURE_OT_SetHeadbone)
    bpy.utils.unregister_class(BSP_EDITOR_HELPER_PT_Panel)

if __name__ == "__main__":
    register()
