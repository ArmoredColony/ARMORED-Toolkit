# v1.2

import bpy
from bpy.props import EnumProperty, BoolProperty, IntProperty


class ARMORED_OT_single_subdivision_level(bpy.types.Operator):
    '''Adds a single subdivision modifier level to all selected objects (ignores non-MESH objects automatically)

(www.armoredColony.com)'''
    
    bl_idname = 'view3d.armored_single_subdivision_level'
    bl_label = 'ARMORED Subdivision Level'
    bl_options = {'REGISTER', 'UNDO'}

    action: EnumProperty(
        name='Action', 
        description='Increase or Decrease the current SubD level by 1',
        default='INCREASE',
        # options={'HIDDEN'},
        items=[ ('INCREASE', 'Increase', 'Increase Subdivision level by 1'), 
                ('DECREASE', 'Decrease', 'Decrease Subdivision level by 1'),
                ]
        )

    sync_render_levels: BoolProperty(
        name='Sync Render Levels',
        description='If enabled, the Render levels will increase along with the viewport levels',
        default=True,
        )

    render_level_offset: IntProperty(
        name='Render Offset',
        description='Match viewport levels and then add this ammount on top',
        default=1, 
        min=0, max=5,
        )
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        
        row = layout.row(align=False)
        # row.prop(self, 'action', expand=True)
        row.label(text=f'   Action: {self.action}')
        layout.separator()

        box = layout.box()
        row = box.row(align=True)
        row.prop(self, 'sync_render_levels')

        sub = box.row(align=True)
        sub.active = True if self.sync_render_levels else False
        sub.prop(self, 'render_level_offset')

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def invoke(self, context, event):
        self.selected_objects = [ob for ob in context.selected_objects if ob.type == 'MESH']

        if context.object not in self.selected_objects and context.object.type == 'MESH':
            self.selected_objects.append(context.object)

        for ob in self.selected_objects:
            mod = next((mod for mod in reversed(ob.modifiers) if mod.type == 'SUBSURF' and mod.show_viewport), None)
        
            if mod is None:
                mod = ob.modifiers.new(name='Subdivision', type='SUBSURF')
                mod.levels = 1
            
            else:
                if self.action == 'INCREASE':
                    mod.levels += 1

                elif self.action == 'DECREASE':
                    mod.levels -= 1

        if context.object.mode == 'OBJECT':
            bpy.ops.ed.undo_push()

        return self.execute(context)


    def execute(self, context):
        if context.object.mode == 'OBJECT':
            self.selected_objects = [ob for ob in context.selected_objects if ob.type == 'MESH']

            if context.object not in self.selected_objects and context.object.type == 'MESH':
                self.selected_objects.append(context.object)

        for ob in  self.selected_objects:
            mod = next((mod for mod in reversed(ob.modifiers) if mod.type == 'SUBSURF' and mod.show_viewport), None)

            if self.sync_render_levels:
                mod.render_levels = mod.levels + self.render_level_offset

        if context.object.mode == 'OBJECT':
            bpy.ops.ed.undo_push()

        return {'FINISHED'}


class ARMORED_MT_single_subdivision_level(bpy.types.Menu):
    bl_label = 'SubD Modifier Level'
    bl_idname = 'ARMORED_MT_single_subdivision_level'

    def draw(self, context):
        layout = self.layout

        # layout.label(text = 'ARMORED Scripts')
        layout.operator(ARMORED_OT_single_subdivision_level.bl_idname, text='ARMORED Subdiv Level Up').action = 'INCREASE'
        layout.operator(ARMORED_OT_single_subdivision_level.bl_idname, text='ARMORED Subdiv Level Down').action = 'DECREASE'


def draw_menu(self, context):
    self.layout.separator()
    self.layout.menu(ARMORED_MT_single_subdivision_level.bl_idname, icon='FAKE_USER_OFF')


classes = (
    ARMORED_OT_single_subdivision_level,
    ARMORED_MT_single_subdivision_level,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_object.append(draw_menu)
    bpy.types.VIEW3D_MT_edit_mesh.append(draw_menu)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_object.remove(draw_menu)
    bpy.types.VIEW3D_MT_edit_mesh.remove(draw_menu)
