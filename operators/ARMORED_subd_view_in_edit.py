# v1.3

import bpy
from bpy.props import EnumProperty, BoolProperty



def get_subd_modifiers(self, context, obj):
    return [mod for mod in reversed(obj.modifiers) if mod.type == 'SUBSURF' and mod.show_viewport]
    

class ARMORED_OT_subd_view_in_edit(bpy.types.Operator):
    '''Control how SubD modifiers are displayed in edit mode for the selected objects'.

(www.armoredColony.com)'''
    
    bl_idname = 'mesh.armored_subd_view_in_edit'
    bl_label = 'ARMORED SubD View in Edit'
    bl_options = {'REGISTER'}

    mode: EnumProperty(name='Mode', default='FULL', 
            description='Control how SubD modifiers are displayed in edit mode for the selected objects',
            items=[ ('OFF',    'Off',               'No Subdivision'               ), 
                    ('HYBRID', 'SubD with Cage',    'Subdivision with visible Cage'),
                    ('FULL',   'SubD without Cage', 'Subdivision without the Cage' ),   ])

    only_affect_last: BoolProperty(name='Only Affect Last', default=False, 
            description='Only affect the last SubD modifier in the stack',)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.mode == 'EDIT_MESH'

    def execute(self, context):
        objects_in_edit = [ob for ob in context.selected_objects if context.mode == 'EDIT_MESH']
        
        if context.active_object not in objects_in_edit:
            objects_in_edit.append(context.active_object)

        for ob in objects_in_edit:
            mods = get_subd_modifiers(self, context, obj=ob)
            
            if not mods:
                mod = context.active_object.modifiers.new(name='Subdivision', type='SUBSURF')

            if self.only_affect_last:
                mods = [mods[0]]

            for mod in mods:    
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


class ARMORED_MT_subd_view_in_edit(bpy.types.Menu):
    bl_label = 'SubD View in Edit'
    bl_idname = 'ARMORED_MT_subd_view_in_edit'

    def draw(self, context):
        layout = self.layout

        layout.operator('mesh.armored_subd_view_in_edit', text='ARMORED SubD Off')      .mode = 'OFF'
        layout.operator('mesh.armored_subd_view_in_edit', text='ARMORED SubD with Cage').mode = 'HYBRID'
        layout.operator('mesh.armored_subd_view_in_edit', text='ARMORED SubD Only')     .mode = 'FULL'


def menu_func(self, context):
    self.layout.separator()
    self.layout.menu(ARMORED_MT_subd_view_in_edit.bl_idname, icon='FAKE_USER_OFF')


classes = (
    ARMORED_OT_subd_view_in_edit,
    ARMORED_MT_subd_view_in_edit,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_edit_mesh.append(menu_func)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_edit_mesh.remove(menu_func)
