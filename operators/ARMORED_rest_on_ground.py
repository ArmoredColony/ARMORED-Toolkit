
# v1.2

import bpy
from mathutils import Vector
import bmesh


def origin_to_bottom(obj):
    mw = obj.matrix_world
    local_verts = [Vector(v[:]) for v in obj.bound_box]
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    x, y, z = 0, 0, 0

    l = len(local_verts)
    '''
    # will give a modified center
    # eg if array modifier will be centre of array
    y = sum([v.y for v in local_verts]) / l
    x = sum([v.x for v in local_verts]) / l
    '''
    z = min([v.z for v in local_verts])

    local_origin = Vector((x, y, z))
    global_origin = mw @ local_origin

    for v in bm.verts:
        v.co = v.co - local_origin

    bm.to_mesh(obj.data)

    #move the mesh back
    mw.translation = global_origin


class ARMORED_OT_rest_on_ground(bpy.types.Operator):
    '''Set the pivots of the selected MESH objects to their base and rest them on the grid.

(www.armoredColony.com)'''

    bl_idname = 'object.armored_rest_on_ground'
    bl_label = 'ARMORED Rest on Ground'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        mode = context.mode

        if mode == 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='OBJECT')

        selected_objects = [ob for ob in context.selected_objects if ob.type == 'MESH']
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

        for ob in selected_objects:
            origin_to_bottom(ob)
            ob.location[2] = 0

        if mode == 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='EDIT')
            
        return {'FINISHED'}


classes = (
    ARMORED_OT_rest_on_ground,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)