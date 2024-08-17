bl_info = {
    "name": "BSP Editor Helper",
    "blender": (4, 2, 0),  # Updated to Blender 4.2
    "category": "Object",
    "author": "Patatifique",
    "description": "Plugin for Blender 4.2, various functions to help working with ghost master.",
}

import bpy

def get_next_render_flag_index(obj):
    # Get the next available render flag index for the given object.
    index = 1
    while f"RENDERFLAGS{index}" in obj:
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
            obj[f"RENDERFLAGS{index}"] = "RUNTIME_LIGHTABLE"
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
            obj[f"RENDERFLAGS{index}"] = "DOUBLE_SIDED"
        return {'FINISHED'}

class ARMATURE_OT_SetHeadbone(bpy.types.Operator):
    """Set selected bone as MDL-jnt-HEADBONE"""
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
    # Creates Panel
    bl_label = "BSP Editor Helper"
    bl_idname = "BSP_EDITOR_HELPER_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BSP Editor"

    # Define properties
    bpy.types.Scene.use_render_flags = bpy.props.BoolProperty(name="Render Flags", default=False)
    bpy.types.Scene.use_armature_flags = bpy.props.BoolProperty(name="Armature", default=False)
    bpy.types.Scene.use_map_editing = bpy.props.BoolProperty(name="Map Editing", default=False)
    bpy.types.Scene.show_ice_layer = bpy.props.BoolProperty(name="Show Ice Layer", default=True)
    bpy.types.Scene.show_invisible_flag = bpy.props.BoolProperty(name="Show Invisible Flag", default=False)

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

        # Map Editing Panel
        row = layout.row()
        row.prop(scene, "use_map_editing", text="Map Editing", icon="TRIA_DOWN" if scene.use_map_editing else "TRIA_RIGHT", emboss=False)
        if scene.use_map_editing:
            col = layout.column(align=True)
            col.prop(scene, "show_ice_layer", text="Show Ice Layer")
            col.prop(scene, "show_invisible_flag", text="Show Invisible Flag")

def update_ice_layer_visibility(self, context):
    # Update the visibility of objects with 'mat_2pssnow2' material.
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            for mat_slot in obj.material_slots:
                if mat_slot.material and mat_slot.material.name == "mat_2pssnow2":
                    obj.hide_set(not context.scene.show_ice_layer)

def update_invisible_flag_visibility(self, context):
    # Update the visibility of objects with the 'FLAGS0' custom property set to 'INVISIBLE'.
    for obj in bpy.data.objects:
        if  obj.get("FLAGS0") == "INVISIBLE":
            obj.hide_set(not context.scene.show_invisible_flag)

# Assign the update functions to the properties
bpy.types.Scene.show_ice_layer = bpy.props.BoolProperty(name="Show Ice Layer", default=True, update=update_ice_layer_visibility)
bpy.types.Scene.show_invisible_flag = bpy.props.BoolProperty(name="Show Invisible Flag", default=False, update=update_invisible_flag_visibility)

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
