import bpy


class OBJECT_OT_armored_fast_material(bpy.types.Operator):
	'''Assign materials to all selected objects.

	armoredColony.com '''

	bl_idname = 'object.armored_fast_material'
	bl_label = 'ARMORED Fast Material'
	bl_options = {'REGISTER', 'UNDO'}

	# @classmethod
	# def poll(cls, context):
	# 	return context.active_object is not None

	def execute(self, context):
		self.active_object = context.active_object
		self.selected_objects = context.selected_objects

		active_material = self.active_object.data.materials[0]

		for obj in self.selected_objects:
			data = obj.data
			materials = data.materials

			if not data.materials:
				materials.append(None)
			
			materials[0] = active_material
			


		return {'FINISHED'}
	


classes = (
	OBJECT_OT_armored_fast_material,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)