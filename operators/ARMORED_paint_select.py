import bpy
# from bpy.props import IntProperty, FloatProperty

# v0.6

class ARMORED_OT_paint_select(bpy.types.Operator):
    '''Paint Select like Modo (bind it to a single key, like "Q") (Experimental)

(www.armoredColony.com)'''

    bl_idname = 'view3d.armored_paint_select'
    bl_label = 'ARMORED Paint Select'
    bl_options = {'REGISTER', 'UNDO'}

    def invoke(self, context, event):
        self.painted = False
        self.selecting = False
        self.deselecting = False
        self.first_key = event.type

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):

        if event.type == 'LEFTMOUSE':
            if event.value == 'PRESS':
                self.selecting = True
                self.painted = True
            else:
                self.selecting = False

        if event.type == 'RIGHTMOUSE':
            if event.value == 'PRESS':
                self.deselecting = True
            else:
                self.deselecting = False

        if event.type == self.first_key and event.value == 'RELEASE':    
            if not self.painted:
                bpy.ops.wm.tool_set_by_id(name='builtin.select_box')
            return {'FINISHED'}

        elif event.type in {'ESC'}:
            return {'CANCELLED'}
        
        if self.selecting:
            bpy.ops.view3d.select('INVOKE_DEFAULT', extend=True, deselect=False)
        if self.deselecting:
            bpy.ops.view3d.select('INVOKE_DEFAULT', extend=False, deselect=True)

        return {'RUNNING_MODAL'}


classes = (
    ARMORED_OT_paint_select,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)    


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
