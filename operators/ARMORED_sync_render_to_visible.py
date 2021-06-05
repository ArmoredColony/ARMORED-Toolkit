# v1.1

import bpy
from bpy.props import EnumProperty, BoolProperty


class ARMORED_OT_sync_render_to_viewport(bpy.types.Operator):
    '''Syncronizes render visibility to match object visibility (what you see what you render).

(www.armoredColony.com)'''
    
    sync_meshes  : BoolProperty(name='Sync Meshes', default=True, description='Sync Mesh Render visibility to Viewport visibility.')
    sync_curves  : BoolProperty(name='Sync Curves', default=True, description='Sync Curve Render visibility to Viewport visibility.')
    sync_lights  : BoolProperty(name='Sync Lights', default=True, description='Sync Light Render visibility to Viewport visibility.')
    sync_fonts   : BoolProperty(name='Sync Text',   default=True, description='Sync Text Object Render visibility to Viewport visibility.')
    
    bl_idname = 'view3d.armored_sync_render_to_viewport'
    bl_label = 'ARMORED Sync Render to Viewport'
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        layout.label(text='Sync by Type:')
        layout.prop(self, 'sync_meshes',  text='Mesh')
        layout.prop(self, 'sync_curves',  text='Curve')
        layout.prop(self, 'sync_lights',  text='Light')
        layout.prop(self, 'sync_fonts',   text='Text')
    
    def execute(self, context):
        # Sync Collections.
        ignore_collections_with_name = {'light', 'lights','scene lights'}
        if self.sync_lights:
            ignore_collections_with_name = {}

        vlayer = context.view_layer
        for col in context.scene.collection.children:
            if col.name.lower() not in ignore_collections_with_name:
                col.hide_render = vlayer.layer_collection.children[col.name].hide_viewport

        # Sync Individual Objects.
        objects = context.scene.objects
        meshes  = (ob for ob in objects if ob.type == 'MESH')
        curves  = (ob for ob in objects if ob.type == 'CURVE')
        lights  = (ob for ob in objects if ob.type == 'LIGHT')
        fonts   = (ob for ob in objects if ob.type == 'FONT')

        if self.sync_meshes:
            for ob in meshes:
                ob.hide_render = ob.hide_get()

        if self.sync_curves:
            for ob in curves:
                ob.hide_render = ob.hide_get()

        if self.sync_lights:
            for ob in lights:
                ob.hide_render = ob.hide_get()

        if self.sync_fonts:
            for ob in fonts:
                ob.hide_render = ob.hide_get()

        return {'FINISHED'}


def draw_sync_button(self, context):
    self.layout.operator(ARMORED_OT_sync_render_to_viewport.bl_idname, icon='RESTRICT_RENDER_OFF', text='')

classes = (
    ARMORED_OT_sync_render_to_viewport,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.OUTLINER_HT_header.append(draw_sync_button)
    # bpy.types.VIEW3D_HT_header.prepend(draw_sync_button)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.OUTLINER_HT_header.remove(draw_sync_button)
    # bpy.types.VIEW3D_HT_header.remove(draw_sync_button)