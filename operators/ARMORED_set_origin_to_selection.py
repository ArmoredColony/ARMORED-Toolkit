# v1.2

import bpy, bmesh
from mathutils import Vector


class ARMORED_OT_origin_to_selection(bpy.types.Operator):
    '''Move the object's origin to the selected components or center its origin if nothing is selected.

(www.armoredColony.com)'''

    bl_idname = 'mesh.armored_origin_to_selection'
    bl_label = 'ARMORED Origin to Selection'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        obj = context.edit_object
        bm = bmesh.from_edit_mesh(obj.data)
        sel_components = next((v for v in bm.verts if v.select), None)

        original_location = Vector(context.scene.cursor.location)  
        bpy.ops.view3d.snap_cursor_to_selected()

        bpy.ops.object.mode_set(mode = 'OBJECT') 
        if sel_components is None: 
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
        else: 
            bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
        bpy.ops.object.mode_set(mode = 'EDIT') 

        context.scene.cursor.location = original_location 
        return {'FINISHED'}


def draw_menu(self, context):
    self.layout.separator()
    self.layout.operator(ARMORED_OT_origin_to_selection.bl_idname, text='Origin to Selection')


classes = (
    ARMORED_OT_origin_to_selection,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.append(draw_menu)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_edit_mesh_context_menu.remove(draw_menu)