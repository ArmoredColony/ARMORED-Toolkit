# v1.4

import bpy
from bpy.props import FloatProperty


class ARMORED_OT_autosmooth(bpy.types.Operator):
    '''Switches between Autosmooth by angle and Flat Shading (ignores any selections that are not Meshes).

(www.armoredColony.com)'''
    
    bl_idname = 'view3d.armored_autosmooth'
    bl_label = 'ARMORED Autosmooth'
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        selected_objects = set(ob for ob in context.selected_objects if ob.type == 'MESH')

        # If the active object is not a mesh, get a mesh from our selection instead.
        if context.object.type == 'MESH':
            active = context.object
            selected_objects.add(context.object)
        else:
            if selected_objects:
                active = next(iter(selected_objects))
            else:
                self.report({'WARNING'}, 'Nothing to Autosmooth')
                return {'CANCELLED'}

        auto_smooth  = not active.data.use_auto_smooth
        # smooth_angle = 0.610865 # 35 deg

        # Make all the objects match the toggled properties of the active object.
        for ob in selected_objects:
            ob.data.use_auto_smooth   = auto_smooth
            # ob.data.auto_smooth_angle = smooth_angle
        
        sel_status = context.object.select_get()
        context.object.select_set(True)

        current_mode = context.object.mode # context.mode returns EDIT_MESH, while .object returns EDIT.
        previous_mode = False

        if current_mode != 'OBJECT':
            previous_mode = current_mode
            bpy.ops.object.mode_set(mode='OBJECT', toggle = False)

        if active.data.use_auto_smooth:
            bpy.ops.object.shade_smooth()
        else:
            bpy.ops.object.shade_flat()

        if previous_mode:
            bpy.ops.object.mode_set(mode=previous_mode, toggle = False)
        
        if not sel_status:
            context.object.select_set(False)
            
        return {'FINISHED'}


classes = (
    ARMORED_OT_autosmooth,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)