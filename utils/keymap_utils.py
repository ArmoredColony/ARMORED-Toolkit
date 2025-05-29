import abc
import bpy

from . import(
	debug,
)


def create_kmi(km, idname, type, value, ctrl=False, alt=False, shift=False, active=True):
	'''
	Add a kmi the traditional way.

	 Returns:
		kmi: The newly created keymap item.
	'''
	
	kmi = km.keymap_items.new(idname, type, value, ctrl=ctrl, alt=alt, shift=shift)
	kmi.active = active

	return kmi


def disable_kmi(km, idname, type=None, value=None, ctrl=None, alt=None, shift=None):
	'''
	Disables a keymap item by setting its 'active' property to False.

	Returns:
		bool: `True` if at least one KMI was found and disabled, `False` otherwise.
	'''

	kmi = get_kmi(km, idname, type, value, ctrl, alt, shift)

	if kmi is None:
		print(f'ARMORED-Toolkit WARNING: Keymap item [{idname}] not found.')
		return False
	
	kmi.active = False

	return True



def get_kmi(km, idname, type=None, value=None, ctrl=None, alt=None, shift=None):
	'''
	Get a keymap item from the user keyconfig.
	Returns the first match found based on specified criteria.
	Any argument set to None will be ignored in the comparison.
	'''

	for kmi in km.keymap_items:
		if kmi.idname != idname:
			continue

		if type is not None and kmi.type != type:
			continue

		if value is not None and kmi.value != value:
			continue

		if ctrl is not None and kmi.ctrl != ctrl:
			continue

		if alt is not None and kmi.alt != alt:
			continue

		if shift is not None and kmi.shift != shift:
			continue

		return kmi

	return None

	

class KeymapGroup(abc.ABC):
	'''Keymaps that override or supersede default Blender Keymaps'''

	def __init__(self):
		self.keymap_list = []
		self.km = None
		self.kmi = None
		self.error_count = 0
	
	# type=key, value=event
	def add(self, idname, type, value, ctrl=False, alt=False, shift=False):
		self.kmi = self.km.keymap_items.new(idname, type, value, ctrl=ctrl, alt=alt, shift=shift)
		self.keymap_list.append((self.km, self.kmi))

		return self.kmi

	def prop(self, attr: str, val):
		'''
		Set the property for the last added keymap item (self.kmi).
		The complexity allows for operators that use other operators as properties (macros?).

		Example:
			self.add('mesh.loopcut_slide')
			self.prop('TRANSFORM_OT_edge_slide.release_confirm', True)
		'''
		
		try:
			split_attr = attr.split('.')

			if len(split_attr) > 1:
				last_attr = split_attr.pop()
				join_attr = '.'.join(split_attr)
				setattr(eval(f'self.kmi.properties.{join_attr}'), last_attr, val)

			else:
				setattr(self.kmi.properties, attr, val)

		except Exception as e:
			self.error_count += 1
			print(f'ARMORED-Toolkit WARNING: {e}')

	@abc.abstractmethod
	def register():
		'''
		Register they keymap items (kmi).
		'''
		
		pass
	
	def unregister(self):
		if not self.keymap_list:
			debug.msg(self.formatted_class_name, '[Nothing to Unregister]', spaces=22)
			return

		self.status_message('DISABLED')
		self._unregister_keymaps()
		self.keymap_list.clear()

	def _unregister_keymaps(self):
		self.error_count = 0
		for km, kmi in self.keymap_list:
			try:
				km.keymap_items.remove(kmi)
			except Exception as e:
				self.error_count += 1
				debug.msg(e, 'Probably an F2 Addon Exception')

	def status_message(self, action:str):
		'''
		Prints aligned columns of [Modifiers] [Type] [Value] - [ID Name] for each keymap item,
		and how many errors occurred during the process.
		'''
		
		# Title + Error Count
		debug.msg(f'\n{action} [{self.formatted_class_name}]{self._error_msg()}:')

		# The modifiers are treated as a single column;
		# so we concatenate them tor the max_length calculation.
		concatenated_modifiers = []
		for _km, kmi in self.keymap_list:
			parts = []
			if kmi.ctrl:
				parts.append('CTRL')
			if kmi.alt:
				parts.append('ALT')
			if kmi.shift:
				parts.append('SHIFT')

			concatenated_modifiers.append(' '.join(parts))

		# Find the max lengths for each column.
		max_mod_len   = max((len(mods)     for mods in concatenated_modifiers), default=0)
		max_type_len  = max(len(kmi.type)  for _km, kmi in self.keymap_list)
		max_value_len = max(len(kmi.value) for _km, kmi in self.keymap_list)

		for (_km, kmi), mod_str in zip(self.keymap_list, concatenated_modifiers):
			debug.msg(f'    {mod_str.ljust(max_mod_len)} '
					f'{kmi.type.ljust(max_type_len)} '
					f'{kmi.value.ljust(max_value_len)} '
					f'- {kmi.idname}')
		
		debug.msg()

	def _error_msg(self):
		return '' if not self.error_count else f' with {self.error_count} errors'

	@property
	def formatted_class_name(self):
		return self.__class__.__name__.replace('_', ' ').title()

