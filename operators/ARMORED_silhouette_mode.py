# v1.0

import bpy
from bpy.props import StringProperty, BoolProperty


class MESH_OT_silhouette_mode(bpy.types.Operator):
    '''Provides additional functionality to the view_selected operator, such as re-centering the object even if you don't have any components selected, or framing all the objects in the scene if no object is selected.

(www.armoredColony.com)'''
    
    bl_idname = 'view3d.armored_silhouette_mode'
    bl_label = 'ARMORED Silhouette Mode'
    bl_options = {'REGISTER'}
    
    last_mode          : StringProperty(name='Previous Mode',          default='MATCAP')
    last_cavity        : StringProperty(name='Previous Cavity',        default='BOTH')
    last_fade_inactive : BoolProperty(  name='Previous Fade Inactive', default=False)

    def set_flat_mode(self, context):
        space_data = context.space_data
        space_data.shading.light = 'FLAT'
        space_data.shading.cavity_type = 'WORLD'
        space_data.overlay.show_fade_inactive = False
    
    def update_last_mode(self, context):
        space_data = context.space_data
        self.last_mode = space_data.shading.light
        self.last_cavity = space_data.shading.cavity_type
        self.last_fade_inactive = space_data.overlay.show_fade_inactive

    def set_last_mode(self, context):
        space_data = context.space_data
        space_data.shading.light = self.last_mode
        space_data.shading.cavity_type = self.last_cavity
        space_data.overlay.show_fade_inactive = self.last_fade_inactive

    def invoke(self, context, event):
        if context.space_data.shading.light == 'FLAT':
            self.set_last_mode(context)
        else:
            self.update_last_mode(context)
            self.set_flat_mode(context)

        return {'FINISHED'}

    
classes = (
    MESH_OT_silhouette_mode,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)