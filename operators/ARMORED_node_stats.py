# v1.4

import bpy
from bpy.props import FloatProperty


class NODE_OT_armored_node_stats(bpy.types.Operator):
	'''Get node stats (location, etc).

	armoredColony.com '''

	bl_idname = 'node.armored_node_stats'
	bl_label = 'ARMORED Node Stats'
	bl_options = {'REGISTER', 'UNDO'}
    
	@classmethod
	def poll(cls, context):
		return context.workspace.name in {'Geometry Nodes',}

	def execute(self, context):
		node = context.active_node
		
		stats = {
			'name ' : node.name,	# NOTE: I added an extra space in "name", just so it lines up with "label" when printed.
			'label' : node.label,
			'type' : node.type,
			'location' : node.location,
			'inputs' : node.inputs[:],
			'outputs' : node.outputs[:],
		}
			
		print()
		for key, val in stats.items():
			if type(val) is list:
				if self._empty_list(val):
					continue
				self._iterate_and_print(key, val)
			else:
				self._print(key, val)
				

		# self.report({'INFO'}, f'Location {node.location}')
		return {'FINISHED'}
	
	def _empty_list(self, lst: list):
		if not lst:
			print(    'None')
			return True

	def _iterate_and_print(self, key: str, val: list):
		print(f'{key}:')
		for idx, e in enumerate(val):
			print(f"    [{idx}] '{e.name}'")
	
	def _print(self, key, val):
		val = f"'{val}'" if type(val) is str else val
		print(f'{key}: {val}')


classes = (
    NODE_OT_armored_node_stats,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
