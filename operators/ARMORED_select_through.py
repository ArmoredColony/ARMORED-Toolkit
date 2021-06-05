# v1.3

import bpy
from bpy.props import StringProperty, EnumProperty


class ARMORED_OT_select_through(bpy.types.Operator):
    '''Binds "RMB Click Drag" to toggle X-ray mode and enable Box Select at the same time, simulating select-through like Maya

(www.armoredColony.com)'''

    bl_idname = 'mesh.armored_select_through'
    bl_label  = 'ARMORED Select Through Box'
    bl_options = {'REGISTER', 'UNDO'}

    # mode: StringProperty(name='Select Mode', defaul='SET', description='yeah whatever')

    mode: EnumProperty( 
        name='Mode', 
        description='Selection Mode', 
        default='SET', 
        items=[ ('SET', 'Set',      'Create a new selecton'),
                ('ADD', 'Add',      'Add to the current selection'),
                ('SUB', 'Subtract', 'Subtract from the curent selection'), ]
        )

    def invoke(self, context, event):
        bpy.context.space_data.shading.show_xray = True
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def modal(self, context, event):
        # bpy.context.space_data.shading.show_xray = True
        # bpy.context.space_data.shading.type = 'WIREFRAME'

        if event.type == 'MOUSEMOVE' and event.value == 'PRESS':
            bpy.ops.view3d.select_box('INVOKE_DEFAULT', mode=self.mode, wait_for_input=False)
            return {'RUNNING_MODAL'}

        elif event.type == 'MOUSEMOVE' and event.value == 'RELEASE':
            bpy.context.space_data.shading.show_xray = False
            # bpy.context.space_data.shading.type = 'SOLID'
            return {'CANCELLED'}

        return {'RUNNING_MODAL'}


# class ARMORED_OT_select_through_lasso(bpy.types.Operator):

#     bl_idname = 'armored.select_through_lasso'
#     bl_label  = 'ARMORED Select Through Lasso'
#     bl_options = {'REGISTER', 'UNDO'}

#     mode : bpy.props.StringProperty (name='Select Mode', default = 'SET')

#     def invoke(self, context, event):
#         context.window_manager.modal_handler_add(self)
#         return {'RUNNING_MODAL'}

#     def modal(self, context, event):
#         bpy.context.space_data.shading.show_xray = True
#         # bpy.context.space_data.shading.type = 'WIREFRAME'

#         if event.type == 'MOUSEMOVE' and event.value == 'PRESS':
#             bpy.ops.view3d.select_lasso('INVOKE_DEFAULT', mode=self.mode)
#             return {'RUNNING_MODAL'}

#         elif event.type == 'MOUSEMOVE' and event.value == 'RELEASE':
#             bpy.context.space_data.shading.show_xray = False
#             # bpy.context.space_data.shading.type = 'SOLID'
#             return {'CANCELLED'}

#         return {'RUNNING_MODAL'}

classes = (
    ARMORED_OT_select_through,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)