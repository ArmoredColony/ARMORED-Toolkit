# v1.2

import bpy
from bpy.props import EnumProperty

class ARMORED_OT_subd_toggle(bpy.types.Operator):
    '''Controls how SubD modifiers are displayed in edit mode.

(www.armoredColony.com)'''
    
    bl_idname = 'mesh.armored_subd_toggle'
    bl_label = 'ARMORED Maya SubD Toggle'
    bl_options = {'REGISTER'}

    mode_items = [
                ('OFF',    'Off',               'No Subdivision'               ), 
                ('HYBRID', 'SubD with Cage',    'Subdivision with visible Cage'),
                ('FULL',   'SubD without Cage', 'Subdivision without the Cage' )
    ]
    mode : EnumProperty ( name='Mode', default='FULL', items=mode_items )

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.mode == 'EDIT_MESH'

    def execute(self, context):
        objects_in_edit = [ob for ob in context.selected_objects if context.mode == 'EDIT_MESH']
        if context.object not in objects_in_edit:
            objects_in_edit.append(context.object)

        for ob in objects_in_edit:
            mod = next((mod for mod in reversed(ob.modifiers) if mod.type == 'SUBSURF' and mod.show_viewport), None)
            
            if mod is None:
                mod = context.object.modifiers.new(name='Subdivision', type='SUBSURF')

            if self.mode == 'OFF':
                mod.show_on_cage = False
                mod.show_in_editmode = False

            elif self.mode == 'HYBRID':
                mod.show_on_cage = False
                mod.show_in_editmode = True

            elif self.mode == 'FULL':
                mod.show_on_cage = True
                mod.show_in_editmode = True

        return {'FINISHED'}


class ARMORED_MT_subd_toggle(bpy.types.Menu):
    bl_label = 'SubD Modifier in Edit'
    bl_idname = 'ARMORED_MT_subd_toggle'

    def draw(self, context):
        layout = self.layout

        layout.operator('mesh.armored_subd_toggle', text='ARMORED SubD Off')      .mode = 'OFF'
        layout.operator('mesh.armored_subd_toggle', text='ARMORED SubD with Cage').mode = 'HYBRID'
        layout.operator('mesh.armored_subd_toggle', text='ARMORED SubD Only')     .mode = 'FULL'


def menu_func(self, context):
    self.layout.separator()
    self.layout.menu(ARMORED_MT_subd_toggle.bl_idname, icon='FAKE_USER_OFF')


classes = (
    ARMORED_OT_subd_toggle,
    ARMORED_MT_subd_toggle,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_edit_mesh.append(menu_func)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_edit_mesh.remove(menu_func)
