import bpy
from mathutils import Vector
import os

# GHOST MASTER AUTORIG KINDA

# Made by Pat on 02/10/2024


class OBJECT_OT_GhostMasterIK(bpy.types.Operator):
    """Creates IK setup for Ghost Master rig"""
    bl_idname = "object.ghost_master_ik"
    bl_label = "Create Ghost Master IK"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = bpy.context.object

        # Ensure that the active object is an armature
        if obj and obj.type == 'ARMATURE':

        #####################################################
        # IK SETUP (for both legs but no arms for now sorry)
        #####################################################

            # Switch to Edit Mode to modify bones
            bpy.ops.object.mode_set(mode='EDIT')

            # Function to set up IK for a given leg (left or right)
            def setup_ik_leg(thighbone_name, shinbone_name, effbone_name, side_prefix):
                # Move the tail of the specified bones to the head of their child bones
                for bone_name in [thighbone_name, shinbone_name]:
                    bone = obj.data.edit_bones.get(bone_name)
                    if bone:
                        children = bone.children
                        if children:
                            child_bone = children[0]
                            bone.tail = child_bone.head
                            print(f"Moved tail of {bone.name} to head of {child_bone.name}.")

                # Create a new bone for Foot IK
                shin_bone = obj.data.edit_bones.get(shinbone_name)
                eff_bone = obj.data.edit_bones.get(effbone_name)
                if shin_bone and eff_bone:
                    ik_bone = obj.data.edit_bones.new(f'{side_prefix}-Foot-Ik')
                    ik_bone.head = eff_bone.head
                    ik_bone.tail = eff_bone.tail
                    ik_bone.roll = eff_bone.roll
                    ik_bone.use_deform = False

                    parent_bone = obj.data.edit_bones.get('MDL-GOD')
                    if parent_bone:
                        ik_bone.parent = parent_bone
                        ik_bone.use_connect = False

                # Create the knee pole vector
                thigh_bone = obj.data.edit_bones.get(thighbone_name)
                if thigh_bone and shin_bone:
                    knee_pos = (thigh_bone.head + shin_bone.tail) / 2
                    knee_offset = Vector((0.0, -0.5, 0.0))
                    pole_position = knee_pos + knee_offset

                    pole_bone = obj.data.edit_bones.new(f'{side_prefix}-Knee-Pole')
                    pole_bone.head = pole_position
                    pole_bone.tail = pole_position + Vector((0.0, 0.2, 0.0))
                    pole_bone.use_deform = False
                    if parent_bone:
                        pole_bone.parent = parent_bone

            # Setup IK for the left leg
            setup_ik_leg('MDL-jnt-L-thighbone', 'MDL-jnt-L-LEG-shin', 'MDL-eff9', 'L')

            # Setup IK for the right leg
            setup_ik_leg('MDL-jnt-R-thighbone', 'MDL-jnt-R-leg-shin', 'MDL-eff23', 'R')

            # Switch back to Object Mode
            bpy.ops.object.mode_set(mode='OBJECT')

            # Add IK constraints for both legs
            def add_constraints(thighbone_name, shinbone_name, foot_eff_name, side_prefix):
                # Add IK constraint to the shin bone
                pbone_shin = obj.pose.bones.get(shinbone_name)
                if pbone_shin:
                    ik_constraint = pbone_shin.constraints.new('IK')
                    ik_constraint.target = obj
                    ik_constraint.subtarget = f'{side_prefix}-Foot-Ik'
                    ik_constraint.pole_target = obj
                    ik_constraint.pole_subtarget = f'{side_prefix}-Knee-Pole'
                    ik_constraint.chain_count = 2
                    ik_constraint.pole_angle = 0  # Adjust this if needed

                # Add Copy Rotation constraint to the foot effector bone
                pbone_foot = obj.pose.bones.get(foot_eff_name)
                if pbone_foot:
                    copy_rot_constraint = pbone_foot.constraints.new('COPY_ROTATION')
                    copy_rot_constraint.target = obj
                    copy_rot_constraint.subtarget = f'{side_prefix}-Foot-Ik'

            # Add constraints for the left leg
            add_constraints('MDL-jnt-L-thighbone', 'MDL-jnt-L-LEG-shin', 'MDL-eff9', 'L')

            # Add constraints for the right leg
            add_constraints('MDL-jnt-R-thighbone', 'MDL-jnt-R-leg-shin', 'MDL-eff23', 'R')



            #####################################################
            # BONE SHAPE IMPORT
            #####################################################


            # Get the path to the assets folder in the plugin directory
            addon_dir = os.path.dirname(__file__)
            asset_path = os.path.join(addon_dir, "assets", "GmBones.blend")
        
            # Check if the file exists
            if not os.path.exists(asset_path):
                self.report({'ERROR'}, f"GmBones file not found: {asset_path}")
                return {'CANCELLED'}
        
            # Create or get the GmBones collection
            gm_bones_collection = bpy.data.collections.get("GmBones")
            if gm_bones_collection is None:
                gm_bones_collection = bpy.data.collections.new("GmBones")
                bpy.context.scene.collection.children.link(gm_bones_collection)

            # Append all objects from the GmBones file
            with bpy.data.libraries.load(asset_path, link=False) as (data_from, data_to):
                data_to.objects = data_from.objects

            # Link imported objects to the GmBones collection
            for obj in data_to.objects:
                if obj is not None:
                    gm_bones_collection.objects.link(obj)
        
            # Hide the GmBones collection in the viewport
            gm_bones_collection.hide_viewport = True
            gm_bones_collection.hide_render = True


        else:
            self.report({'ERROR'}, "Select an armature object")

        return {'FINISHED'}



def register():
    bpy.utils.register_class(OBJECT_OT_GhostMasterIK)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_GhostMasterIK)