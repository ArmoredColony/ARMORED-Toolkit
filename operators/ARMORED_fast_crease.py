# v1.1

import bpy, bmesh
from bpy.props import EnumProperty, BoolProperty


class ARMORED_OT_fast_crease(bpy.types.Operator):
    '''Fully Crease/Uncrease selected edges (uncrease will apply to all edges if nothing is selected).

(www.armoredColony.com)'''
    
    bl_idname = 'mesh.armored_fast_crease'
    bl_label = 'ARMORED Crease'
    bl_options = {'REGISTER', 'UNDO'}

    crease_mode: EnumProperty( 
        name='Action', 
        description='Crease mode.', 
        default='CREASE', 
        items=[ ('CREASE',   'Crease',   'Selection crease level to 1'),
                ('UNCREASE', 'Uncrease', 'Selection crease level to 0'), ]
        )

    deselect_after_crease : BoolProperty(name='Deselect after Crease', default=True)
    crease_face_border    : BoolProperty(name='Crease Face Border',    default=True)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        row = layout.row(align=True)
        row.prop(self, 'crease_mode', expand=True)

        subrow1 = layout.row(align=True)
        subrow2 = layout.row(align=True)

        if self.crease_mode == 'CREASE':
            # subrow1.prop(self, 'deselect_after_crease')
            # subrow2.prop(self, 'crease_face_border')
            subrow1.enabled = True
            subrow2.enabled = True
        else:
            subrow1.enabled = False
            subrow2.enabled = False

        subrow1.prop(self, 'deselect_after_crease')
        subrow2.prop(self, 'crease_face_border')

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        obj = context.edit_object
        bm = bmesh.from_edit_mesh(obj.data)

        mode = context.tool_settings.mesh_select_mode[:]
        if mode[2]: 
            if self.crease_face_border:
                bpy.ops.mesh.region_to_loop()
        
        sel_components = next((e for e in bm.edges if e.select), None)

        if self.crease_mode == 'UNCREASE':
            if sel_components is None:
                bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.transform.edge_crease(value=-1)
        else:
            bpy.ops.transform.edge_crease(value=1)

        if self.deselect_after_crease:
            bpy.ops.mesh.select_all(action='DESELECT')

        return {'FINISHED'}


class ARMORED_MT_fast_crease(bpy.types.Menu):
    bl_label = 'Fast Crease'
    bl_idname = 'ARMORED_MT_fast_crease'

    def draw(self, context):
        layout = self.layout

        # layout.label(text = 'ARMORED Scripts')
        layout.operator(ARMORED_OT_fast_crease.bl_idname, text='ARMORED Crease').crease_mode = 'CREASE'
        layout.operator(ARMORED_OT_fast_crease.bl_idname, text='ARMORED Uncrease').crease_mode = 'UNCREASE'


def draw_menu(self, context):
    self.layout.separator()
    self.layout.menu(ARMORED_MT_fast_crease.bl_idname, icon='FAKE_USER_OFF')


classes = (
    ARMORED_OT_fast_crease,
    ARMORED_MT_fast_crease,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_edit_mesh_edges.append(draw_menu)
    
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_edit_mesh_edges.remove(draw_menu)