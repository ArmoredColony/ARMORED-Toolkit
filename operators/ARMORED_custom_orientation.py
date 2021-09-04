# v1.0


import bpy
from bpy_extras import view3d_utils


def raycast(context, event):
    # OLDER VERSIONS OF BLENDER USE VIEW_LAYER INSTEAD OF DEPSGRAPH?

    scene = context.scene
    region = context.region
    rv3d = context.region_data
    coord = event.mouse_region_x, event.mouse_region_y

    depsgraph = context.evaluated_depsgraph_get()
    # view_layer = context.view_layer 

    direction = view3d_utils.region_2d_to_vector_3d(region, rv3d, coord)
    origin = view3d_utils.region_2d_to_origin_3d(region, rv3d, coord)

    result, location, normal, index, obj, matrix = scene.ray_cast(depsgraph, origin, direction)

    return obj


def delete_custom_orientation(self):
    try:
        bpy.ops.transform.select_orientation(orientation=self.orientation_name)
        bpy.ops.transform.delete_orientation()
    #     print('deleted custom orientation')
    except TypeError:
        pass
        # print('orientation does not exist')

def set_custom_orientation(self):
    try:
        bpy.ops.transform.create_orientation(name=self.orientation_name, use_view=False, use=True, overwrite=True)
    except RuntimeError:
        self.report({'WARNING'}, 'ARMORED Toolkit: Runtime Error when creating custom orientation')

    return {'FINISHED'}
    

class ARMORED_OT_custom_orientation(bpy.types.Operator):
    '''Creates a temporary custom orientation from your selection (reset by running it again while hovering over an empty area of your viewport).

(armoredColony.com)'''
 
    bl_idname  = 'mesh.armored_custom_orientation'
    bl_label   = 'ARMORED Set Custom Orientation'
    bl_options = {'REGISTER',}
    
    orientation_name: bpy.props.StringProperty(name='Orientation Name', default='AC Custom')
    

    def invoke(self, context, event):
        if context.mode != 'EDIT_MESH':
            self.report({'WARNING'}, 'ARMORED Toolkit: Custom Orientation script only works on meshes')
            return {'CANCELLED'}

        obj = raycast(context, event)

        if obj != context.active_object:
            delete_custom_orientation(self)
            return {'FINISHED'}

        set_custom_orientation(self)
        return {'FINISHED'}
        

classes = (
    ARMORED_OT_custom_orientation,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)