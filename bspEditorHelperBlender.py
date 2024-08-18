bl_info = {
    "name": "Ghost Master Helper",
    "blender": (4, 2, 0),  # Updated to Blender 4.2
    "category": "Object",
    "author": "Patatifique",
    "description": "Plugin for Blender 4.2, various functions to help working with Ghost Master.",
}

import bpy

def get_next_render_flag_index(obj):
    """Finds the next available index for the RENDER_FLAGS property."""
    index = 0
    while f"RENDER_FLAGS{index}" in obj:
        index += 1
    return index

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

class ARMATURE_OT_SetChainpoint(bpy.types.Operator):
    """Set selected bone's NullBoxes property to CHAINPOINT"""
    bl_idname = "armature.set_chainpoint"
    bl_label = "Set Chainpoint"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        if obj and obj.type == 'ARMATURE' and context.active_bone:
            bone_name = context.active_bone.name

            # Apply to Pose mode bone
            if bone_name in obj.pose.bones:
                pose_bone = obj.pose.bones[bone_name]
                pose_bone["NullBoxes"] = "CHAINPOINT"

            # Temporarily switch to Edit mode to modify the Edit mode bone
            bpy.ops.object.mode_set(mode='EDIT')
            if bone_name in obj.data.edit_bones:
                edit_bone = obj.data.edit_bones[bone_name]
                edit_bone["NullBoxes"] = "CHAINPOINT"
            # Switch back to Pose mode
            bpy.ops.object.mode_set(mode='POSE')

        else:
            self.report({'WARNING'}, "No active bone selected in Pose or Edit mode")
        return {'FINISHED'}

class ARMATURE_OT_SetSpellPoint(bpy.types.Operator):
    """Set selected bone's NullBoxes property to SPELLPOINT"""
    bl_idname = "armature.set_spellpoint"
    bl_label = "Set SpellPoint"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.object
        if obj and obj.type == 'ARMATURE' and context.active_bone:
            bone_name = context.active_bone.name

            # Apply to Pose mode bone
            if bone_name in obj.pose.bones:
                pose_bone = obj.pose.bones[bone_name]
                pose_bone["NullBoxes"] = "SPELLPOINT"

            # Temporarily switch to Edit mode to modify the Edit mode bone
            bpy.ops.object.mode_set(mode='EDIT')
            if bone_name in obj.data.edit_bones:
                edit_bone = obj.data.edit_bones[bone_name]
                edit_bone["NullBoxes"] = "SPELLPOINT"
            # Switch back to Pose mode
            bpy.ops.object.mode_set(mode='POSE')

        else:
            self.report({'WARNING'}, "No active bone selected in Pose or Edit mode")
        return {'FINISHED'}

class OBJECT_OT_SetFloorProperty(bpy.types.Operator):
    """Set Selected objects Floor tags based on currently viewed floors"""
    bl_idname = "object.set_floor_property"
    bl_label = "Set Floor"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        selected_objects = context.selected_objects
        visible_floors = []

        # Gather all visible floors based on the current floor view settings
        if context.scene.show_floor_1:
            visible_floors.append('1')
        if context.scene.show_floor_2:
            visible_floors.append('2')
        if context.scene.show_floor_3:
            visible_floors.append('3')
        if context.scene.show_floor_4:
            visible_floors.append('4')
        if context.scene.show_floor_5:
            visible_floors.append('5')
        if context.scene.show_floor_6:
            visible_floors.append('6')

        # Set the FLOORS property for each selected object
        floors_value = ','.join(visible_floors)
        for obj in selected_objects:
            obj["FLOORS"] = floors_value

        return {'FINISHED'}

class GHOST_MASTER_HELPER_PT_GeneralPanel(bpy.types.Panel):
    # Creates the main panel
    bl_label = "Ghost Master Helper General"
    bl_idname = "GHOST_MASTER_HELPER_PT_general_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Ghost Master Helper"

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
            col.operator("armature.set_chainpoint", text="Set Chainpoint")
            col.operator("armature.set_spellpoint", text="Set SpellPoint")

class GHOST_MASTER_HELPER_PT_MapEditingPanel(bpy.types.Panel):
    # Creates the map editing panel
    bl_label = "Map Editing"
    bl_idname = "GHOST_MASTER_HELPER_PT_map_editing_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Ghost Master Helper"

    # Define properties
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

        # Map Editing Panel
        col = layout.column(align=True)
        col.prop(scene, "show_ice_layer", text="Show Ice Layer", toggle=True)
        col.prop(scene, "show_invisible_flag", text="Show Invisible Flag", toggle=True)

        # Add a separator (space) between "Show Invisible Flag" and "Current Floor View"
        layout.separator()

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

        # Add a separator (space) before the "Set Floor" button
        layout.separator()
        
        # Set Floor Button
        layout.operator("object.set_floor_property", text="Set Floor")

def register():
    bpy.utils.register_class(OBJECT_OT_AddLightableProperty)
    bpy.utils.register_class(OBJECT_OT_AddDoubleSidedProperty)
    bpy.utils.register_class(ARMATURE_OT_SetHeadbone)
    bpy.utils.register_class(ARMATURE_OT_SetChainpoint)  # Register Set Chainpoint Operator
    bpy.utils.register_class(ARMATURE_OT_SetSpellPoint)  # Register Set SpellPoint Operator
    bpy.utils.register_class(OBJECT_OT_SetFloorProperty)  # Register Set Floor Operator
    bpy.utils.register_class(GHOST_MASTER_HELPER_PT_GeneralPanel)
    bpy.utils.register_class(GHOST_MASTER_HELPER_PT_MapEditingPanel)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_AddLightableProperty)
    bpy.utils.unregister_class(OBJECT_OT_AddDoubleSidedProperty)
    bpy.utils.unregister_class(ARMATURE_OT_SetHeadbone)
    bpy.utils.unregister_class(ARMATURE_OT_SetChainpoint)  # Unregister Set Chainpoint Operator
    bpy.utils.unregister_class(ARMATURE_OT_SetSpellPoint)  # Unregister Set SpellPoint Operator
    bpy.utils.unregister_class(OBJECT_OT_SetFloorProperty)  # Unregister Set Floor Operator
    bpy.utils.unregister_class(GHOST_MASTER_HELPER_PT_GeneralPanel)
    bpy.utils.unregister_class(GHOST_MASTER_HELPER_PT_MapEditingPanel)

if __name__ == "__main__":
    register()
