# v1.3

import bpy
from bpy.props import IntProperty, FloatProperty, BoolProperty, StringProperty, EnumProperty

from mathutils import Matrix



def set_lattice_interpolation(lattice_ob, interpolation_type):
    lattice_ob.data.interpolation_type_u = interpolation_type
    lattice_ob.data.interpolation_type_v = interpolation_type
    lattice_ob.data.interpolation_type_w = interpolation_type
    



class ARMORED_OT_lattice(bpy.types.Operator):
    '''Creates a lattice that matches your object dimensions and transforms.

(www.armoredColony.com)'''

    bl_idname = 'object.armored_lattice'
    bl_label  = 'ARMORED Lattice'
    bl_options = {'REGISTER', 'UNDO'}

    resolution : IntProperty (name='Resolution', default=2, min=2)

    @classmethod
    def poll(cls, context):
        return context.active_object is not None
    
    def execute(self, context):
        self.target = context.object

        if self.target.type not in {'MESH', 'CURVE'}:
            self.report({'ERROR'}, 'Lattice\n This operator only supports MESH types... for now.')
            return {'CANCELLED'}

        if context.active_object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode = 'OBJECT')

        self.lattice_data = bpy.data.lattices.new('Lattice')
        self.lattice = bpy.data.objects.new('Lattice', self.lattice_data)
        # self.lattice.matrix_world = self.target.matrix_world
        self.lattice.dimensions = context.object.dimensions
        self.lattice.location = context.object.location
        self.lattice.rotation_euler  = context.object.rotation_euler 

        context.collection.objects.link(self.lattice)

        bpy.ops.object.select_all(action='DESELECT')

        context.view_layer.objects.active = self.lattice
        self.lattice.select_set(True)
        
        self.lattice_data.points_u = self.resolution
        self.lattice_data.points_v = self.resolution
        self.lattice_data.points_w = self.resolution

        mod = self.target.modifiers.new('Lattice', 'LATTICE')
        mod.object = self.lattice
        
        # This makes it so the mesh scale doesn't get multiplied by the latice scale after parenting.
        self.target.parent = self.lattice
        self.target.matrix_parent_inverse = self.lattice.matrix_world.inverted()

        bpy.ops.object.mode_set(mode = 'EDIT')

        return {'FINISHED'}


class ARMORED_OT_lattice_modal(bpy.types.Operator):
    '''Creates a lattice that matches your object dimensions and transforms (control the modal by scrolling).

(www.armoredColony.com)'''

    bl_idname = 'object.armored_lattice_modal'
    bl_label  = 'ARMORED Lattice (modal)'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def invoke(self, context, event):
        self.target = context.object

        if self.target.type != 'MESH':
            self.report({'ERROR'}, 'Lattice\n Cannot apply Lattice to non-mesh objects.')
            return {'CANCELLED'}

        if context.active_object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode = 'OBJECT')


        self.lattice_data = bpy.data.lattices.new('Lattice')
        self.lattice = bpy.data.objects.new('Lattice', self.lattice_data)
        # self.lattice.matrix_world = self.target.matrix_world
        self.lattice.dimensions = context.object.dimensions
        self.lattice.location = context.object.location
        self.lattice.rotation_euler  = context.object.rotation_euler
        set_lattice_interpolation(self.lattice, interpolation_type='KEY_CATMULL_ROM')

        context.collection.objects.link(self.lattice)

        bpy.ops.object.select_all(action='DESELECT')

        context.view_layer.objects.active = self.lattice
        self.lattice.select_set(True)

        self.report({'INFO'}, 'Scroll Up or Down to add more divisions, LEFTMOUSE to apply.')

        context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}


    def modal(self, context, event):
        context.area.tag_redraw()

        if event.type == 'WHEELUPMOUSE':
            if event.shift:
                self.lattice_data.points_w += 1
            else:
                self.lattice_data.points_u += 1
                self.lattice_data.points_v += 1
                self.lattice_data.points_w += 1
        
        elif event.type == 'WHEELDOWNMOUSE':
            if event.shift:
                self.lattice_data.points_w -= 1
            else:
                self.lattice_data.points_u -= 1
                self.lattice_data.points_v -= 1
                self.lattice_data.points_w -= 1

        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            mod = self.target.modifiers.new('Lattice', 'LATTICE')
            mod.object = self.lattice
            
            # This makes it so the mesh scale doesn't get multiplied by the latice scale after parenting.
            self.target.parent = self.lattice
            self.target.matrix_parent_inverse = self.lattice.matrix_world.inverted()

            bpy.ops.object.mode_set(mode = 'EDIT')

            self.report({'INFO'}, 'Your lattice is ready.')
            return {'FINISHED'}

        elif event.type == 'RIGHTMOUSE' and event.value == 'PRESS':
            bpy.data.objects.remove(self.lattice, do_unlink=True)
            return {'CANCELLED'}

        elif event.type in {'MIDDLEMOUSE'}:
            return {'PASS_THROUGH'}

        return {'RUNNING_MODAL'}


classes = (
    ARMORED_OT_lattice,
    ARMORED_OT_lattice_modal,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
