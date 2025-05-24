version = (2, 1, 0)

import bpy


class NODE_OT_armored_node_info(bpy.types.Operator):
	'''Get node info (name, label, type, inputs, outputs, etc).

	armoredColony.com '''

	bl_idname = 'node.armored_node_info'
	bl_label = 'ARMORED Node Info'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.area.type == 'NODE_EDITOR' and context.active_node is not None
	
	def execute(self, context):
		node = context.active_node

		if node is None:
			self.report({'WARNING'}, 'Active Node is None')
			return {'CANCELLED'}
		
		info = {
			'name (uniq)':	node.name,
			'label':	node.label,
			'type':		node.type,
			'bl_idname':	node.bl_idname,
			'parent':	node.parent.name if node.parent else None,
			'node_tree':	node.id_data.name,
			'location':	node.location,
		}

		# Find the longest key for proper alignment
		max_key_len = max(len(key) for key in (*info, 'inputs', 'outputs'))

		separator = '='
		tab_width = 8
		tab = ' ' * tab_width

		print('\nNODE INFO:')

		for key, value in info.items():
			space_for_non_string = ' ' if not isinstance(value, str) else ''
			print(f'{tab}{key:<{max_key_len}} {separator} {space_for_non_string}{repr(value)}')

		if node.inputs:
			print(f'\tinputs:')
			for i, val in enumerate(node.inputs):
				print(f'{tab}{tab}{i:<{max_key_len - tab_width}} {separator} {repr(val.name)}')

		if node.outputs:
			print(f'\toutputs:')
			for i, val in enumerate(node.outputs):
				print(f'{tab}{tab}{i:<{max_key_len - tab_width}} {separator} {repr(val.name)}')
		
		print()

		return {'FINISHED'}

	
	
classes = (
    NODE_OT_armored_node_info,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
