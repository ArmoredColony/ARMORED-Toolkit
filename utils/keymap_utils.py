from . import(
    addon,
    debug,
)


class KeymapGroup():
    '''Keymaps that override or supersede default Blender Keymaps'''

    # keymap_list = []
    def __init__(self, name):
        self.name = name
        self.keymap_list = []
    
    # @classmethod
    def add(self, km, idname, type, value, ctrl=False, alt=False, shift=False):
        # type = key, value = event
        kmi = km.keymap_items.new(idname, type, value, ctrl=ctrl, alt=alt, shift=shift)
        self.keymap_list.append((km, kmi))
        debug.msg(f'    {idname}{" CTRL" if ctrl else ""}{" ALT" if alt else ""}{" SHIFT" if shift else ""} {type} {value}')
        return kmi
    
    def register():
        raise NotImplementedError
    
    # @classmethod
    def unregister(self):
        if not self.keymap_list:
            debug.msg(self._formatted_name, '[Nothing to Unregister]', space=22)
            return

        for km, kmi in self.keymap_list:
            try:
                debug.msg(f'    {kmi.idname}{" CTRL" if kmi.ctrl else ""}{" ALT" if kmi.alt else ""}{" SHIFT" if kmi.shift else ""} {kmi.type} {kmi.value}')
                km.keymap_items.remove(kmi)
            except RuntimeError as e:
                debug.msg(e, 'Probably an F2 Addon Exception')
        
        self.keymap_list.clear()
        debug.msg(f'Disabled {self._formatted_name}')

    # @classmethod
    def enabled_message(self):
        debug.msg(f'Enabled {self._formatted_name}')

    # @classmethod
    @property
    def _formatted_name(self):
        return self.name.replace("_", " ").title()
        # return __class__.__name__.replace("_", " ").title()

    # @classmethod
    def kmi_props(self, kmi_props, attr, value):
        try:
            setattr(kmi_props, attr, value)
            
        except AttributeError:
            print(f'Warning: property {attr} not found in keymap item {kmi_props.__class__.__name__}')

        except Exception as e:
            print(f'Warning: {e}')