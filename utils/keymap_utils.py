from abc import ABC, abstractmethod

from . import(
    addon,
    debug,
)


class KeymapGroup(ABC):
    '''Keymaps that override or supersede default Blender Keymaps'''

    def __init__(self, name):
        self.name = name
        self.keymap_list = []
        self.km = None
        self.kmi = None
        self.error_count = 0
    
    # type=key, value=event
    def add(self, idname, type, value, ctrl=False, alt=False, shift=False):
        self.kmi = self.km.keymap_items.new(idname, type, value, ctrl=ctrl, alt=alt, shift=shift)
        self.keymap_list.append((self.km, self.kmi))
        debug.msg(f'    {idname}{" CTRL" if ctrl else ""}{" ALT" if alt else ""}{" SHIFT" if shift else ""} {type} {value}')
    
    def prop(self, attr, val):
        try:
            setattr(self.kmi.properties, attr, val)
        except Exception as e:
            self.error_count += 1
            print(f'    ARMORED-Toolkit WARNING: {e}, check for typos?')

    @abstractmethod
    def register():
        pass
    
    def unregister(self):
        if self._empty_keymap_list(): 
            return

        self._unregister_keymaps()
        self.keymap_list.clear()
        self.disabled_message()

    def _unregister_keymaps(self):
        self.error_count = 0
        for km, kmi in self.keymap_list:
            try:
                debug.msg(f'    {kmi.idname}{" CTRL" if kmi.ctrl else ""}{" ALT" if kmi.alt else ""}{" SHIFT" if kmi.shift else ""} {kmi.type} {kmi.value}')
                km.keymap_items.remove(kmi)
            except Exception as e:
                self.error_count += 1
                debug.msg(e, 'Probably an F2 Addon Exception')

    def _empty_keymap_list(self):
        if not self.keymap_list:
            debug.msg(self._formatted_name, '[Nothing to Unregister]', space=22)
            return True

    def enabled_message(self):
        debug.msg(f'Enabled {self._formatted_name} {self._error_msg()}')
    
    def disabled_message(self):
        debug.msg(f'Disabled {self._formatted_name} {self._error_msg()}')

    def _error_msg(self):
        return '' if not self.error_count else f'with {self.error_count} errors.'

    @property
    def _formatted_name(self):
        return self.name.replace("_", " ").title()
