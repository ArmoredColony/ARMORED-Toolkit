version = (1, 0, 0)

import bpy


def get_modifier_types(self, context) -> list[tuple[str, str, str]]:
	modifier_types = sorted([modifier.identifier for modifier in bpy.types.Modifier.bl_rna.properties['type'].enum_items])
	# print(modifier_types.index('SUBSURF'))

	return list(map(lambda mod: (mod, mod.replace('_', ' ').title(), f'Remove all {mod} modifiers from the selected objects'), modifier_types))


class OBJECT_OT_armored_remove_modifiers(bpy.types.Operator):
	'''Remove specific Modifiers from the selected objects.

	armoredColony.com '''

	bl_idname = 'object.armored_remove_modifiers'
	bl_label = 'ARMORED Remove Modifiers'
	bl_options = {'REGISTER', 'UNDO'}

	filter: bpy.props.EnumProperty(
		name='Remove by',
		default='TYPE',
		items=[
			('TYPE', 'Type', 'Remove all modifiers of the selected type.'),
			('NAME', 'Name', 'Remove all modifiers with the selected name.'),
			('ALL',  'All',  'Remove all modifiers.'),
			],
		)

	modifier_type: bpy.props.EnumProperty(
		name='Modifier Type',
		items=get_modifier_types,
		default=41,	# Default values for an Enum that gets items from a function must be an integer.
		)

	modifier_name: bpy.props.StringProperty(
		name='Modifier Name',
		default='Subdivision',
		)
	
	def draw(self, context):
		layout = self.layout
		layout.use_property_split = True
		
		col = layout.column(align=True)

		row = col.row(align=True)
		row.prop(self, 'filter', expand=True)
		col.separator()

		if self.filter == 'TYPE':
			col.prop(self, 'modifier_type')
		elif self.filter == 'NAME':
			col.prop(self, 'modifier_name')
		
		col.separator()


	def invoke(self, context, event):
		if not context.selected_objects:
			self.report({'WARNING'}, 'No objects selected!')
			return {'CANCELLED'}
		
		self.removed_modifier_count = 0
		
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		for obj in context.selected_objects:

			if self.filter == 'TYPE':
				modifiers_to_remove = self._get_modifiers_by_type(obj, self.modifier_type)

			elif self.filter == 'NAME':
				modifiers_to_remove = self._get_modifiers_by_name(obj, self.modifier_name)

			elif self.filter == 'ALL':
				modifiers_to_remove = self._get_all_modifiers(obj)
			
			self._remove_modifiers(obj, modifiers_to_remove)
		
		if self.removed_modifier_count:
			self.report({'INFO'}, f'Removed {self.removed_modifier_count} modifiers.')
		else:
			self.report({'WARNING'}, 'No modifiers were removed.')

		return {'FINISHED'}
	

	# PRIVATE METHODS

	def _get_modifiers_by_type(self, obj: bpy.types.Object, mod_type: str) -> list[bpy.types.Modifier]:
		return [mod for mod in obj.modifiers if mod.type == mod_type]
	
	def _get_modifiers_by_name(self, obj: bpy.types.Object, mod_name: str) -> list[bpy.types.Modifier]:
		return [mod for mod in obj.modifiers if mod.name == mod_name]
	
	def _get_all_modifiers(self, obj: bpy.types.Object) -> list[bpy.types.Modifier]:
		return list(obj.modifiers)
	
	def _remove_modifiers(self, obj: bpy.types.Object, modifiers_to_remove: list[bpy.types.Modifier]) -> None:
		for mod in modifiers_to_remove:
			print(f'Removing Modifier \'{mod.name}\' from \'{obj.name}\'')
			obj.modifiers.remove(mod)
			self.removed_modifier_count += 1

classes = (
	OBJECT_OT_armored_remove_modifiers,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)