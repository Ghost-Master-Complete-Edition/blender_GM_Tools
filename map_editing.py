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
        
        
def register():
  bpy.utils.register_class(OBJECT_OT_SetFloorProperty)  # Register Set Floor Operator
  
def unregister():
  bpy.utils.unregister_class(OBJECT_OT_SetFloorProperty)  # Unregister Set Floor Operator 
   
if __name__ == "__main__":
    register()
  