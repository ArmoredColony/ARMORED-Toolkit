version = (1, 0, 0)

import bpy
import math
# import bmesh


class ARMORED_OT_autosmooth(bpy.types.Operator):
	'''Applies a 'Smooth by Angle' Modifier to the selected objects
	
	armoredColony.com '''
	
	bl_idname = 'view3d.armored_autosmooth'
	bl_label = 'ARMORED Autosmooth'
	bl_options = {'REGISTER', 'UNDO'}

	angle: bpy.props.FloatProperty(
		name='Angle', default=math.radians(30), min=0, max=math.radians(180), unit='ROTATION', 
		description='The angle in degrees that will be used to determine the smoothing of the mesh.')
	
	@classmethod
	def poll(cls, context):
		return bpy.app.version >= (4, 1, 0)
	
	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		layout.prop(self, 'angle')
		layout.separator()
		layout.operator('wm.operator_defaults', text='Reset')

	
	def execute(self, context):
		active_object = context.active_object

		selected_objects = [ob for ob in context.selected_objects if ob.type == 'MESH']
		self._add_smooth_by_angle_modifier(context, selected_objects)
		bpy.ops.object.shade_smooth()
		
		context.view_layer.objects.active = active_object

		return {'FINISHED'}

	def _add_smooth_by_angle_modifier(self, context, objects: list[bpy.types.Object]):

		for obj in objects:
			mod = obj.modifiers.get('Smooth by Angle')

			if mod is None or mod.type != 'NODES':
				context.view_layer.objects.active = obj
				bpy.ops.object.modifier_add_node_group(
					asset_library_type='ESSENTIALS', 
					asset_library_identifier="", 
					relative_asset_identifier="geometry_nodes\\smooth_by_angle.blend\\NodeTree\\Smooth by Angle"
				)

			mod = obj.modifiers.get('Smooth by Angle')
			# mod.node_group.nodes['Group Input.001'].outputs['Angle'].default_value = 40
			mod['Input_1'] = self.angle


classes = (
	ARMORED_OT_autosmooth,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)