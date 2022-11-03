# v1.0

import bpy
import bmesh
# import numpy as np


class MESH_OT_armored_mask_from_selected(bpy.types.Operator):
	'''Converts the selected vertices into a sculpt mask.

armoredColony.com '''

	bl_idname = 'mesh.armored_mask_from_selected'
	bl_label = 'ARMORED Mask from Selected'
	bl_options = {'REGISTER', 'UNDO'}

	@classmethod
	def poll(cls, context):
		return context.active_object is not None

	def execute(self, context):
		ob = context.active_object
		me = ob.data
		bm = bmesh.new()
		bm.from_mesh(me)

		sel_verts = [v for v in bm.verts if v.select]

		mask_layer = bm.verts.layers.paint_mask.verify()
		mask_value = 1.0

		# bm.verts.ensure_lookup_table()

		for v in sel_verts:
			v[mask_layer] = mask_value

		bm.to_mesh(me)
		bm.clear()
		me.update()

		return {'FINISHED'}



# class MESH_OT_armored_mask_from_selected_alt(bpy.types.Operator):
# 	'''Separates the masked faces into a new object.

# armoredColony.com '''

# 	bl_idname = 'sculpt.armored_extract_masked'
# 	bl_label = 'ARMORED Mask from Selected Alt'
# 	bl_options = {'REGISTER', 'UNDO'}

# 	@classmethod
# 	def poll(cls, context):
# 		return context.active_object is not None

# 	def execute(self, context):
# 		ob = context.active_object
# 		me = ob.data
# 		bm = bmesh.new()
# 		bm.from_mesh(me)

# 		#get selected verts
# 		v_sel = np.empty(len(me.vertices), dtype=bool)
# 		me.vertices.foreach_get('select', v_sel)
# 		sel_idx, = np.where(v_sel)

# 		#get custom data layer paint_mask
# 		mask_layer= bm.verts.layers.paint_mask.verify() #strange way, but that gets you custom data layer
# 		bm.verts.ensure_lookup_table()
# 		#set every selected vert to mask_value

# 		mask_value = 1.0
# 		for idx in sel_idx:
# 			bm.verts[idx][mask_layer] = mask_value

# 		bm.to_mesh(me)
		
# 		return {'FINISHED'}


classes = (
	MESH_OT_armored_mask_from_selected,
	# MESH_OT_armored_mask_from_selected_alt,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in classes:
		bpy.utils.unregister_class(cls)