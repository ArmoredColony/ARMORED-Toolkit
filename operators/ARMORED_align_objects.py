version = (1, 1, 0)

import bpy


def draw(self, context):
	layout = self.layout
	# scene = context.scene
	# render = scene.render

	col = layout.column(align=True)

	#layout.prop(render, "use_lock_interface")
	col.label(text='Align Objects')
	
	row = col.row(align=True)
	op = row.operator('object.align', text='X')
	op.align_axis = {'X'}
	op.relative_to = 'OPT_4'

	op = row.operator('object.align', text='Y')
	op.align_axis = {'Y'}
	op.relative_to = 'OPT_4'

	op = row.operator('object.align', text='Z')
	op.align_axis = {'Z'}
	op.relative_to = 'OPT_4'

	# col.separator()

	# col.label(text='Align to Cursor')
	# row = col.row(align=True)

	# op = row.operator('object.align', text='X')
	# op.align_axis = {'X'}
	# op.relative_to = 'OPT_2'

	# op = row.operator('object.align', text='Y')
	# op.align_axis = {'Y'}
	# op.relative_to = 'OPT_2'

	# op = row.operator('object.align', text='Z')
	# op.align_axis = {'Z'}
	# op.relative_to = 'OPT_2'


def register():
	bpy.types.VIEW3D_PT_snapping.append(draw)


def unregister():
	bpy.types.VIEW3D_PT_snapping.remove(draw)