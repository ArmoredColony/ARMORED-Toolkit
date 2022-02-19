import bpy
from bpy.props import FloatProperty

from pprint import pprint


class NODE_OT_armored_node_stats(bpy.types.Operator):
	'''Get node stats (name, label, type, inputs, outputs, etc).

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
			'name  ': node.name,
			'label ': node.label,
			'type  ': node.type,
			'bl_idname': node.bl_idname,
			'parent': node.parent.name if node.parent else None,
			'node_tree': node.node_tree.name if hasattr(node, 'node_tree') else None,
			'location': node.location,
			# 'inputs': node.inputs[:],
			# 'outputs': node.outputs[:],
			'inputs' : [(i, val.name) for i, val in enumerate(node.inputs)],
			'outputs': [(i, val.name) for i, val in enumerate(node.outputs)],
		}

		print('\nNODE STATS:')
		pprint(stats, indent=3, sort_dicts=False)

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
