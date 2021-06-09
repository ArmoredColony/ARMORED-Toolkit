# v1.0

import bpy
from .. utils import addon
# from .. utils.addon import get_prefs, get_path, get_name


debug = False


def main(self, context):
    # if not bpy.ops.object.mode_set.poll or not bpy.ops.object.editmode_toggle.poll():
    # if not bpy.ops.object.mode_set.poll():
    #     print('ARMTK - Operator Poll Failed')
    #     self.report({'DEBUG'}, 'ARMORED Toolkit\n Sub-Operator Poll Failed')
    #     return {'FINISHED'}

    workspace = (context.window.workspace.name_full).upper()
    # bpy.ops.object.mode_set(toggle=True)



    if context.object.mode == 'SCULPT':
        # bpy.ops.object.mode_set(mode='OBJECT', toggle=True)
        bpy.ops.sculpt.sculptmode_toggle()  # Will toggle to Object Mode.
        if debug: print('Sculp mode detected, toggle to object? \n')
    
    elif context.object.type == 'GPENCIL':
        # bpy.ops.object.mode_set(mode='EDIT_GPENCIL', toggle=True)
        bpy.ops.gpencil.editmode_toggle()   # Will toggle between Object end Edit GPencil.
        if debug: print('GPencil object type detected, toggle between EDIT/OBJECT \n')
    
    elif workspace == 'SCULPTING':
        if debug: print('Sculpt Worspace detected')
        try:
            # bpy.ops.object.mode_set(mode='SCULPT', toggle=True)
            bpy.ops.sculpt.sculptmode_toggle()      # Will toggle between Object end Sculpt.
            if debug: print('Toggle to sculpt mode successful \n')

        except TypeError:
        # except RuntimeError:
            if debug: print('Runtime Error')
            if bpy.ops.object.editmode_toggle.poll():
                bpy.ops.object.editmode_toggle()        # Will toggle between Object end Edit.
                # bpy.ops.object.mode_set(mode='EDIT', toggle=True)
                if debug: print('Toggle to edit mode successful \n')
            else:
                if debug: print('Edit mode Poll Failed \n')

    else:
        if bpy.ops.object.editmode_toggle.poll():
            # bpy.ops.object.mode_set(mode='EDIT', toggle=True)
            bpy.ops.object.editmode_toggle()        # Will toggle between Object end Edit.
            if debug: print('Toggle to edit mode successful \n')
        else:
            if debug: print('Edit mode Poll Failed \n')



class ARMORED_OT_mode_toggle_grouped(bpy.types.Operator):
    bl_idname = 'armored.mode_toggle'
    bl_label = 'ARMORED Mode Toggle'
    bl_options = {'REGISTER', 'UNDO_GROUPED'}

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        main(self, context)
        return {'FINISHED'}


class ARMORED_OT_mode_toggle_normal(bpy.types.Operator):
    bl_idname = 'armored.mode_toggle'
    bl_label = 'ARMORED Mode Toggle'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        main(self, context)
        return {'FINISHED'}


class ARMORED_OT_mode_toggle_none(bpy.types.Operator):
    bl_idname = 'armored.mode_toggle'
    bl_label = 'ARMORED Mode Toggle'
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        main(self, context)
        return {'FINISHED'}



# classes = (
    # ARMORED_OT_mode_toggle,
    # ARMORED_OT_mode_toggle_wrapper,
    # ARMORED_OT_mode_toggle_standard,
    # ARMORED_OT_mode_toggle_grouped_undo,
    # ARMORED_OT_mode_toggle_no_undo,
# )

def register():
    # from .. utils.preferences import get_prefs, get_path, get_name

    undo_mode = addon.preferences().tab_undo_mode
    # print(f'TAB Undo History Mode: {undo_mode}')

    if undo_mode == 'GROUPED':
        bpy.utils.register_class(ARMORED_OT_mode_toggle_grouped)

    elif undo_mode == 'NORMAL':
        bpy.utils.register_class(ARMORED_OT_mode_toggle_normal)

    elif undo_mode == 'NONE':
        bpy.utils.register_class(ARMORED_OT_mode_toggle_none)

def unregister():

    try:
        bpy.utils.unregister_class(ARMORED_OT_mode_toggle_grouped)
    except RuntimeError: pass

    try:
        bpy.utils.unregister_class(ARMORED_OT_mode_toggle_normal)
    except RuntimeError: pass

    try:
        bpy.utils.unregister_class(ARMORED_OT_mode_toggle_none)
    except RuntimeError: pass
