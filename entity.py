import bpy
import mathutils

# Transfer Nullboxes Operator
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

# UV DRIVER SECTION

#UV DRIVER Funtions 
def create_UV_driver(obj):
    """Creates an empty object as UV driver and parents it to obj."""
    # Create driver
    driver = bpy.data.objects.new(f"{obj.name}_UV_Driver", None)
    bpy.context.collection.objects.link(driver)

    # Parent to object with no inverse
    driver.parent = obj
    driver.matrix_parent_inverse.identity()

    # Move driver away
    driver.location.z += 2.0

    # Lock unused transforms
    driver.lock_location = (False, False, True)
    driver.lock_rotation = (True, True, False)
    driver.lock_scale = (True, True, True)
    
    # Add custom property
    driver["UV_DRIVER"] = "UV_DRIVER"

    return driver

def create_UV_mapping_node(obj, driver):
    """Creates and links UV Map and Mapping nodes for the object's active material."""
    mat = obj.active_material
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links

    # Find Principled BSDF
    principled = next(node for node in nodes if node.type == 'BSDF_PRINCIPLED')
    tex_node = principled.inputs['Base Color'].links[0].from_node

    # UV Map node
    uv_map_node = nodes.new(type='ShaderNodeUVMap')
    uv_map_node.uv_map = obj.data.uv_layers.active.name

    # Mapping node
    mapping_node = nodes.new(type='ShaderNodeMapping')
    mapping_node.label = "GM_UV_MAPPING"

    # Position nodes
    uv_map_node.location = tex_node.location.x - 400, tex_node.location.y
    mapping_node.location = uv_map_node.location.x + 200, uv_map_node.location.y

    # Connect nodes
    links.new(uv_map_node.outputs['UV'], mapping_node.inputs['Vector'])
    links.new(mapping_node.outputs['Vector'], tex_node.inputs['Vector'])

    return mapping_node

def link_UV_mapping_node(mapping_node, driver):
    """Adds drivers to the Mapping node's Location and Rotation inputs based on the UV driver."""
    # Location drivers for X and Y
    for i, axis in enumerate(['x', 'y']):
        drv = mapping_node.inputs['Location'].driver_add("default_value", i).driver
        drv.type = 'SCRIPTED'
        var = drv.variables.new()
        var.name = 'drv_loc'
        var.targets[0].id = driver
        var.targets[0].data_path = f"location.{axis}"
        drv.expression = f"-{var.name} / 2"

    # Rotation driver for Z
    drv = mapping_node.inputs['Rotation'].driver_add("default_value", 2).driver
    drv.type = 'SCRIPTED'
    var = drv.variables.new()
    var.name = 'drv_rot'
    var.targets[0].id = driver
    var.targets[0].data_path = "rotation_euler.z"
    drv.expression = f"-{var.name}"

# UV DRIVER Operators
class OBJECT_OT_CreateUVDriver(bpy.types.Operator):
    """Create UV driver for the selected object."""
    bl_idname = "object.create_uv_driver"
    bl_label = "Create UV Driver"
    bl_options = {'REGISTER', 'UNDO'}
    def execute(self, context):
        # Check if an object is selected
        if not bpy.context.selected_objects:
            self.report({'WARNING'}, "No object selected")
            return {'CANCELLED'}
        selected_objects = bpy.context.selected_objects
        # Check if the selected object is a mesh
        for obj in selected_objects:
            if obj.type == 'MESH':
                # Check using custom property obj children don't already have Driver'
                for child in obj.children:
                    if child.get("UV_DRIVER") == "UV_DRIVER":
                        self.report({'WARNING'}, f"{child.name} already has a UV driver, try relinking it instead")
                        return {'CANCELLED'}
                # Check if the object has an active material
                if not obj.active_material:
                    self.report({'WARNING'}, f"{obj.name} has no active material")
                    return {'CANCELLED'}
                # Check if the active material has a texture node
                if not any(node.type == 'TEX_IMAGE' for node in obj.active_material.node_tree.nodes):
                    self.report({'WARNING'}, f"{obj.name} has no texture node in the active material")
                    return {'CANCELLED'}

                # If all checks passed create the UV driver and mapping node
                driver = create_UV_driver(obj)
                mapping_node = create_UV_mapping_node(obj, driver)
                link_UV_mapping_node(mapping_node, driver)
            else:
                self.report({'WARNING'}, f"{obj.name} is not a mesh object")
                return {'CANCELLED'}
        return {'FINISHED'}      
        
class OBJECT_OT_RelinkUVDriver(bpy.types.Operator):
    """Relink UV driver for the selected object or driver."""
    bl_idname = "object.relink_uv_driver"
    bl_label = "Relink UV Driver"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        if not bpy.context.selected_objects:
            self.report({'WARNING'}, "No object selected")
            return {'CANCELLED'}
        
        selected_objects = bpy.context.selected_objects
        
        for obj in selected_objects:
            driver = None
            mesh = None
            
            if obj.type == 'MESH' or obj.get("UV_DRIVER") == "UV_DRIVER":
                if obj.type == 'MESH':
                    mesh = obj
                    for child in mesh.children:
                        if child.get("UV_DRIVER") == "UV_DRIVER":
                            driver = child
                            break
                    if not driver:
                        self.report({'ERROR'}, f"No UV driver found among children of {mesh.name}")
                        return {'CANCELLED'}
                else:
                    driver = obj
                    mesh = driver.parent
                    if not mesh or mesh.type != 'MESH':
                        self.report({'ERROR'}, f"UV driver {driver.name} has no valid mesh parent")
                        return {'CANCELLED'}
            else:
                self.report({'WARNING'}, f"{obj.name} is not a mesh object or a UV driver")
                continue

            # Check that mesh doesn't already have the mapping node
            if any(node.label == "GM_UV_MAPPING" for node in mesh.active_material.node_tree.nodes):
                self.report({'ERROR'}, f"{mesh.name} is already linked to its driver")
                return {'CANCELLED'}

            # Proceed with creating mapping node and linking the driver to the mesh
            print(f"Relinking UV driver for mesh: {mesh.name}, driver: {driver.name}")
            mapping_node = create_UV_mapping_node(mesh, driver)
            link_UV_mapping_node(mapping_node, driver)
        
        return {'FINISHED'}

            

            
def register():
    bpy.utils.register_class(OBJECT_OT_TransferNullboxes)
    bpy.utils.register_class(OBJECT_OT_CreateUVDriver)
    bpy.utils.register_class(OBJECT_OT_RelinkUVDriver)
    
def unregister():
    bpy.utils.unregister_class(OBJECT_OT_TransferNullboxes)
    bpy.utils.unregister_class(OBJECT_OT_CreateUVDriver)
    bpy.utils.unregister_class(OBJECT_OT_RelinkUVDriver)
    
if __name__ == "__main__":
    register()