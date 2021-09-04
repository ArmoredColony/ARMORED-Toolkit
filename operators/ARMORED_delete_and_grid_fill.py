# v1.0


import bpy
import bmesh
from bpy.props import IntProperty, BoolProperty

import math


class ARMORED_OT_delete_and_grid_fill(bpy.types.Operator):
    '''Creates a temporary custom orientation from your selection (reset by running it again while hovering over an empty area of your viewport).

(armoredColony.com)'''
 
    bl_idname  = 'mesh.armored_delete_and_grid_fill'
    bl_label   = 'ARMORED Delete and Grid Fill'
    bl_options = {'REGISTER', 'UNDO'}

    span : IntProperty(name='Span', default=1)
    offset : IntProperty(name='Offset', default=0, options={'SKIP_SAVE'})
    use_interp_simple : BoolProperty(name='Simple Blending', default=False)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        
        col = layout.column(align=True)
        col.prop(self, 'span')
        col.prop(self, 'offset')
        col.prop(self, 'use_interp_simple')

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'
    
    def invoke(self, context, event):
        bm = bmesh.from_edit_mesh(context.edit_object.data)
        edge_border = {e for e in bm.edges if e.select and (e.is_boundary or not all(f.select for f in e.link_faces))}
        self.span = math.floor(len(edge_border) / 4)
        return self.execute(context)

    def execute(self, context):
        bm = bmesh.from_edit_mesh(context.edit_object.data)
        edge_border = {e for e in bm.edges if e.select and (e.is_boundary or not all(f.select for f in e.link_faces))}
        bpy.ops.mesh.delete(type='FACE')

        # bpy.ops.mesh.select_mode(type='EDGE')
        context.tool_settings.mesh_select_mode = (False, True, False)

        for e in edge_border:
            e.select = True
        
        bpy.ops.mesh.fill_grid(span=self.span, offset=self.offset, use_interp_simple=self.use_interp_simple)
        context.tool_settings.mesh_select_mode = (False, False, True)

        return {'FINISHED'}
    

def draw(self, context):
    layout = self.layout
    layout.operator_context = 'INVOKE_DEFAULT';
    layout.operator(ARMORED_OT_delete_and_grid_fill.bl_idname, text='Delete and Grid Fill')


classes = (
    ARMORED_OT_delete_and_grid_fill,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_edit_mesh_delete.append(draw)
    # bpy.types.VIEW3D_MT_curve_add.append(draw)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_edit_mesh_delete.remove(draw)
    # bpy.types.VIEW3D_MT_curve_add.remove(draw)