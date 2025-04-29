import bpy.utils.previews
import os

from . import paths


def load_icons(preview_collections):
	pcoll = bpy.utils.previews.new()

	icon_path  = paths.AddonPaths.icons

	icon_names = [	# Without the PNG extension.
		'armored_colony32',
		'artstation32',
		'blender_market32',
		'github32',
		'gumroad32',
		'youtube32',
	]

	for icon_name in icon_names:
		pcoll.load(icon_name, os.path.join(icon_path, f'{icon_name}.png'), 'IMAGE')

	preview_collections['web_icons'] = pcoll

	return preview_collections


def unload_icons(preview_collections):
	for pcoll in preview_collections.values():
		bpy.utils.previews.remove(pcoll)
		
	preview_collections.clear()