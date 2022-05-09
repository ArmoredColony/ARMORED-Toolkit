import bpy
from bpy.props import BoolProperty


def wireframe_selected(context):
	for ob in context.selected_objects:
		ob.show_wire = True


def remove_all_wireframes():
	for ob in bpy.data.objects:
		ob.show_wire = False


class ARMORED_OT_wireframe_selected(bpy.types.Operator):
	'''Enables wireframes on selected objects and viceversa.

armoredColony.com '''

	bl_idname = 'armored.wireframe_selected'
	bl_label = 'ARMORED Wireframe Selected'
	bl_options = {'REGISTER'}

	def invoke(self, context, event):
		remove_all_wireframes()
		wireframe_selected(context)
		return {'FINISHED'}


# ================================================================================
# HIJACK MACROS 
# Run the original operators and then our `wireframe selected` operator afterwards.


class VIEW3D_OT_armored_select_click(bpy.types.Macro):
    bl_idname = 'view3d.armored_select_click'
    bl_label = 'ARMORED Select Click'
    bl_options = {'REGISTER', 'UNDO'}


class VIEW3D_OT_armored_select_box(bpy.types.Macro):
    bl_idname = 'view3d.armored_select_box'
    bl_label = 'ARMORED Select Box'
    bl_options = {'REGISTER', 'UNDO'}


class OBJECT_OT_armored_select_all(bpy.types.Macro):
    bl_idname = 'object.armored_select_all'
    bl_label = 'ARMORED Select All'
    bl_options = {'REGISTER', 'UNDO'}


classes = (
	ARMORED_OT_wireframe_selected,
	VIEW3D_OT_armored_select_click,
	VIEW3D_OT_armored_select_box,
	OBJECT_OT_armored_select_all,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)

	VIEW3D_OT_armored_select_click.define('VIEW3D_OT_select')
	VIEW3D_OT_armored_select_click.define('ARMORED_OT_wireframe_selected')

	VIEW3D_OT_armored_select_box.define('VIEW3D_OT_select_box')
	VIEW3D_OT_armored_select_box.define('ARMORED_OT_wireframe_selected')

	OBJECT_OT_armored_select_all.define('OBJECT_OT_select_all')
	OBJECT_OT_armored_select_all.define('ARMORED_OT_wireframe_selected')


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)