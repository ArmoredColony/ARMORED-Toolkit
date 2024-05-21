version = (1, 0, 0)

import bpy


class ARMORED_OT_get_curve_length(bpy.types.Operator):
	'''Prints the length of the Active Curve Object

	armoredColony.com '''

	bl_idname = 'object.armored_get_curve_length'
	bl_label  = 'ARMORED Get Curve Length'
	bl_options = {'REGISTER', 'UNDO'}

	curve_len: bpy.props.FloatProperty(
		name='Curve Length', subtype='DISTANCE', unit='LENGTH')

	round_number: bpy.props.IntProperty(
		name='Round Decimals', default=4, min=0)

	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True

		scene_unit = context.scene.unit_settings.length_unit
		layout.label(text=f'Curve Length: {round(self.curve_len, self.round_number)} {scene_unit.lower().title()}')
		layout.prop(self, 'round_number')

		# layout.prop(self, 'curve_len').active(False)


	def execute(self, context):
		ob = context.active_object
		
		if ob.type != 'CURVE':
			self.report({'WARNING'}, 'This is not a Curve Object')
			return {'FINISHED'}

		self.curve_len = ob.data.splines[0].calc_length()

		# self.report({'INFO'}, f'Curve Length: {self.curve_len}')
		print('Curve Length: ', self.curve_len)

		return {'FINISHED'}


classes = (
	ARMORED_OT_get_curve_length,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
    

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)