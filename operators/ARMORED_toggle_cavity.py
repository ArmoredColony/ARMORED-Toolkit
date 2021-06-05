import bpy
from bpy.props import EnumProperty

# v1.5

class ARMORED_OT_toggle_cavity(bpy.types.Operator):
    '''Toggle Cavity On/Off (Optional: set specific cavity type to be used. Defaults to 'SCREEN')

(www.armoredColony.com)'''

    bl_idname  = 'view3d.armored_toggle_cavity'
    bl_label   = 'ARMORED Toggle Cavity'
    bl_options = {'REGISTER'}

    cavity_type_items = [
                ('SCREEN',  'Screen',  'Screen Space Cavities'), 
                ('WORLD',   'World',   'World Space Cavities'),
                ('BOTH',    'Screen',  'Screen + World Space Cavities'),
                ('CURRENT', 'Current', 'Use the current type'),
    ]
    cavity_type : bpy.props.EnumProperty (name='cavity_type', items=cavity_type_items, default='CURRENT')
   
    def execute(self, context):
        context.space_data.shading.show_cavity = not context.space_data.shading.show_cavity

        if self.cavity_type != 'CURRENT':
            context.space_data.shading.cavity_type = self.cavity_type
        
        # World Cavity (AO) Options >>
        context.scene.display.matcap_ssao_samples = 64          # The sample number updates but the viewport does NOT?
        context.space_data.shading.cavity_ridge_factor  = 1.5
        context.space_data.shading.cavity_valley_factor = 1.5
        bpy.context.preferences.studio_lights.refresh()

        return {'FINISHED'}


class ARMORED_OT_cycle_cavity_type(bpy.types.Operator):
    '''Cycle through the different Cavity types)

(www.armoredColony.com)'''

    bl_idname  = 'view3d.armored_cycle_cavity_type'
    bl_label   = 'ARMORED Cycle Cavity Type'
    bl_options = {'REGISTER'}

    def execute(self, context):

        def switch(context):
            switcher = {
                'SCREEN': 'WORLD',
                'WORLD':  'BOTH',
                'BOTH':   'SCREEN',
            }

            return switcher[context.space_data.shading.cavity_type]

        self.report({'INFO'}, f'Cavity Type: {switch(context)}')
        context.space_data.shading.cavity_type = switch(context)

        return {'FINISHED'}


classes = (
    ARMORED_OT_toggle_cavity,
    ARMORED_OT_cycle_cavity_type,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
