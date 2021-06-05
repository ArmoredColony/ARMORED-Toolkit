# v1.1

import bpy


class ARMORED_OT_open_most_recent(bpy.types.Operator):
    '''Opens the most recent blend file.

(www.armoredColony.com)'''

    bl_idname = 'view3d.armored_open_most_recent'
    bl_label = 'ARMORED Open most recent file'
    bl_options = {'REGISTER'}

    def execute(self, context):
        recent_files_path = bpy.utils.user_resource('CONFIG', 'recent-files.txt')

        try:
            with open(recent_files_path) as file:
                recent_files = file.read().splitlines()

        except (IOError, OSError, FileNotFoundError):
            recent_files = []

        if recent_files:
            most_recent = recent_files[0]

            # load_ui ensures the the viewport location/angle is loaded as well
            bpy.ops.wm.open_mainfile(filepath=most_recent, load_ui=True)

        return {'FINISHED'}


classes = (
    ARMORED_OT_open_most_recent,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)