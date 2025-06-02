version = (1, 3, 0)

import bpy
import bmesh
import math


def move_modifier_to_bottom(context, obj: bpy.types.Object, modifier_name: str) -> None:
	'''
	Move the modifier down the stack until it reaches the bottom.
	'''
	
	mod = obj.modifiers.get(modifier_name)

	for _ in range( len(obj.modifiers) ):
		if obj.modifiers[-1] == mod:
			break
		
		with context.temp_override(object=obj):
			bpy.ops.object.modifier_move_down(modifier=modifier_name)


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
		selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']

		if context.mode == 'OBJECT':
			self._shade_smooth(objects=selected_objects, value=True)
				
		elif context.mode in {'EDIT_MESH', 'EDIT_CURVE'}:
			self._shade_smooth_bmesh(objects=selected_objects, value=True)

		self._add_smooth_by_angle_modifier(context, objects=selected_objects)
			
		
		return {'FINISHED'}


	# PRIVATE METHODS __________________________________________________

	def _add_smooth_by_angle_modifier(self, context, objects: list[bpy.types.Object]):
		'''
		Apply the new Smooth by Angle Modifier for Blender 4.1 and later.
		'''

		active_object = context.active_object

		for obj in objects:
			mod = obj.modifiers.get('Smooth by Angle')

			if mod is None or mod.type != 'NODES':
				context.view_layer.objects.active = obj

				bpy.ops.object.modifier_add_node_group(
					asset_library_type='ESSENTIALS', 
					asset_library_identifier='', 
					relative_asset_identifier='geometry_nodes\\smooth_by_angle.blend\\NodeTree\\Smooth by Angle'
				)

			mod = obj.modifiers.get('Smooth by Angle')
			mod['Input_1'] = self.angle
			mod.use_pin_to_last = True

			move_modifier_to_bottom(context, obj, mod.name)
		
		context.view_layer.objects.active = active_object
	
	def _shade_smooth(self, objects: list[bpy.types.Object], value: bool) -> None:
		'''
		Alternative to `object.shade_smooth()` that works on the specified objects instead of the current selection.
		This is useful in case your selection includes non-mesh objects or if the active is not part of the selection.
		'''

		for obj in objects:
			mesh = obj.data
			values = [value] * len(mesh.polygons)
			mesh.polygons.foreach_set('use_smooth', values)
			mesh.update()

	def _shade_smooth_bmesh(self, objects: list[bpy.types.Object], value: bool) -> None:
		'''
		Smoothing for geometry that is still being edited.
		'''

		for obj in objects:
			mesh = obj.data
			bm = bmesh.from_edit_mesh(mesh)
			for f in bm.faces:
				f.smooth = value
		
		bmesh.update_edit_mesh(mesh)


classes = (
	ARMORED_OT_autosmooth,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)

def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)