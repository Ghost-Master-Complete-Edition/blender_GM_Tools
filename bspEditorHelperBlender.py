bl_info = {
    "name": "BSP Editor Helper",
    "blender": (4, 2, 0),  # Updated to Blender 4.2
    "category": "Object",
    "author": "Patatifique",
    "description": "Plugin for Blender 4.2, various functions to help working with ghost master.",
}

import bpy

def update_ice_layer_visibility(self, context):
    """Update the visibility of objects with 'mat_2pssnow2' material."""
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            for mat_slot in obj.material_slots:
                if mat_slot.material and mat_slot.material.name == "mat_2pssnow2":
                    obj.hide_set(not context.scene.show_ice_layer)

def update_invisible_flag_visibility(self, context):
    """Update the visibility of objects with the 'FLAGS0' custom property set to 'INVISIBLE'."""
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj.get("FLAGS0") == "INVISIBLE":
            obj.hide_set(not context.scene.show_invisible_flag)

def update_floor_visibility(self, context):
    """Update visibility of objects based on their FLOORS property and current floor settings."""
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and "FLOORS" in obj:
            object_floors = obj["FLOORS"].split(',')
            is_visible = (
                (context.scene.show_floor_6 and '6' in object_floors) or
                (context.scene.show_floor_5 and '5' in object_floors) or
                (context.scene.show_floor_4 and '4' in object_floors) or
                (context.scene.show_floor_3 and '3' in object_floors) or
                (context.scene.show_floor_2 and '2' in object_floors) or
                (context.scene.show_floor_1 and '1' in object_floors)
            )
            obj.hide_set(not is_visible)

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
    bpy.types.Scene.use_floor_view = bpy.props.BoolProperty(name="Current Floor View", default=False)

    bpy.types.Scene.show_ice_layer = bpy.props.BoolProperty(name="Show Ice Layer", default=True, update=update_ice_layer_visibility)
    bpy.types.Scene.show_invisible_flag = bpy.props.BoolProperty(name="Show Invisible Flag", default=False, update=update_invisible_flag_visibility)

    bpy.types.Scene.show_floor_1 = bpy.props.BoolProperty(name="Floor 1", default=True, update=update_floor_visibility)
    bpy.types.Scene.show_floor_2 = bpy.props.BoolProperty(name="Floor 2", default=True, update=update_floor_visibility)
    bpy.types.Scene.show_floor_3 = bpy.props.BoolProperty(name="Floor 3", default=True, update=update_floor_visibility)
    bpy.types.Scene.show_floor_4 = bpy.props.BoolProperty(name="Floor 4", default=True, update=update_floor_visibility)
    bpy.types.Scene.show_floor_5 = bpy.props.BoolProperty(name="Floor 5", default=True, update=update_floor_visibility)
    bpy.types.Scene.show_floor_6 = bpy.props.BoolProperty(name="Floor 6", default=True, update=update_floor_visibility)

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
            col.prop(scene, "show_ice_layer", text="Show Ice Layer", toggle=True)
            col.prop(scene, "show_invisible_flag", text="Show Invisible Flag", toggle=True)

        # Current Floor View Panel
        row = layout.row()
        row.prop(scene, "use_floor_view", text="Current Floor View", icon="TRIA_DOWN" if scene.use_floor_view else "TRIA_RIGHT", emboss=False)
        if scene.use_floor_view:
            col = layout.column(align=True)
            col.prop(scene, "show_floor_6", text="Floor 6", toggle=True)
            col.prop(scene, "show_floor_5", text="Floor 5", toggle=True)
            col.prop(scene, "show_floor_4", text="Floor 4", toggle=True)
            col.prop(scene, "show_floor_3", text="Floor 3", toggle=True)
            col.prop(scene, "show_floor_2", text="Floor 2", toggle=True)
            col.prop(scene, "show_floor_1", text="Floor 1", toggle=True)

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
