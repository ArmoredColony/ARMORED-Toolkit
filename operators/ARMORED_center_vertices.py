# v1.2

import bpy
import bmesh
from bpy.props import EnumProperty


class ARMORED_OT_center_vertices(bpy.types.Operator):
    '''Moves your selected components to the world center in the specified Axis.

(www.armoredColony.com)'''
    
    bl_idname = 'mesh.armored_center_vertices'
    bl_label = 'ARMORED Center Vertices'
    bl_options = {'REGISTER', 'UNDO'}

    axis: EnumProperty( 
        name='Axis', 
        description='Move selected components to World Zero X, Y or Z', 
        default='X', 
        items=[ ('X', 'X', 'Move selection to World Zero X'),
                ('Y', 'Y', 'Move selection to World Zero Y'),
                ('Z', 'Z', 'Move selection to World Zero Z'), ]
        )

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        if context.mode != 'EDIT_MESH':
            self.report({'ERROR'}, 'Zero Vertex X\n You need to be in edit mode.')
            return {'CANCELLED'}

        ob = context.edit_object
        me = ob.data
        bm = bmesh.from_edit_mesh(me)

        verts = [v for v in bm.verts if v.select]

        for v in verts:
            if self.axis == 'X':
                v.co[0] = 0
            elif self.axis == 'Y':
                v.co[1] = 0
            else:
                v.co[2] = 0

        bmesh.update_edit_mesh(me)
        return {'FINISHED'}


class ARMORED_MT_center_vertices(bpy.types.Menu):
    bl_label = 'Center Vertices'
    bl_idname = 'ARMORED_MT_center_vertices'

    def draw(self, context):
        layout = self.layout

        # layout.label(text = 'ARMORED Scripts')
        layout.operator(ARMORED_OT_center_vertices.bl_idname, text='ARMORED Center in X').axis = 'X'
        layout.operator(ARMORED_OT_center_vertices.bl_idname, text='ARMORED Center in Y').axis = 'Y'
        layout.operator(ARMORED_OT_center_vertices.bl_idname, text='ARMORED Center in Z').axis = 'Z'


def draw_menu(self, context):
    self.layout.separator()
    self.layout.menu(ARMORED_MT_center_vertices.bl_idname, icon='FAKE_USER_OFF')


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
