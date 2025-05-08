import bpy

class OBJECT_OT_TransferNullboxes(bpy.types.Operator):
    """Transfer nullboxes from non-active empties to the active empty with ID assignment"""
    bl_idname = "object.transfer_nullboxes"
    bl_label = "Transfer Nullboxes"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        # Get the active object (assumed to be an empty)
        active_empty = bpy.context.active_object
        selected_objects = bpy.context.selected_objects
        existing_ids = []

        # Filter for non-active selected empties
        non_active_empties = [obj for obj in selected_objects if obj != active_empty and obj.type == 'EMPTY']

        # Set active object mode to OBJECT to ensure we can manipulate parenting
        bpy.ops.object.mode_set(mode='OBJECT')

        for empty in non_active_empties:
            for child in empty.children:
                if "nullboxes" in child.keys():
                    # Duplicate the child
                    bpy.ops.object.select_all(action='DESELECT')
                    child.select_set(True)
                    bpy.context.view_layer.objects.active = child
                    bpy.ops.object.duplicate()
                    dup = bpy.context.active_object

                    # Clear parent but keep transform
                    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
            
                    # Collect existing nullbox_ids from active_empty's children
                    for child in active_empty.children:
                        if "nullbox_ids" in child.keys():
                            try:
                                existing_ids.append(int(child["nullbox_ids"]))
                            except ValueError:
                                pass  # skip if not an int

                    # Determine the next available ID
                    next_id = max(existing_ids, default=-1) + 1
                    dup["nullbox_ids"] = str(next_id)  # assign new ID to the duplicate

                    # Check if the duplicated empty's name starts with "MDL-AP" and has a number
                    if dup.name.startswith("MDL-AP"):
                        # Extract the number part from the duplicated empty's name
                        number_part = dup["nullbox_ids"]

                        # Check if the parent of the duplicated empty starts with "MDL-"
                        if active_empty.name.startswith("MDL-"):
                            # Remove the "MDL-" prefix from the parent name
                            new_parent_name = active_empty.name[4:]
                        else:
                            # Use the parent empty name as is
                            new_parent_name = active_empty.name

                        # Construct the new name for the duplicated empty
                        new_name = f"MDL-AP{number_part}_{new_parent_name}"

                        # Rename the duplicated empty
                        dup.name = new_name
            
                    # Parent to active empty with Keep Transform (Without Inverse)
                    bpy.context.view_layer.objects.active = active_empty
                    dup.select_set(True)
                    bpy.ops.object.parent_no_inverse_set(keep_transform=True)

        print("Done duplicating, reparenting, and renaming.")



        return {'FINISHED'}
        
def register():
    bpy.utils.register_class(OBJECT_OT_TransferNullboxes)
    
def unregister():
    bpy.utils.unregister_class(OBJECT_OT_TransferNullboxes)
    
if __name__ == "__main__":
    register()