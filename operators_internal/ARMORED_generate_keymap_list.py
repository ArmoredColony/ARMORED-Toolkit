# v1.0

import bpy
from pprint import pprint

from .. customize import keymaps


class ARMORED_OT_generate_keymap_list(bpy.types.Operator):
	'''Display the keymaps this button will enable'''

	bl_idname  = 'armored.generate_keymap_list'
	bl_label   = 'ARMORED Generate Keymap List'
	bl_options = {'REGISTER', 'INTERNAL'}

	category : bpy.props.StringProperty(default='www.armoredColony.com')

	def execute(self, context):
		keymap_groups = keymaps.keymap_groups
		test = keymap_groups['zbrush_sculpting']
		keymap_list = test.keymap_list

		# for _km, kmi in keymap_list:
			# print(kmi.idname, kmi.type, kmi.value)
		idnames = [kmi.idname for km, kmi in keymap_list]
		pprint(idnames, indent=3, sort_dicts=False)
		return {'FINISHED'}


classes = (
	ARMORED_OT_generate_keymap_list,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)    


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
