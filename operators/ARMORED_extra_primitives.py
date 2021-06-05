# v1.1

import bpy, bmesh
from bpy.props import IntProperty, BoolProperty, FloatProperty, EnumProperty
from math import radians


class ARMORED_OT_cube(bpy.types.Operator):
    '''Cube Primitive with adjustable segments.

(www.armoredColony.com)'''

    bl_idname = 'mesh.armored_cube'
    bl_label = 'ARMORED Cube'
    bl_description = 'Creates a Cube with adjustable segments'
    bl_options = {'REGISTER', 'UNDO'}

    align_options = (
                ('WORLD',  'World',  'Align to World'), 
                ('VIEW',   'View',   'Align to View'),
                ('CURSOR', 'Cursor', 'Align to Cursor')
    )
    
    size           : FloatProperty ( name='Size',         default=2, min=0.001 )
    subdivisions   : IntProperty   ( name='Subdivisions', default=0, min=0, max=30 )
    align_rotation : EnumProperty  ( name='Align', items=align_options, default='WORLD' )


    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT', 'EDIT_MESH'}

    def execute(self, context):
        bpy.ops.mesh.primitive_cube_add(size=self.size, align=self.align_rotation)
        mode = bpy.context.mode

        if mode == 'OBJECT':
            bpy.ops.object.mode_set(mode='EDIT')

        if self.subdivisions > 0:
            bpy.ops.mesh.subdivide(number_cuts=self.subdivisions, smoothness=0)

        bpy.ops.mesh.select_all(action='DESELECT')

        return {'FINISHED'}


class ARMORED_OT_quadsphere(bpy.types.Operator):
    '''Quad Sphere Primitive.

(www.armoredColony.com)'''

    bl_idname = 'mesh.armored_quadsphere'
    bl_label = 'ARMORED Quadsphere'
    bl_description = 'Creates a Quadsphere'
    bl_options = {'REGISTER', 'UNDO'}

    align_options = (
                ('WORLD',  'World',  'Align to World'), 
                ('VIEW',   'View',   'Align to View'),
                ('CURSOR', 'Cursor', 'Align to Cursor')
    )

    subdivisions   : IntProperty   ( name='Subdivisions', default=4, min=1, max=20 )
    smoothness     : FloatProperty ( name='Smoothness',   default=1, min=0, max=1  )
    sphere_cast    : BoolProperty  ( name='Sphere Cast',  default=True)
    align_rotation : EnumProperty  ( name='Align', items=align_options, default='WORLD' )

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT', 'EDIT_MESH'}

    def execute(self, context):
        bpy.ops.mesh.primitive_cube_add(align=self.align_rotation)     
        mode = bpy.context.mode

        if mode == 'OBJECT':
            bpy.ops.object.mode_set(mode='EDIT')
                
        bpy.ops.mesh.subdivide(number_cuts=self.subdivisions, smoothness=self.smoothness)
        if self.sphere_cast:
            bpy.ops.transform.tosphere(value=1)

        if mode == 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

            # Have to figure out how scale the mesh data directly in edit mode.
            context.object.dimensions = (2, 2, 2)
            bpy.ops.object.transform_apply(location=False, scale=True, rotation=False)
        
        return {'FINISHED'}


class ARMORED_OT_single_vertex(bpy.types.Operator):
    '''Add a single vertext and enter edit mode.

(www.armoredColony.com)'''

    bl_idname = 'mesh.armored_single_vertex'
    bl_label = 'ARMORED Single Vert'
    bl_description = 'Add a Single Vertice to Edit Mode'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT', 'EDIT_MESH'}

    def execute(self, context):
        mesh = bpy.data.meshes.new('Vert')
        mesh.vertices.add(1)

        from bpy_extras import object_utils
        object_utils.object_data_add(context, mesh, operator=None)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.context.tool_settings.mesh_select_mode = (True, False, False)

        return {'FINISHED'}


def draw_menu(self, context):
    self.layout.separator()
    self.layout.operator(ARMORED_OT_cube.bl_idname,          text='Maya Cube',     icon='CUBE')
    self.layout.operator(ARMORED_OT_quadsphere.bl_idname,    text='Quad Sphere',   icon='SPHERE')
    self.layout.operator(ARMORED_OT_single_vertex.bl_idname, text='Single Vertex', icon='DOT')


classes = (
    ARMORED_OT_cube,
    ARMORED_OT_quadsphere,
    ARMORED_OT_single_vertex,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_mesh_add.append(draw_menu)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    bpy.types.VIEW3D_MT_mesh_add.remove(draw_menu)


