# ARMORED TOOLKIT CHANGELOG


## v0.1.3 (LATEST)
*(unreleased)*

**FEATURES**
- Keymap Override: Transform with Gizmos.
- New Tool: *Set Custom Orientation* creates a temporaty orientation based on your selection, running the script
  from an empty area of the viewport goes back to Global pivot orientation.
- Transform Toggle Tool now goes back to the previous tool instead of defaulting to Box Select.
- Transform Toggle Tool (now Toggle Tool) now toggles any tool with the input *idname*.

**DEV**
- Swapped out the keymap functions for classes, simplifying the module's register/unregister methods among other things.

## v0.1.2
*(06/Jul/21)*
- BUGFIX: Addon was deleting default blender matcaps LMAO, but only in certain custom builds.


## v0.1.1
*(04/Jul/21)*
- BUGFIX: Resource paths were NOT being created when needed, preventing the addon from being enabled.


## v0.1.0
*(03/Jul/21)*
- FIRST PUBLIC RELEASE.