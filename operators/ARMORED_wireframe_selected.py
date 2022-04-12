import bpy
from bpy.props import BoolProperty


def wireframe_selected(context):
	for ob in context.selected_objects:
		ob.show_wire = True


def remove_all_wireframes():
	for ob in bpy.data.objects:
		ob.show_wire = False


class VIEW3D_OT_armored_select(bpy.types.Operator):
	bl_idname = 'view3d.armored_select'
	bl_label = 'ARMORED Select'
	bl_options = {'REGISTER', 'UNDO'}
	
	extend   : BoolProperty(name='Extend',   default=False, options={'SKIP_SAVE'})
	deselect : BoolProperty(name='Deselect', default=False, options={'SKIP_SAVE'})
	toggle   : BoolProperty(name='Toggle',   default=False, options={'SKIP_SAVE'})

	def invoke(self, context, event):
		result = bpy.ops.view3d.select('INVOKE_DEFAULT', extend=self.extend, deselect=self.deselect, toggle=self.toggle)
		# print(result)

		if context.mode != 'OBJECT':
			return result

		if 'PASS_THROUGH' in result:
			if not any((event.ctrl, event.alt, event.shift)):
				bpy.ops.object.select_all(action='DESELECT')
				remove_all_wireframes()
			return {'PASS_THROUGH'}

		if 'FINISHED' in result:
			remove_all_wireframes()
			wireframe_selected(context)
			return {'FINISHED'}

		return result



class ARMORED_OT_wireframe_selected(bpy.types.Operator):
	bl_idname = 'armored.wireframe_selected'
	bl_label = 'ARMORED Wireframe Selected'
	bl_options = {'INTERNAL'}

	def invoke(self, context, event):
		remove_all_wireframes()
		wireframe_selected(context)
		return {'FINISHED'}


class VIEW3D_OT_armored_select_macro(bpy.types.Macro):
    bl_idname = 'view3d.armored_select_macro'
    bl_label = 'ARMORED Select Macro'
    bl_options = {'REGISTER', 'UNDO'}


class VIEW3D_OT_armored_select_box(bpy.types.Macro):
    bl_idname = 'view3d.armored_select_box'
    bl_label = 'ARMORED Select Box'
    bl_options = {'REGISTER', 'UNDO'}


classes = (
	VIEW3D_OT_armored_select,
	VIEW3D_OT_armored_select_macro,
	ARMORED_OT_wireframe_selected,
	VIEW3D_OT_armored_select_box,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	
	VIEW3D_OT_armored_select_macro.define('VIEW3D_OT_select')
	VIEW3D_OT_armored_select_macro.define('ARMORED_OT_wireframe_selected')

	VIEW3D_OT_armored_select_box.define('VIEW3D_OT_select_box')
	VIEW3D_OT_armored_select_box.define('ARMORED_OT_wireframe_selected')


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)