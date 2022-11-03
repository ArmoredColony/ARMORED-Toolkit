# v1.3

import bpy
import bmesh
from bpy.props import EnumProperty


class ARMORED_OT_center_vertices(bpy.types.Operator):
    '''Flattens the selected vertices to the World's Center in a specific Axis.

www.armoredColony.com '''
    
    bl_idname = 'mesh.armored_center_vertices'
    bl_label = 'ARMORED Center Vertices'
    bl_options = {'REGISTER', 'UNDO'}

    axis: EnumProperty( 
        name='Axis', 
        description='Flatten to World Center X, Y or Z', 
        default='X', 
        items=[ ('X', 'X', 'Flatten to World Center X'),
                ('Y', 'Y', 'Flatten to World Center Y'),
                ('Z', 'Z', 'Flatten to World Center Z'), ]
        )

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        for ob in context.objects_in_mode:
            me = ob.data
            bm = bmesh.from_edit_mesh(me)

            matrix_world = ob.matrix_world

            verts = [v for v in bm.verts if v.select]

            for v in verts:
                new_co = matrix_world @ v.co

                if self.axis == 'X':
                    new_co.x = 0
                elif self.axis == 'Y':
                    new_co.y = 0
                else:
                    new_co.z = 0

                v.co = matrix_world.inverted() @ new_co

            bmesh.update_edit_mesh(me)

        return {'FINISHED'}


class ARMORED_MT_center_vertices(bpy.types.Menu):
    bl_label = 'Flatten to World Center'
    bl_idname = 'ARMORED_MT_center_vertices'

    def draw(self, context):
        layout = self.layout

        layout.operator(ARMORED_OT_center_vertices.bl_idname, text='To World Center X').axis = 'X'
        layout.operator(ARMORED_OT_center_vertices.bl_idname, text='To World Center Y').axis = 'Y'
        layout.operator(ARMORED_OT_center_vertices.bl_idname, text='To World Center Z').axis = 'Z'


def draw_menu(self, context):
    self.layout.separator()
    self.layout.menu(ARMORED_MT_center_vertices.bl_idname)


classes = (
    ARMORED_OT_center_vertices,
    ARMORED_MT_center_vertices,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_transform.append(draw_menu)
    
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_transform.remove(draw_menu)
