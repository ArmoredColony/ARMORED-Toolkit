# v1.4

import bpy
from bpy.props import EnumProperty


class ARMORED_OT_subd_view_in_edit(bpy.types.Operator):
	'''Control how SubD modifiers are displayed in edit mode for the selected objects'.

www.armoredColony.com '''
	
	bl_idname = 'mesh.armored_subd_view_in_edit'
	bl_label = 'ARMORED SubD View in Edit'
	bl_options = {'REGISTER'}

	mode: EnumProperty(
		name='Mode',
		description='Control how SubD modifiers are displayed in edit mode for the selected objects',
		default='FULL', 
		items=[ ('OFF',    'Off',               'No Subdivision'               ), 
			('HYBRID', 'SubD with Cage',    'Subdivision with visible Cage'),
			('FULL',   'SubD without Cage', 'Subdivision without the Cage' ),
			])


	@classmethod
	def poll(cls, context):
		return context.mode == 'EDIT_MESH'

	def execute(self, context):

		for ob in context.objects_in_mode:

			mods = self._get_subd_modifiers(ob)
			
			if not mods:
				mods = [ob.modifiers.new(name='Subdivision', type='SUBSURF')]

			for mod in mods:    

				if self.mode == 'OFF':

					mod.show_on_cage = False
					mod.show_in_editmode = False

				elif self.mode == 'HYBRID':

					mod.show_on_cage = False
					mod.show_in_editmode = True
					if mod.levels == 0:
						mod.levels = 1

				elif self.mode == 'FULL':

					mod.show_on_cage = True
					mod.show_in_editmode = True
					if mod.levels == 0:
						mod.levels = 1

		return {'FINISHED'}

	def _get_subd_modifiers(self, ob: bpy.types.Object) -> list[bpy.types.Modifier]:
		return [mod for mod in ob.modifiers if mod.type == 'SUBSURF']


class ARMORED_MT_subd_view_in_edit(bpy.types.Menu):
	bl_label = 'SubD View in Edit'
	bl_idname = 'ARMORED_MT_subd_view_in_edit'

	def draw(self, context):
		layout = self.layout
		layout.operator('mesh.armored_subd_view_in_edit', text='ARMORED SubD Off')      .mode = 'OFF'
		layout.operator('mesh.armored_subd_view_in_edit', text='ARMORED SubD with Cage').mode = 'HYBRID'
		layout.operator('mesh.armored_subd_view_in_edit', text='ARMORED SubD Only')     .mode = 'FULL'


def menu_func(self, context):
	self.layout.separator()
	self.layout.menu(ARMORED_MT_subd_view_in_edit.bl_idname)


classes = (
	ARMORED_OT_subd_view_in_edit,
	ARMORED_MT_subd_view_in_edit,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	bpy.types.VIEW3D_MT_edit_mesh.append(menu_func)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)
	bpy.types.VIEW3D_MT_edit_mesh.remove(menu_func)
