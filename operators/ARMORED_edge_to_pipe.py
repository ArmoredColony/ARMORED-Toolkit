# v1.2

import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty
import bgl
import blf


def draw_callback_px(self, context):
    font_id = 0  # need to find out how best to get this.

    # draw some text
    blf.position(font_id, self.pos_x+30, self.pos_y+30, 0)
    blf.size(font_id, 20, 72)
    blf.draw(font_id, str(self.pipe.data.bevel_resolution*2+4) + " Sides")


class ARMORED_OT_edge_to_pipe(bpy.types.Operator):
    '''Dinamically create a pipe from any selected edges or curves.

(www.armoredColony.com)'''

    bl_idname = 'mesh.armored_edge_to_pipe'
    bl_label = 'ARMORED Edge to Pipe'
    bl_options = {'REGISTER', 'UNDO'}

    start_mouse_x : IntProperty()   
    pipe_radius   : FloatProperty()
    pos_x         : IntProperty()
    pos_y         : IntProperty()
    flat_shade    : BoolProperty(default=True)

    @classmethod
    def poll(cls, context):
        ob = context.object
        return  ob is not None and (ob.type == 'CURVE' or context.mode == 'EDIT_MESH')

    def modal(self, context, event):
        context.area.tag_redraw()
        
        if (event.type == 'S') and (event.value == 'PRESS'):
            self.flat_shade = not self.flat_shade
            bpy.ops.object.shade_flat() if self.flat_shade else bpy.ops.object.shade_smooth()

        if event.type == 'MOUSEMOVE':
            self.pos_x = event.mouse_x
            self.pos_y = event.mouse_y

            delta = self.start_mouse_x - event.mouse_x
            context.object.data.bevel_depth = self.pipe_radius + delta * 0.003
        
        elif event.type == 'WHEELUPMOUSE':
            bpy.context.object.data.bevel_resolution += 1

        elif event.type == 'WHEELDOWNMOUSE':
            if bpy.context.object.data.bevel_resolution > 0:         
                bpy.context.object.data.bevel_resolution -= 1
        
        elif event.type == 'LEFTMOUSE':
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'FINISHED'}

        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            context.object.data.bevel_depth = self.pipe_radius     
            bpy.context.object.data.bevel_resolution = self.pipe_segments
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        if context.object.type == 'CURVE' :
            self.pipe = context.object
        
        if context.object.type == 'MESH':
            bpy.ops.mesh.duplicate()
            bpy.ops.mesh.separate(type='SELECTED')

            obj = context.object
            bpy.ops.object.editmode_toggle()
            
            obj.select_set(False)

            context.view_layer.objects.active = context.selected_objects[-1]
            bpy.ops.object.convert(target='CURVE')

            self.pipe = bpy.context.view_layer.objects.active           
            self.pipe.data.fill_mode = 'FULL'
            self.pipe.data.splines[0].use_smooth = True
                    
        self.start_mouse_x = event.mouse_x
        self.pipe_radius = self.pipe.data.bevel_depth
        self.pipe_segments = self.pipe.data.bevel_resolution
        
        if context.mode == 'EDIT_CURVE':
            bpy.ops.object.editmode_toggle()

        if self.flat_shade:
            bpy.ops.object.shade_flat()
        else:
            bpy.ops.object.shade_smooth()
        
        args = (self, context)
        self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_callback_px, args, 'WINDOW', 'POST_PIXEL')
        context.window_manager.modal_handler_add(self)
        
        return {'RUNNING_MODAL'}


classes = (
    ARMORED_OT_edge_to_pipe,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)