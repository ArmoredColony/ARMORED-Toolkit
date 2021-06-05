# v1.1

import bpy, bmesh
from bpy.props import BoolProperty


class ARMORED_OT_focus(bpy.types.Operator):
    '''Ignores geometry created by the mirror modifier when focusing on the selected object.

(www.armoredColony.com)'''
    
    bl_idname = 'mesh.armored_focus'
    bl_label = 'ARMORED Focus'
    bl_options = {'REGISTER'}
    # bl_options = {'REGISTER', 'UNDO'}

    ignore_mirrors: BoolProperty(
        name='Ignore Mirrors', 
        description='Ignores Mirror Modifiers when focusing on the selected object.', 
        default=False,
    )

    smooth_focus: BoolProperty(
        name='Smooth Focus', 
        description='Focuses on the selected object with a smooth transition.', 
        default=True,
    )
    
    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text='Focus Selected')
        column = box.column()

        column.prop(self, 'ignore_mirrors', toggle=True)
        column.prop(self, 'smooth_focus', toggle=True)

    # @classmethod
    # def poll(cls, context):
    #     return context.space_data.type == 'VIEW_3D' and context.region.type == 'WINDOW'

    def execute(self, context):
        mirror_mods = []
        sel_components = True

        if context.mode == 'OBJECT':
            selection = context.selected_objects

            if not selection:
                bpy.ops.view3d.view_all('INVOKE_DEFAULT') if self.smooth_focus else bpy.ops.view3d.view_all()
                return {'FINISHED'}

            if self.ignore_mirrors:
                mirror_mods = [mod for obj in selection for mod in obj.modifiers if mod.type == 'MIRROR' and mod.show_viewport]

                for mod in mirror_mods:
                    mod.show_viewport = False
        
        elif context.mode == 'EDIT_MESH': 
            obj = context.edit_object
            bm = bmesh.from_edit_mesh(obj.data)
            mode = context.tool_settings.mesh_select_mode[:]
            
            if mode[1]:
                sel_components = next((e for e in bm.edges if e.select), None)
            else:
                sel_components = next((v for v in bm.verts if v.select), None)

            if sel_components is None:
                bpy.ops.mesh.select_all(action='SELECT')

        bpy.ops.view3d.view_selected('INVOKE_DEFAULT') if self.smooth_focus else bpy.ops.view3d.view_selected()
        
        if sel_components is None: 
            bpy.ops.mesh.select_all(action='DESELECT')

        for mod in mirror_mods:
            mod.show_viewport = True

        return {'FINISHED'}

    
classes = (
    ARMORED_OT_focus,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)