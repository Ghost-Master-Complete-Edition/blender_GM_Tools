import bpy
from .map_editing import update_ice_layer_visibility
from .map_editing import update_invisible_flag_visibility
from .map_editing import update_floor_visibility

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

        # Button to Set Specular Tint to Black
        layout.operator("object.set_specular_tint_to_black", text="Set Specular Tint to Black")

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

class GHOST_MASTER_HELPER_PT_GhostMasterAnimationPanel(bpy.types.Panel):
    """Creates IK setup for Ghost Master rig"""
    bl_label = "Ghost Master Animation"
    bl_idname = "OBJECT_PT_ghost_master_anim"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Ghost Master Helper'

    def draw(self, context):
        layout = self.layout
        layout.operator("object.ghost_master_ik", text="Rig Setup")
        
        # Add button for FKIK switch
        layout.operator("object.switch_fk_ik", text="Switch FK/IK")

        # Add button for Delete rig Setup
        layout.operator("object.delete_rig_setup", text="Delete Rig Setup")

        
def register():
    bpy.utils.register_class(GHOST_MASTER_HELPER_PT_GeneralPanel)
    bpy.utils.register_class(GHOST_MASTER_HELPER_PT_MapEditingPanel)
    bpy.utils.register_class(GHOST_MASTER_HELPER_PT_GhostMasterAnimationPanel)

def unregister():
    bpy.utils.unregister_class(GHOST_MASTER_HELPER_PT_GeneralPanel)
    bpy.utils.unregister_class(GHOST_MASTER_HELPER_PT_MapEditingPanel)
    bpy.utils.unregister_class(GHOST_MASTER_HELPER_PT_GhostMasterAnimationPanel)

if __name__ == "__main__":
    register()
