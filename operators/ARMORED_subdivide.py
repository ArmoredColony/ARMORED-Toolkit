version = (1, 3, 0)

import bpy


class ARMORED_OT_subdivide(bpy.types.Operator):
	'''Destructively subdivides the selected object (no modifiers). If a SubD modifier already exists it will subdivide and then subtract 1 level from the modifier to maintain the polycount).

 armoredColony.com '''
	
	bl_idname = 'view3d.armored_subdivide'
	bl_label = 'ARMORED Subdivide'
	bl_options = {'REGISTER', 'UNDO'}

	subdivision_type: bpy.props.EnumProperty(
		name='Type', default='CATMULL_CLARK',
		items=[ ('CATMULL_CLARK', 'Catmull-Clark', 'Smooth Catmul Clark Subdivision'),
			('SIMPLE',        'Flat',   'Flat Subdivision') ])

	limit_surface: bpy.props.BoolProperty(
		name='Limit Surface', default=False)

	def draw(self, context):
		layout = self.layout
		col = layout.column(align=True)

		col.row().prop(self, 'subdivision_type', expand=True)
		col.separator()
		col.prop(self, 'limit_surface')
	
	# @classmethod
	# def poll(cls, context):
	# 	return context.object is not None

	def execute(self, context):
		mode = context.mode
		
		active_object = context.active_object
		selected_objects = [obj for obj in context.selected_objects if obj.type == 'MESH']

		if active_object not in selected_objects:
			selected_objects.append(active_object)

		if mode == 'SCULPT':
			mod = next((mod for mod in reversed(active_object.modifiers) if mod.type == 'MULTIRES' and mod.show_viewport), None)

			if mod is None:
				mod = active_object.modifiers.new(name='Multires', type='MULTIRES')

			bpy.ops.object.multires_subdivide(modifier='Multires', mode='CATMULL_CLARK')

			return {'FINISHED'}

		if mode == 'EDIT_MESH':
			bpy.ops.object.mode_set(mode='OBJECT')

		for obj in selected_objects:
			mod = next((mod for mod in reversed(obj.modifiers) if mod.type == 'SUBSURF' and mod.show_viewport), None)
			
			if mod is not None:
				mod.levels -= 1
			
			mod = obj.modifiers.new(name='temp_subd', type='SUBSURF')

			mod.subdivision_type = self.subdivision_type
			mod.boundary_smooth = 'PRESERVE_CORNERS'
			mod.use_limit_surface = self.limit_surface

			context.view_layer.objects.active = obj
			bpy.ops.object.modifier_apply(modifier=mod.name)

		context.view_layer.objects.active = active_object

		if mode == 'EDIT_MESH':
			bpy.ops.object.mode_set(mode='EDIT')

		return {'FINISHED'}




classes = (
	ARMORED_OT_subdivide,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)    


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
