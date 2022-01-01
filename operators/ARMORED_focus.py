# v2.2

import bpy
from bpy_extras import view3d_utils


class MESH_OT_armored_focus(bpy.types.Operator):
    '''Provides additional functionality to the view_selected operator, such as re-centering the object even if you don't have any components selected, or framing all the objects in the scene if no object is selected.

(www.armoredColony.com)'''
    
    bl_idname = 'mesh.armored_focus'
    bl_label = 'ARMORED Focus'
    bl_options = {'REGISTER'}
    
    def object_focus(self, context):
        if context.selected_objects:
            bpy.ops.view3d.view_selected('INVOKE_DEFAULT')
            return

        bpy.ops.view3d.view_all('INVOKE_DEFAULT')

    def edit_mesh_focus(self, context):
        obj = context.edit_object
        selection = obj.data.total_vert_sel
        
        if not selection: 
            bpy.ops.mesh.select_all(action='SELECT')

        bpy.ops.view3d.view_selected('INVOKE_DEFAULT')

        if not selection: 
            bpy.ops.mesh.select_all(action='DESELECT')

    def sculpting_focus(self, context, event):
        if self.raycast_hit(context, event):
            bpy.ops.view3d.view_center_pick('INVOKE_DEFAULT')
            return

        # bpy.ops.object.mode_set(mode='OBJECT', toggle=True)
        # bpy.ops.view3d.view_selected('INVOKE_DEFAULT')
        # bpy.ops.object.mode_set(mode='SCULPT', toggle=True)
        bpy.ops.view3d.view_all('INVOKE_DEFAULT', center=False) # False is already the default.
    
    def raycast_hit(self, context, event):
        scene = context.scene
        region = context.region
        rv3d = context.region_data
        coord = event.mouse_region_x, event.mouse_region_y

        depsgraph = context.evaluated_depsgraph_get()
        # view_layer = context.view_layer # for older blenders

        # get the ray from the viewport and mouse
        direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
        origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

        result, location, normal, index, obj, matrix = scene.ray_cast(depsgraph, origin, direction)

        return result

    def invoke(self, context, event):
        if context.mode == 'OBJECT':
            self.object_focus(context)
            return {'FINISHED'}
        
        if context.mode == 'EDIT_MESH':
            self.edit_mesh_focus(context)
            return {'FINISHED'}
        
        if context.mode == 'SCULPT':
            self.sculpting_focus(context, event)
            return {'FINISHED'}
        
        return {'FINISHED'}

    
classes = (
    MESH_OT_armored_focus,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)