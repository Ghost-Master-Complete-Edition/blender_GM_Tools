import bpy
import bmesh

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

def update_collider_visibility(self, context):
    """Update visibility of objects with the 'IS_COLLIDER' custom property set to 'TRUE'."""
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj.get("IS_COLLIDER") == "TRUE":
            obj.hide_set(not context.scene.show_collider_objects)
            
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


def split_every_face_keep_normals(self, context):
    if bpy.context.mode != 'OBJECT':
        self.report({'ERROR'}, "Please switch to Object Mode first.")
        return {'CANCELLED'}
    # Store all selected mesh objects
    selected_meshes = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
    
    if not selected_meshes:
        raise Exception("Please select at least one mesh object.")

    for obj in selected_meshes:
        # Duplicate mesh
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.duplicate()
        temp = bpy.context.active_object
        temp.name = f"{obj.name}__temp"

        # Reselect original
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj

        # Enter edit mode with bmesh
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(obj.data)
        bpy.ops.mesh.select_all(action='DESELECT')

        # Split each face into a separate mesh (optional, depends on your goal)
        for face in bm.faces:
            bpy.ops.mesh.select_all(action='DESELECT')
            face.select = True
            bmesh.update_edit_mesh(obj.data)
            bpy.ops.mesh.split()

        # Exit edit mode
        bpy.ops.object.mode_set(mode='OBJECT')

        # Add Data Transfer modifier
        mod = obj.modifiers.new(name="DataTransfer", type='DATA_TRANSFER')
        mod.object = temp
        mod.use_loop_data = True
        mod.data_types_loops = {'CUSTOM_NORMAL'}
        mod.loop_mapping = 'NEAREST_NORMAL'
    
        # Apply modifier
        bpy.ops.object.modifier_apply(modifier=mod.name)

        # Delete temp mesh
        bpy.data.objects.remove(temp, do_unlink=True)

        print("Split faces for objects:", [obj.name for obj in selected_meshes])

class OBJECT_OT_SplitFacesKeepNormals(bpy.types.Operator):
    """Splits every faces of selected object into seperate faces, while keeping Normals the same."""
    bl_idname = "object.split_faces_keep_normals"
    bl_label = "Split Faces (Keep Normals)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        split_every_face_keep_normals(self, context)
        return {'FINISHED'}
        
def register():
  bpy.utils.register_class(OBJECT_OT_SplitFacesKeepNormals)  # Register Split Faces Operator
  bpy.utils.register_class(OBJECT_OT_SetFloorProperty)  # Register Set Floor Operator
  
def unregister():
  bpy.utils.unregister_class(OBJECT_OT_SplitFacesKeepNormals)  # Unregister Split Faces Operator
  bpy.utils.unregister_class(OBJECT_OT_SetFloorProperty)  # Unregister Set Floor Operator/
   
if __name__ == "__main__":
    register()
  