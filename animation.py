import bpy
from mathutils import Vector
import os

# GHOST MASTER AUTORIG KINDA

# Made by Pat on 02/10/2024


class OBJECT_OT_GhostMasterIK(bpy.types.Operator):
    """Creates rig setup for selected Ghost Master armature"""
    bl_idname = "object.ghost_master_ik"
    bl_label = "Create Ghost Master rig setup"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = bpy.context.object

        # Ensure that the active object is an armature
        if obj and obj.type == 'ARMATURE':

            # Store the armature reference
            armature = obj

            #####################################################
            # IK SETUP (for both legs but no arms for now sorry)
            #####################################################

            # Switch to Edit Mode to modify bones
            bpy.ops.object.mode_set(mode='EDIT')

            # Function to set up IK for a given limb (left or right)
            def setup_ik(limb, proximal_name, distal_name, side_prefix):
                # Check if IK bones already exist
                if limb == 'Leg':
                    ik_bone_name = f'{side_prefix}-Foot-Ik'
                    pole_bone_name = f'{side_prefix}-Knee-Pole'
                elif limb == 'Arm':
                    ik_bone_name = f'{side_prefix}-Hand-Ik'
                    pole_bone_name = f'{side_prefix}-Elbow-Pole'

                if obj.data.edit_bones.get(ik_bone_name) or obj.data.edit_bones.get(pole_bone_name):
                    self.report({'WARNING'}, f"IK bones for {side_prefix} {limb} already exist.")
                    return  # Skip the setup if bones are found



                # Create proxy bones for the proximal and distal bones
                # Duplicate bones to create proxies
                proxy_proximal = obj.data.edit_bones.new(f'{proximal_name}_proxy')
                proxy_distal = obj.data.edit_bones.new(f'{distal_name}_proxy')

                original_proximal = obj.data.edit_bones.get(proximal_name)
                original_distal = obj.data.edit_bones.get(distal_name)


                # Copy transforms from original to proxy
                for proxy, original in [(proxy_proximal, original_proximal), (proxy_distal, original_distal)]:
                    proxy.head = original.head.copy()
                    proxy.tail = original.tail.copy()
                    proxy.roll = original.roll
                    proxy.use_deform = False
                    parent_bone = obj.data.edit_bones.get('MDL-GOD')
                    if parent_bone:
                        proxy.parent = parent_bone
                        proxy.use_connect = False

                # Move the tail of the specified proxy bones to the head of their original bones child
                for bone_name in [proximal_name, distal_name]:
                    bone = obj.data.edit_bones.get(bone_name)
                    proxy_bone = obj.data.edit_bones.get(f'{bone_name}_proxy')
                    if bone:
                        children = bone.children
                        if children:
                            child_bone = children[0]
                            proxy_bone.tail = child_bone.head
                            print(f"Moved tail of {bone.name} to head of {child_bone.name}.")

                # Parent proxy distal to proxy proximal
                if proxy_proximal and proxy_distal:
                    proxy_distal.parent = proxy_proximal
                    proxy_distal.use_connect = True

                # Automatically find the parent of the proximal bone, parent the proximal proxy to it
                if original_proximal and original_proximal.parent:
                    parent_bone = obj.data.edit_bones.get(original_proximal.parent.name)
                    if parent_bone:
                        proxy_proximal.parent = parent_bone
                        proxy_proximal.use_connect = False

                # Automatically find the first child of the distal bone to use as the effector
                if original_distal and original_distal.children:
                    eff_bone = original_distal.children[0]  # First child of shinbone

                    # Create the IK bone
                    if limb == 'Leg':
                        ik_bone = obj.data.edit_bones.new(f'{side_prefix}-Foot-Ik')

                    elif limb == 'Arm':
                        ik_bone = obj.data.edit_bones.new(f'{side_prefix}-Hand-Ik')
                   
                    ik_bone.head = eff_bone.head
                    ik_bone.tail = eff_bone.tail
                    ik_bone.roll = eff_bone.roll
                    ik_bone.use_deform = False
                    parent_bone = obj.data.edit_bones.get('MDL-GOD')

                    if parent_bone:
                        ik_bone.parent = parent_bone
                        ik_bone.use_connect = False

                # Create the pole vector
                if proxy_proximal and proxy_distal:
                    pole_pos = (proxy_proximal.head + proxy_distal.tail) / 2
                    pole_offset = Vector((0.0, -0.5, 0.0))
                    pole_position = pole_pos + pole_offset

                    if limb == 'Leg':
                        pole_bone = obj.data.edit_bones.new(f'{side_prefix}-Knee-Pole')
                        pole_bone.head = pole_position
                        pole_bone.tail = pole_position + Vector((0.0, 0.2, 0.0))
                    
                    elif limb == 'Arm':
                        pole_bone = obj.data.edit_bones.new(f'{side_prefix}-Elbow-Pole')
                        pole_bone.head = pole_position
                        pole_bone.tail = pole_position + Vector((0.0, -0.2, 0.0))
                    
                    pole_bone.use_deform = False
                    if parent_bone:
                        pole_bone.parent = parent_bone

            # # Setup IK for the left leg

            setup_ik('Leg', 'MDL-jnt-L-thighbone', 'MDL-jnt-L-LEG-shin', 'L')

            # # Setup IK for the right leg
            setup_ik('Leg', 'MDL-jnt-R-thighbone', 'MDL-jnt-R-leg-shin', 'R')

            # # Setup IK for the left arm
            # setup_ik('Arm', 'MDL-jnt-L-bicepBONE', 'MDL-jnt-L-FOREARM', 'L')

            # # Setup IK for the right arm
            # setup_ik('Arm', 'MDL-jnt-R-bicepBONE', 'MDL-jnt49_2-RFarm', 'R')


            # Switch back to Object Mode
            bpy.ops.object.mode_set(mode='OBJECT')

            # Add IK constraints
            def add_constraints(limb, proximal_name, distal_name, terminal_eff_name, side_prefix):
                # Constraint proxy bones to the original bones
                proxy_proximal = obj.pose.bones.get(f'{proximal_name}_proxy')
                proxy_distal = obj.pose.bones.get(f'{distal_name}_proxy')

                original_proximal = obj.pose.bones.get(proximal_name)
                original_distal = obj.pose.bones.get(distal_name)

                # Proximal bone constraints
                if original_proximal and proxy_proximal:
                    if not any(c.type == 'CHILD_OF' and c.subtarget == proxy_proximal.name for c in original_proximal.constraints):
                        childof_constraint = original_proximal.constraints.new('CHILD_OF')
                        childof_constraint.name = "ChildOf_Proxy"
                        childof_constraint.target = obj
                        childof_constraint.subtarget = proxy_proximal.name
                        childof_constraint.use_location_x = False
                        childof_constraint.use_location_y = False
                        childof_constraint.use_location_z = False
                        childof_constraint.mute = True

                # Distal bone constraints
                if original_distal and proxy_distal:
                    if not any(c.type == 'COPY_ROTATION' and c.subtarget == proxy_distal.name for c in original_distal.constraints):
                        copyrot_constraint = original_distal.constraints.new('COPY_ROTATION')
                        copyrot_constraint.name = "CopyRot_Proxy"
                        copyrot_constraint.target = obj
                        copyrot_constraint.subtarget = proxy_distal.name
                        copyrot_constraint.target_space = 'LOCAL_OWNER_ORIENT'
                        copyrot_constraint.owner_space = 'LOCAL'
                        childof_constraint.mute = True

                # Normal IK contraints
                if proxy_distal:
                    if not any(constraint.type == 'IK' for constraint in proxy_distal.constraints):
                        # Add IK constraint to the shin bone
                        ik_constraint = proxy_distal.constraints.new('IK')
                        ik_constraint.target = obj
                        ik_constraint.pole_target = obj
                        ik_constraint.chain_count = 2
                        
                        if limb == 'Leg':
                            ik_constraint.subtarget = f'{side_prefix}-Foot-Ik'
                            ik_constraint.pole_subtarget = f'{side_prefix}-Knee-Pole'
                            ik_constraint.pole_angle = 0  # Adjust this if needed
                        elif limb == 'Arm':
                            ik_constraint.subtarget = f'{side_prefix}-Hand-Ik'
                            ik_constraint.pole_subtarget = f'{side_prefix}-Elbow-Pole'
                            ik_constraint.pole_angle = 180  # Adjust this if needed
                        
                        # Mute the IK constraint by default
                        ik_constraint.mute = True
                    else:
                        self.report({'WARNING'}, f"IK constraint already exists on {proxy_distal.name}.")
                else:
                    self.report({'WARNING'}, f"{limb} bone {distal_name} not found.")

                # Add Copy Rotation constraint to the terminal effector bone (Foot or Hand)
                pbon_terminal = obj.pose.bones.get(terminal_eff_name)
                if pbon_terminal:
                    # Check if Copy Rotation constraint already exists
                    if not any(constraint.type == 'COPY_ROTATION' for constraint in pbon_terminal.constraints):
                        # Add Copy Rotation constraint to the foot effector bone
                        copy_rot_constraint = pbon_terminal.constraints.new('COPY_ROTATION')
                        copy_rot_constraint.target = obj
                        if limb == 'Leg':
                            copy_rot_constraint.subtarget = f'{side_prefix}-Foot-Ik'
                        elif limb == 'Arm':
                            copy_rot_constraint.subtarget = f'{side_prefix}-Hand-Ik'

                        # Mute the Copy Rotation constraint by default
                        copy_rot_constraint.mute = True
                    else:
                        self.report({'WARNING'}, f"Copy Rotation constraint already exists on {pbon_terminal.name}.")
                else:
                    self.report({'WARNING'}, f"Foot effector bone {terminal_eff_name} not found.")

            # Add constraints for the left leg
            add_constraints('Leg', 'MDL-jnt-L-thighbone', 'MDL-jnt-L-LEG-shin', 'MDL-eff9', 'L')

            # Add constraints for the right leg
            add_constraints('Leg', 'MDL-jnt-R-thighbone', 'MDL-jnt-R-leg-shin', 'MDL-eff23', 'R')

            # Add constraints for the left arm
            # add_constraints('Arm', 'MDL-jnt-L-bicepBONE', 'MDL-jnt-L-FOREARM', 'MDL-eff45', 'L')

            # # Add constraints for the right arm
            # add_constraints('Arm', 'MDL-jnt-R-bicepBONE', 'MDL-jnt49_2-RFarm', 'MDL-eff50', 'R')

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

            # Check if the GmBones collection is already imported
            gm_bones_collection = bpy.data.collections.get("GmBones")
            if gm_bones_collection is None or len(gm_bones_collection.objects) == 0:   
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
                self.report({'WARNING'}, "GmBones collection already imported.")

            #####################################################
            # BONE SHAPE AND BONE COLLECTIONS SETUP
            #####################################################

            # Define the bones assigned to collections as lists
            bones_FK=["MDL-lfoot", "MDL-rfoot", "MDL-jnt-L-LEG-shin", "MDL-jnt-R-leg-shin", "MDL-jnt-L-thighbone", "MDL-jnt-R-thighbone"]
            bones_IK=["L-Foot-Ik", "R-Foot-Ik", "L-Knee-Pole", "R-Knee-Pole"]

            # Check if bone collections are already created, if not, create them
            
            bcoll_Gm_Rig = armature.data.collections_all.get("GM Rig")
            if bcoll_Gm_Rig is None:
                bcoll_Gm_Rig = armature.data.collections.new("GM Rig")
            else:
                self.report({'WARNING'}, "GM Rig collection already exists.")

            bcoll_Main = armature.data.collections_all.get("Main")
            if bcoll_Main is None:
                bcoll_Main = armature.data.collections.new("Main", parent=bcoll_Gm_Rig)
            else:
                self.report({'WARNING'}, "Main collection already exists.")

            bcoll_FK = armature.data.collections_all.get("FK")
            if bcoll_FK is None:
                bcoll_FK = armature.data.collections.new("FK", parent=bcoll_Gm_Rig)
            else:
                self.report({'WARNING'}, "FK collection already exists.")

            bcoll_IK = armature.data.collections_all.get("IK")
            if bcoll_IK is None:
                bcoll_IK = armature.data.collections.new("IK", parent=bcoll_Gm_Rig)
            else:
                self.report({'WARNING'}, "IK collection already exists.")

            bcoll_Extra = armature.data.collections_all.get("Extra")
            if bcoll_Extra is None:
                bcoll_Extra = armature.data.collections.new("Extra", parent=bcoll_Gm_Rig)
            else:
                self.report({'WARNING'}, "Extra collection already exists.")

            # Start by assigning every bone in armature to the Extra collection
            for bone in armature.data.bones:
                bcoll_Extra.assign(armature.pose.bones.get(bone.name))

            # Assign custom shapes to bones based on object names
            for obj in bpy.data.objects:
                # Check if the object name starts with "GmBons-"
                if obj.name.startswith("GmBons-"):
                    # Extract the bone name from the object name
                    bone_name = obj.name[7:]  # Remove "GmBons-" from the name
                    
                    # Check if the armature has a bone with the extracted name
                    if bone_name in armature.data.bones:
                        bone = armature.pose.bones.get(bone_name)
                        
                        # Assign the object as the custom shape for the bone
                        bone.custom_shape = obj
                        print(f"Assigned {obj.name} to {bone_name}")
                        
                        # Assign bone as Main collection
                        bcoll_Main.assign(bone)

                        # Remove bone from Extra collection
                        bcoll_Extra.unassign(bone)
                        
                        # Assign bone as FK collection if it's in the FK list
                        for a in range (len(bones_FK)):
                            if bone_name == bones_FK[a]:
                                bcoll_Main.unassign(bone)
                                bcoll_FK.assign(bone)

                        # Assign bone as IK collection if it's in the IK list
                        for a in range (len(bones_IK)):
                            if bone_name == bones_IK[a]:
                                bcoll_Main.unassign(bone)
                                bcoll_IK.assign(bone)

                                          
                    else:
                        print(f"No bone named {bone_name} found in the armature.")

            # Hide IK and Extra collections
            bcoll_IK.is_visible = False
            bcoll_Extra.is_visible = False

        else:
            self.report({'ERROR'}, "Select an armature object")

        return {'FINISHED'}




class OBJECT_OT_SwitchLegsFKIK(bpy.types.Operator):
    """Switch between FK and IK for the legs"""
    bl_idname = "object.switch_legs_fk_ik"
    bl_label = "Switch Legs FK/IK"
   
    
    def execute(self, context):
        
        obj = bpy.context.object

		# Check if FK is not hidden
        if obj.data.collections_all["FK"].is_visible == True:
                
            ##############
            # Switch to IK
            ##############
       
            # Hide FK
            obj.data.collections_all["FK"].is_visible = False

            # Unhide IK
            obj.data.collections_all["IK"].is_visible = True
                    
            # Unmute all constraints
            for pbone in obj.pose.bones:
                for constraint in pbone.constraints:
                    constraint.mute = False
        
                    
        else:
            ##############
			# Switch to FK
			##############
					
            # Hide IK
            obj.data.collections_all["IK"].is_visible = False

            # Unhide FK
            obj.data.collections_all["FK"].is_visible = True
					
            # Mute IK constraints
            for pbone in obj.pose.bones:
                for constraint in pbone.constraints:
                    if constraint.type == 'IK' or constraint.type == 'COPY_ROTATION' or constraint.type == 'CHILD_OF':
                        constraint.mute = True

     

        return {'FINISHED'}



class OBJECT_OT_DeleteRigSetup(bpy.types.Operator):
    """Deletes IK bones, constraints and the GmBones collection"""
    bl_idname = "object.delete_rig_setup"
    bl_label = "Delete Rig Setup"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = bpy.context.object

		# Ensure that the active object is an armature
        if obj and obj.type == 'ARMATURE':

            # Store the armature reference
            armature = obj

            # Switch to Edit Mode to modify bones
            bpy.ops.object.mode_set(mode='EDIT')

            # Delete the constraints from the shin and thighbones
            for bone_name in ["MDL-jnt-L-LEG-shin", "MDL-jnt-R-leg-shin", "MDL-jnt-L-thighbone", "MDL-jnt-R-thighbone"]:
                bone = obj.data.edit_bones.get(bone_name)
                if bone:
                    pbone = obj.pose.bones.get(bone_name)
                    if pbone:
                        for constraint in pbone.constraints:
                            pbone.constraints.remove(constraint)


            # Delete the copy rotation constraint from the first child of shin bones
            for bone_name in ["MDL-jnt-L-LEG-shin", "MDL-jnt-R-leg-shin"]:
                bone = obj.data.edit_bones.get(bone_name)
                if bone:
                    pbone = obj.pose.bones.get(bone_name)
                    if pbone:
                        # Check if the shin bone has children
                        if bone.children:
                            eff_bone = pbone.id_data.pose.bones.get(bone.children[0].name)  # Get the pose bone of the first child
                            if eff_bone:
                                # Iterate through the constraints of the first child and remove any Copy Rotation constraint
                                for constraint in eff_bone.constraints:
                                    if constraint.type == 'COPY_ROTATION':
                                        eff_bone.constraints.remove(constraint)
            
                                
            # Delete the IK bones and pole targets
            for bone_name in ["L-Foot-Ik", "R-Foot-Ik", "L-Knee-Pole", "R-Knee-Pole"]:
                bone = obj.data.edit_bones.get(bone_name)
                if bone:
                    obj.data.edit_bones.remove(bone)

            # Delete proxy bones
            for bone_name in ["MDL-jnt-L-LEG-shin_proxy", "MDL-jnt-R-leg-shin_proxy", "MDL-jnt-L-thighbone_proxy", "MDL-jnt-R-thighbone_proxy"]:
                bone = obj.data.edit_bones.get(bone_name)
                if bone:
                    obj.data.edit_bones.remove(bone)

            # Switch back to Object Mode
            bpy.ops.object.mode_set(mode='OBJECT')

            # Remove the everything in the GmBones collection and then the collection itself
            gm_bones_collection = bpy.data.collections.get("GmBones")
            if gm_bones_collection:
                for obj in gm_bones_collection.objects:
                    bpy.data.objects.remove(obj)
                bpy.data.collections.remove(gm_bones_collection)

        return {'FINISHED'}


           
def sanity_check():
    issues = []

    # Check for meshes with more than one material
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and len(obj.data.materials) > 1:
            issues.append(f"The mesh '{obj.name}' has more than one material.")

    # Check for one root bone at default values and no animation
    root_bone = None
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            for bone in obj.data.bones:
                if bone.parent is None:  # Root bone
                    if root_bone:
                        issues.append(f"More than one root bone found in '{obj.name}'.")
                    else:
                        root_bone = bone
                        bone_pose = obj.pose.bones[bone.name]
                        if not (round(bone_pose.location.x, 3) == 0 and
                                round(bone_pose.location.y, 3) == 0 and
                                round(bone_pose.location.z, 3) == 0):
                            issues.append(f"The root bone '{bone.name}' does not have the default location (0, 0, 0).")
                        if not (round(bone_pose.rotation_euler.x, 3) == 0 and
                                round(bone_pose.rotation_euler.y, 3) == 0 and
                                round(bone_pose.rotation_euler.z, 3) == 0):
                            issues.append(f"The root bone '{bone.name}' does not have the default rotation (0, 0, 0).")

                        if bone.name in [action.name for action in bpy.data.actions]:
                            issues.append(f"The root bone '{bone.name}' has animation data.")

    if not root_bone:
        issues.append("No root bone found.")

    # Check that all bones are under the root bone's hierarchy
    if root_bone:
        for obj in bpy.data.objects:
            if obj.type == 'ARMATURE':
                for bone in obj.data.bones:
                    if bone.parent is None and bone != root_bone:
                        issues.append(f"The bone '{bone.name}' is not under the root bone '{root_bone.name}'.")

    # Check that the scale of all bones is 1,1,1
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            for bone in obj.pose.bones:
                if not all(round(s, 3) == 1.0 for s in bone.scale):
                    issues.append(f"The bone '{bone.name}' does not have a scale of 1,1,1.")

    # Check for actions with only one keyframe
    for action in bpy.data.actions:
        if len(action.fcurves) == 1 and all(len(fc.keyframe_points) == 1 for fc in action.fcurves):
            issues.append(f"The action '{action.name}' has only one keyframe.")

    return issues

# Button for the Sanity Check in the UI
class OBJECT_OT_SanityCheck(bpy.types.Operator):
    bl_idname = "object.sanity_check"
    bl_label = "Sanity Check"
    bl_description = "Check for rig and animation issues"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        issues = sanity_check()
        if issues:
            for issue in issues:
                self.report({'WARNING'}, issue)
        else:
            self.report({'INFO'}, "All checks passed!")
        return {'FINISHED'}


def register():
    bpy.utils.register_class(OBJECT_OT_GhostMasterIK)
    bpy.utils.register_class(OBJECT_OT_SwitchLegsFKIK)
    bpy.utils.register_class(OBJECT_OT_DeleteRigSetup)
    bpy.utils.register_class(OBJECT_OT_SanityCheck)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_GhostMasterIK)
    bpy.utils.unregister_class(OBJECT_OT_SwitchLegsFKIK)
    bpy.utils.unregister_class(OBJECT_OT_DeleteRigSetup)
    bpy.utils.unregister_class(OBJECT_OT_SanityCheck)