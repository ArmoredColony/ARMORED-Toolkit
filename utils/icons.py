import bpy.utils.previews
import os

from . import paths


def load_icons(preview_collections):
	pcoll = bpy.utils.previews.new()

	pcoll.load('artstation32',	os.path.join(paths.AddonPaths.icons, 'artstation32.png'),	'IMAGE')
	pcoll.load('blender_market32',	os.path.join(paths.AddonPaths.icons, 'blender_market32.png'),	'IMAGE')
	pcoll.load('github32',		os.path.join(paths.AddonPaths.icons, 'github32.png'),		'IMAGE')
	pcoll.load('youtube32',		os.path.join(paths.AddonPaths.icons, 'youtube32.png'),		'IMAGE')

	preview_collections['web_icons'] = pcoll

	return preview_collections

def unload_icons(preview_collections):
	for pcoll in preview_collections.values():
		bpy.utils.previews.remove(pcoll)
	preview_collections.clear()