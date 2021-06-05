# v2.1

import bpy
from bpy.props import EnumProperty, StringProperty

class ARMORED_OT_toggle_transform_tool(bpy.types.Operator):
    '''Toggles the specified transform tool.

(armoredColony.com)'''
 
    bl_idname  = 'view3d.armored_toggle_transform_tool'
    bl_label   = 'ARMORED Toggle Transform Tool'
    bl_options = {'REGISTER', 'UNDO'}

    fallback_tool: EnumProperty( 
        name='Fallback Tool', 
        description='Space the aligned vertices evenly or not.', 
        default='builtin.select_box', 
        # default='PREVIOUS', 
        items=[ ('PREVIOUS',           'Previous',   'Revert back to this tool'),
                ('builtin.select_box', 'Box Select', 'Revert back to this tool'), ]
        )
        
    tool: EnumProperty( 
        name='Tool', 
        description='Space the aligned vertices evenly or not.', 
        default='builtin.move', 
        items=[ ('builtin.move',   'Move',   'Toggle the Move Tool'),
                ('builtin.scale',  'Scale',  'Toggle the Scale Tool'),
                ('builtin.rotate', 'Rotate', 'Toggle the Rotate Tool'), ]
        )
    
    previous_tool: StringProperty(name='Previous Tool', default='builtin.select_box')
    
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        layout.prop(self, 'tool', expand=True)
        layout.prop(self, 'fallback_tool', expand=False)


    def execute(self, context):
        current_tool = context.workspace.tools.from_space_view3d_mode(context.mode, create=False).idname

        if current_tool != self.tool:
            self.previous_tool = current_tool
            bpy.ops.wm.tool_set_by_id(name=self.tool)
            # context.scene.tool_settings.workspace_tool_type = 'DEFAULT'
        else:
            if self.fallback_tool == 'PREVIOUS':
                bpy.ops.wm.tool_set_by_id(name=self.previous_tool)
            else:
                bpy.ops.wm.tool_set_by_id(name=self.fallback_tool)

        return {'FINISHED'}


classes = (
    ARMORED_OT_toggle_transform_tool,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)