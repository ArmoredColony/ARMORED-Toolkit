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
        self.error_count = 0
    
    # type = key, value = event
    def add(self, km, idname, type, value, ctrl=False, alt=False, shift=False):
        kmi = km.keymap_items.new(idname, type, value, ctrl=ctrl, alt=alt, shift=shift)
        self.keymap_list.append((km, kmi))
        debug.msg(f'    {idname}{" CTRL" if ctrl else ""}{" ALT" if alt else ""}{" SHIFT" if shift else ""} {type} {value}')
        return kmi
    
    @abstractmethod
    def register():
        pass
        # raise NotImplementedError
    
    def unregister(self):
        if not self.keymap_list:
            debug.msg(self._formatted_name, '[Nothing to Unregister]', space=22)
            return

        self.error_count = 0
        for km, kmi in self.keymap_list:
            try:
                debug.msg(f'    {kmi.idname}{" CTRL" if kmi.ctrl else ""}{" ALT" if kmi.alt else ""}{" SHIFT" if kmi.shift else ""} {kmi.type} {kmi.value}')
                km.keymap_items.remove(kmi)
            except Exception as e:
                self.error_count += 1
                debug.msg(e, 'Probably an F2 Addon Exception')
        
        self.keymap_list.clear()
        self.error_count = 0
        debug.msg(f'Disabled {self._formatted_name} {self._error_msg()}')

    def enabled_message(self):
        debug.msg(f'Enabled {self._formatted_name} {self._error_msg()}')

    def _error_msg(self):
        return '' if not self.error_count else f'with {self.error_count} errors.'

    @property
    def _formatted_name(self):
        return self.name.replace("_", " ").title()

    def kmi_props(self, kmi_props, attr, value):
        try:
            setattr(kmi_props, attr, value)
        except Exception as e:
            self.error_count += 1
            print(f'    ARMORED-Toolkit WARNING: {e}, check for typos?')