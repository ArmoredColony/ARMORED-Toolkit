# v1.1

import bpy


class ARMORED_MT_PIE_select(bpy.types.Menu):
    '''Pie menu for all selection tools.

(www.armoredColony.com)'''

    bl_idname = 'ARMORED_MT_PIE_select'
    bl_label = 'ARMORED Pie Select Tools'

    def draw(self, context):
        # Note: the position of these menus is only accurate if you activate them from top to bottom as needed.

        pie = self.layout.menu_pie()

        # LEFT
        pie.operator('wm.tool_set_by_id', text='Box Select', icon='SELECT_SET').name = 'builtin.select_box'

        # RIGHT
        pie.operator('wm.tool_set_by_id', text='Paint Select', icon='BRUSH_DATA').name = 'builtin.select_circle'

        # BOTTOM
        pie.operator('wm.tool_set_by_id', text='Lasso Select', icon='GP_SELECT_POINTS').name = 'builtin.select_lasso'

        # TOP
        pie.operator('wm.tool_set_by_id', text='Select/Tweak', icon='RESTRICT_SELECT_OFF').name = 'builtin.select'

        # TOP LEFT
        # pie.operator('mesh.primitive_cube_add', text='Top Left', icon='BLENDER')

        # TOP RIGHT
        # pie.operator('mesh.primitive_cube_add', text='Top Right', icon='BLENDER')

        # BOTTOM LEFT
        # pie.operator('mesh.primitive_cube_add', text='Bottom Left', icon='BLENDER')

        # BOTTOM RIGHT
        # pie.operator('mesh.primitive_cube_add', text='Bottom Right', icon='BLENDER')



classes = (
    ARMORED_MT_PIE_select,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()

    bpy.ops.wm.call_menu_pie(name=ARMORED_MT_PIE_select.bl_idname)
