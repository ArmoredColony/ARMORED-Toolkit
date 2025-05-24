version = (1, 2, 0)

import bpy


def traverse_tree(tree):
	yield tree
	for child in tree.children:
        	yield from traverse_tree(child)


def get_view_layer_collections(context):
	'''
	Returns a list of LayerCollections in the current view layer,
	excluding the root 'Scene Collection'.
	'''

	return [
		lc for lc in traverse_tree(context.view_layer.layer_collection)
		if lc.collection.name != 'Scene Collection'
	]


def get_all_scene_objects(context):
	'''
	Get all objects that are being used in the current scene.
	'''

	scene_objects = [
		ob for ob in bpy.data.objects if context.scene.user_of_id(ob)
	]

	return scene_objects


@bpy.app.handlers.persistent
def sync_render_to_viewport(*args):
	'''
	Check if the sync_render Scene property is enabled before
	syncing the render visibility to the viewport visibility.
	'''
	
	sync_render = bpy.context.scene.armored_sync_render

	if not sync_render:
		return

	print('ARMORED-Toolkit: Syncing Render to Viewport visibility')
	layer_collections = get_view_layer_collections(bpy.context)
	scene_objects     = get_all_scene_objects(bpy.context)

	for layer_coll in layer_collections:
		layer_coll.collection.hide_render = layer_coll.hide_viewport

	for obj in scene_objects:
		obj.hide_render = obj.hide_get()


def draw_sync_button(self, context):
	self.layout.prop(context.scene, 'armored_sync_render', icon='RESTRICT_RENDER_OFF', text='')


def register():
	bpy.types.Scene.armored_sync_render = bpy.props.BoolProperty(
		name='ARMORED Sync Render to Viewport', 
		default=False,
		description='When starting a render, automatically sync it to the Viewport object visibility',
	)
	bpy.app.handlers.render_pre.append(sync_render_to_viewport)
	bpy.types.OUTLINER_HT_header.append(draw_sync_button)

def unregister():
	bpy.app.handlers.render_pre.remove(sync_render_to_viewport)
	bpy.types.OUTLINER_HT_header.remove(draw_sync_button)