# v1.2

import bpy, bmesh
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty


def anything_selected(context):
    me = context.edit_object.data
    bm = bmesh.from_edit_mesh(me)
    
    return next((v for v in bm.verts if v.select), None)


class ARMORED_OT_subdivide(bpy.types.Operator):
    '''Destructively subdivides the selected object (no modifiers). If a SubD modifier already exists it will subdivide and then subtract 1 level from the modifier to maintain the polycount).

 (www.armoredColony.com)'''
    
    bl_idname = 'view3d.armored_subdivide'
    bl_label = 'ARMORED Subdivide'
    bl_options = {'REGISTER', 'UNDO'}

    subdivision_type: EnumProperty(name='Type', default='CATMULL_CLARK',
            items={ ('CATMULL_CLARK', 'Catmull-Clark', 'Smooth Catmul Clark Subdivision'),
                    ('SIMPLE',        'Flat',   'Flat Subdivision') })

    # subdivisions:     IntProperty(name='Subdivisions', default=1, min=1, max=20, options={'SKIP_SAVE', 'HIDDEN'})
    ngons:            BoolProperty(name='Create N-Gons', default=True)
    limit_surface:    BoolProperty(name='Limit Surface', default=False)

    # smoothness:       FloatProperty(name='Smoothness',    default=0, min=0, max=1)

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
        previous_mode = False
        filtered_objects = [ob for ob in context.selected_objects if ob.type in {'MESH'}]

        if not filtered_objects:
            self.report({'WARNING'}, 'ARMORED Toolkit: No valid objects were selected.')
            return {'CANCELLED'}

        original_active = context.object

        if mode == 'SCULPT':
            bpy.ops.object.mode_set(mode='OBJECT')

            mod = next((mod for mod in reversed(context.object.modifiers) if mod.type == 'MULTIRES' and mod.show_viewport), None)
            if mod is None:
                mod = context.object.modifiers.new(name='Multires', type='MULTIRES')

            bpy.ops.object.multires_subdivide(modifier='Multires', mode='CATMULL_CLARK')
            mod.sculpt_levels += 1
            mod.levels = mod.sculpt_levels
            
            bpy.ops.object.mode_set(mode=mode)
            return {'FINISHED'}

        if mode == 'EDIT':
            bpy.ops.object.mode_set(mode='OBJECT')
            # if anything_selected(context) is None:
            #     bpy.ops.object.mode_set(mode='OBJECT')

            # else:
            #     me = context.edit_object.data
            #     bm = bmesh.from_edit_mesh(me)
            #     sel_mode = context.tool_settings.mesh_select_mode[:]

            #     if sel_mode[1]:
            #         edges = set(e for e in bm.edges if e.select)

            #         # If only one edge is selected, switch to vert mode so you can see the divisions being added.
            #         if len(edges) == 1: 
            #             bpy.ops.mesh.select_mode(type='VERT')
            
            #     bpy.ops.mesh.subdivide(number_cuts=1, ngon=self.ngons)
            #     return {'FINISHED'}
                

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
