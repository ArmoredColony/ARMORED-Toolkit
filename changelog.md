# ARMORED TOOLKIT CHANGELOG


## v0.2.0 (LATEST)
*(29/Nov/21)*

### Added ###
- Operator *Delete and Grid Fill* combines Delete Faces and Fill Grid into a single operator. This new operator appears in the [X] (delete) panel automatically.
- *TAB History* is now exposed to users in the addon preferences
- HDRIS, Studio Lights, and Themes to the resources you can install along with MATCAPS.
- Keymap Override *Allow Gizmo Click*. Activate gizmos the instance you click on them instead of waiting for a [MOUSEDRAG] event.

### Changed ###
- *Maya Cube* primitive is now a modal and allows adding segments with [MOUSESCROLL].
- *Armored Focus* is now bound to the F key again when *Operator Keymaps* are enabled.
- *Armored Focus* operator was simplified and performance was increased.
- [ALT+E] now activates *Extrude along normals* when *Operator Keymaps* are enabled instead of displaying the extrude menu.
- Updated the *Armored Colony* theme preset to be more consistent (red UI highlights have black text whenever possible).
- Added, Polished and even Removed a poop ton of addon code.


## v0.1.3
*(16/Jul/21)*

### Added ###
- Keymap Override: *Focus with F* creates all the necessary keymaps 'fit view to selection' can also be done with F and not just NUMPAD_PERIOD (works for most of the main spaces such as Viewport, Outliner, Geometry Nodes, etc).
- Operator: *Set Custom Orientation* creates a temporaty orientation based on your selection, running the script from an empty area of the viewport goes back to Global pivot orientation (bound to D if *Operator Shurtcuts* is enabled).

### Changed ###
- Operator: Toggle Transform now goes back to the previous tool instead of defaulting to Box Select.
- Operator: Toggle Transform (renamed to Toggle) now toggles any tool with the input *idname* when creating a custom KMI.
- Customize: System preferences now load once with a button instead of being a toggle, preventing my preferences from overriding the user's preferences un.expectedly.
- All properties in the addon preferences have more detailed descriptions of what they do/enable--but no video links yet--.
- BUGFIX: load_post events being managed incorrectly caused some user preferences to reset unexpectedly.
- Plus some minor operator edits I can't recall.


## v0.1.2
*(06/Jul/21)*
- BUGFIX: Addon was deleting default blender matcaps LMAO, but only with certain custom builds (99.99% of users were unnafected).


## v0.1.1
*(04/Jul/21)*
- BUGFIX: Resource paths were NOT being created when needed, preventing the addon from being enabled.


## v0.1.0
*(03/Jul/21)*
- FIRST PUBLIC RELEASE.
