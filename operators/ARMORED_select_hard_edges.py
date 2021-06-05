# v1.1

import bpy, bmesh
from bpy.props import FloatProperty
from math import degrees, radians

class ARMORED_OT_select_hard_edges(bpy.types.Operator):
    '''Similar to Select Sharp Edges but limited to your selection or will apply to the entire mesh if nothing is selected.

(www.armoredColony.com)'''

    bl_label = 'ARMORED Select Hard Edges'
    bl_idname = 'mesh.armored_select_hard_edges'
    bl_options = {'REGISTER' , 'UNDO'}

    edge_angle : FloatProperty(name='Edge Angle', default=30)

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'
    
    def execute(self, context):
        ob = context.edit_object
        me = ob.data
        bm = bmesh.from_edit_mesh(me)

        sel_mode = context.tool_settings.mesh_select_mode[:] 

        if not sel_mode[1]: 
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')

        edges = set(e for e in bm.edges if e.select)
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.edges_select_sharp(sharpness=radians(self.edge_angle))

        if edges:
            sharp_edges = set(e for e in bm.edges if e.select)
            new_sel = set(sharp_edges).intersection(edges)
            bpy.ops.mesh.select_all(action='DESELECT')

            for e in new_sel:
                e.select = True

        return {'FINISHED'}


def draw_menu(self , context):
    self.layout.separator()
    self.layout.operator('MESH_OT_armored_select_hard_edges', icon='FAKE_USER_OFF')
            

classes = (
    ARMORED_OT_select_hard_edges,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_edit_mesh_select_by_trait.append(draw_menu)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_edit_mesh_select_by_trait.remove(draw_menu)