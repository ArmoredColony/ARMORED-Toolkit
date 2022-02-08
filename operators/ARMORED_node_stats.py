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
			'name' : node.name,
			'location' : node.location,
			'inputs' : node.inputs[:],
			'outputs' : node.outputs[:],
		}
			
		print()
		for key, val in stats.items():
			if isinstance(val, list):
				print(f'{key}:')
				if not val:
					print('None')
					continue

				for idx, e in enumerate(val):
					print(f'    [{idx}] {e.name}')
			else:
				print(f'{key}: {val}')

		self.report({'INFO'}, f'Node Location {stats.get("location")}')
		return {'FINISHED'}

classes = (
    NODE_OT_armored_node_stats,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
