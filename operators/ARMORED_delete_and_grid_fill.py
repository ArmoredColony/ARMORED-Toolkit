# v1.0


import bpy
import bmesh
from bpy.props import IntProperty, BoolProperty

import math


class ARMORED_OT_delete_faces_and_select_border(bpy.types.Operator):
    '''Creates a temporary custom orientation from your selection (reset by running it again while hovering over an empty area of your viewport).

(armoredColony.com)'''
 
    bl_idname  = 'mesh.armored_delete_faces_and_select_border'
    bl_label   = 'ARMORED Delete faces and select Border'

    def execute(self, context):
        bm = bmesh.from_edit_mesh(context.edit_object.data)
        edge_border = {e for e in bm.edges if e.select and (e.is_boundary or not all(f.select for f in e.link_faces))}
        bpy.ops.mesh.delete(type='FACE')
        context.tool_settings.mesh_select_mode = (False, True, False)

        for e in edge_border:
            e.select = True
        
        return {'FINISHED'}


class ARMORED_OT_switch_to_face_mode(bpy.types.Operator):
    bl_idname  = 'mesh.armored_switch_to_face_mode'
    bl_label   = 'ARMORED Switch to Face Mode'
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        context.tool_settings.mesh_select_mode = (False, False, True)
        return {'FINISHED'}


class ARMORED_OT_delete_and_grid_fill(bpy.types.Macro):
    bl_idname = 'mesh.armored_delete_and_grid_fill'
    bl_label = 'ARMORED Delete and Grid Fill'
    bl_options = {'REGISTER', 'UNDO'}
    

def draw(self, context):
    self.layout.operator(ARMORED_OT_delete_and_grid_fill.bl_idname, text='Delete and Grid Fill', icon='FAKE_USER_OFF')


classes = (
    ARMORED_OT_delete_faces_and_select_border,
    ARMORED_OT_switch_to_face_mode,
    ARMORED_OT_delete_and_grid_fill,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    ARMORED_OT_delete_and_grid_fill.define('MESH_OT_armored_delete_faces_and_select_border')
    ARMORED_OT_delete_and_grid_fill.define('MESH_OT_fill_grid')
    ARMORED_OT_delete_and_grid_fill.define('MESH_OT_armored_switch_to_face_mode')
    bpy.types.VIEW3D_MT_edit_mesh_delete.append(draw)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_edit_mesh_delete.remove(draw)