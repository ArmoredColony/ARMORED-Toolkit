# v1.3

import bpy


class WM_OT_armored_open_most_recent(bpy.types.Operator):
	'''Opens the most recent blend file.

(www.armoredColony.com)'''

	bl_idname = 'wm.armored_open_most_recent'
	bl_label = 'ARMORED Open most recent'
	bl_options = {'REGISTER'}

	def execute(self, context):
		recent_files_path = bpy.utils.user_resource('CONFIG', path='recent-files.txt')
		recent_files = []

		try:
			with open(recent_files_path) as file:
				recent_files = file.read().splitlines()
		except OSError:
			return {'FINISHED'}

		if not recent_files:
			self.report({'ERROR'}, 'Open Most Recent: \nNo recent files available')
			return {'FINISHED'}

		try:
			bpy.ops.wm.open_mainfile('INVOKE_DEFAULT', filepath=recent_files[0], display_file_selector=False)
		except RuntimeError as e:
			self.report({'ERROR'}, f'{e}')

		return {'FINISHED'}


classes = (
	WM_OT_armored_open_most_recent,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)