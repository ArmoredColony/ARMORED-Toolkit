# v1.2

import bpy, bmesh
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty




class ARMORED_OT_subdivide(bpy.types.Operator):
    '''Destructively subdivides the selected object (no modifiers). If a SubD modifier already exists it will subdivide and then subtract 1 level from the modifier to maintain the polycount).

 (www.armoredColony.com)'''
    
    bl_idname = 'view3d.armored_subdivide'
    bl_label = 'ARMORED Subdivide'
    bl_options = {'REGISTER', 'UNDO'}

    subdivision_type: EnumProperty(name='Type', default='CATMULL_CLARK',
            items={ ('CATMULL_CLARK', 'Catmull-Clark', 'Smooth Catmul Clark Subdivision'),
                    ('SIMPLE',        'Flat',   'Flat Subdivision') })

    ngons:            BoolProperty(name='Create N-Gons', default=True)
    limit_surface:    BoolProperty(name='Limit Surface', default=False)

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)

        col.row().prop(self, 'subdivision_type', expand=True)
        col.separator()
        col.prop(self, 'ngons')
        col.prop(self, 'limit_surface')
    
    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        mode = context.object.mode
        original_active = context.object
        filtered_objects = [ob for ob in context.selected_objects if ob.type in {'MESH'}]

        if not filtered_objects:
            self.report({'WARNING'}, 'ARMORED Toolkit: No valid objects were selected.')
            return {'CANCELLED'}

        if mode == 'SCULPT':
            mod = next((mod for mod in reversed(context.object.modifiers) if mod.type == 'MULTIRES' and mod.show_viewport), None)
            if mod is None:
                mod = context.object.modifiers.new(name='Multires', type='MULTIRES')

            bpy.ops.object.multires_subdivide(modifier='Multires', mode='CATMULL_CLARK')
            return {'FINISHED'}

        if mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')

        for ob in filtered_objects:
            mod = next((mod for mod in reversed(ob.modifiers) if mod.type == 'SUBSURF' and mod.show_viewport), None)
            if mod is not None:
                mod.levels -= 1
            
            mod = ob.modifiers.new(name='temp subd', type='SUBSURF')
            mod.subdivision_type = self.subdivision_type
            mod.boundary_smooth = 'PRESERVE_CORNERS'
            mod.use_limit_surface = self.limit_surface

            context.view_layer.objects.active = ob
            bpy.ops.object.modifier_apply(modifier=mod.name)

        context.view_layer.objects.active = original_active
        bpy.ops.object.mode_set(mode=mode)

        return {'FINISHED'}




classes = (
    ARMORED_OT_subdivide,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)    


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
