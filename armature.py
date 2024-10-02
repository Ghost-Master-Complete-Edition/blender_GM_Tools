import bpy

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
              
def register():
    bpy.utils.register_class(ARMATURE_OT_SetHeadbone)
    bpy.utils.register_class(ARMATURE_OT_SetChainpoint)  # Register Set Chainpoint Operator
    bpy.utils.register_class(ARMATURE_OT_SetSpellPoint)  # Register Set SpellPoint Operator

def unregister():
    bpy.utils.unregister_class(ARMATURE_OT_SetHeadbone)
    bpy.utils.unregister_class(ARMATURE_OT_SetChainpoint)  # Unregister Set Chainpoint Operator
    bpy.utils.unregister_class(ARMATURE_OT_SetSpellPoint)  # Unregister Set SpellPoint Operator

if __name__ == "__main__":
    register()