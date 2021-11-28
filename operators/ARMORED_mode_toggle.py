# v1.1

import bpy
from .. utils import addon


debug = False

def main(self, context):
    # if bpy.ops.object.mode_set.poll():
    if bpy.ops.object.editmode_toggle.poll():
        bpy.ops.object.mode_set(mode='EDIT', toggle=True)

    # if bpy.ops.object.editmode_toggle.poll():
        # bpy.ops.object.editmode_toggle()

# def main(self, context):
#     workspace = (context.window.workspace.name_full).upper()

#     if context.object.mode == 'SCULPT':
#         bpy.ops.sculpt.sculptmode_toggle()  # Will toggle to Object Mode.
#         if debug: print('Sculp mode detected, toggle to object? \n')
    
#     elif context.object.type == 'GPENCIL':
#         bpy.ops.gpencil.editmode_toggle()   # Will toggle between Object end Edit GPencil.
#         if debug: print('GPencil object type detected, toggle between EDIT/OBJECT \n')
    
#     elif workspace == 'SCULPTING':
#         if debug: print('Sculpt Worspace detected')
#         try:
#             bpy.ops.sculpt.sculptmode_toggle()      # Will toggle between Object end Sculpt.
#             if debug: print('Toggle to sculpt mode successful \n')

#         except TypeError:
#         # except RuntimeError:
#             if debug: print('Runtime Error')
#             if bpy.ops.object.editmode_toggle.poll():
#                 bpy.ops.object.editmode_toggle()        # Will toggle between Object end Edit.
#                 if debug: print('Toggle to edit mode successful \n')
#             else:
#                 if debug: print('Edit mode Poll Failed \n')

#     else:
#         if bpy.ops.object.editmode_toggle.poll():
#             bpy.ops.object.editmode_toggle()        # Will toggle between Object end Edit.
#             if debug: print('Toggle to edit mode successful \n')
#         else:
#             if debug: print('Edit mode Poll Failed \n')



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



def register():
    undo_mode = addon.prefs().tab_undo_mode
    unregister_all()

    if undo_mode == 'GROUPED':
        bpy.utils.register_class(ARMORED_OT_mode_toggle_grouped)

    elif undo_mode == 'NORMAL':
        bpy.utils.register_class(ARMORED_OT_mode_toggle_normal)

    elif undo_mode == 'SKIP':
        bpy.utils.register_class(ARMORED_OT_mode_toggle_none)


def unregister():
    unregister_all()


def unregister_all():
    try:    bpy.utils.unregister_class(ARMORED_OT_mode_toggle_grouped)
    except  RuntimeError: pass

    try:    bpy.utils.unregister_class(ARMORED_OT_mode_toggle_normal)
    except  RuntimeError: pass

    try:    bpy.utils.unregister_class(ARMORED_OT_mode_toggle_none)
    except  RuntimeError: pass