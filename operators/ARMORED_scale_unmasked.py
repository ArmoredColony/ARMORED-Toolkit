# v1.0

import bpy


class SCULPT_OT_armored_scale_unmasked(bpy.types.Macro):
	'''Sets pivot to unmasked and activates the default modal resize operator.

	armoredColony.com '''
	
	bl_idname = 'sculpt.armored_scale_unmasked'
	bl_label = 'ARMORED Scale Unmasked'
	bl_options = {'REGISTER','UNDO'}

classes = (
	SCULPT_OT_armored_scale_unmasked,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)
	SCULPT_OT_armored_scale_unmasked.define('SCULPT_OT_set_pivot_position')
	SCULPT_OT_armored_scale_unmasked.define('TRANSFORM_OT_resize')


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)