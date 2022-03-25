# ARMORED TOOLKIT CHANGELOG


## v0.3.3
*(unreleased)*

### Added ###
- Operator *Switch Color Modes*: Switches back and forth between two viewport color modes (Vertex color and Object color by default).

### Changed ###
- ZBrush Sculpting keymaps: Vertex Paint Mode now shares hotkeys with Sculpt mode, such as changing brush size with [S] with `release_confirm` enabled, isolating with [TAB] and focusing with [F].


## v0.3.2
*(20/Mar/22)*

### Added ###
- **PDF Keymap List** in the Addon Preferences

### Removed ###
- Video link buttons for the *Keymap Overrides* --at least until I have actual videos I can link to.

### Changed ###
- Transform with Gizmos keymaps:
    + [G] to activate the Move Tool (this override used to only work for the Scale and Rotate tools but now affects all three).
- Operator Shortcuts keymaps:
    - [CTRL][R] to rest on ground in Edit Mode.
    - [ALT][SHIFT][DOUBLE_LMB] to select linked toggle (it conflicted with Blender's loop selection or something.)


## v0.3.1
*(11/Mar/22)*

### Changed ###
- Operator *Focus* now has a dedicated operator for Edit Mode, which fixes some keymap priority issues with binding to [F].
- Sculpting Setup keymap override is renamed to ZBrush Sculpting an is focused on emulating my ZBrush hotkeys). Added some extra keymaps to achieve this (navigation not included):
    + [S] to change brush size.
    + [SHIFT][S] to change brush intensity.
    + [Q] to switch active object (subtool).
    + Double [Q] to switch active object and then frame it.
    + [SHIFT][F] to toggle wireframe.
    + [TAB] enters local view instead of switching to edit mode.


## v0.3.0
*(10/Mar/22)*

### Added ###
- Operator *Remesh* (Sculpt Mode): Same as regular voxel remesh but with vertex color preservation.
- [CTRL][R] keymap for the new remesh operator.
- Operator *Isolate Cycle* (Outliner): based on your outliner selections, isolate 1 object and cycle to the next/previous one using the SCROll wheel. Also works with entire collections.
- Operator *Scale Unmasked (Sculpt Mode)* is a macro than sets pivot to unmasked (while in sculpt mode) and activates the default modal resize operator.
- Operator *Node Stats* (Geometry Nodes Workspace): prints node information: name, type, inputs, outputs, etc.

### Changed ###
- *Armored Focus* now used in sculpt mode too. While hovering the mesh, runs `view3d.view_center_pick`; while hovering empty canvas space, runs **view3d.view_all**, 
- Operator Shortcuts keymaps:
    + Local view (isolate) keymaps now have `frame_selected` set to False.
- Sculpting Setup keymaps:
    + [S] to scale.
    + [F] to focus).
    + Brush scale and Brush intensity now have `release_confirm` enabled.
    + Probably other stuff.
    - [D] to switch objects.
    - [*] trivial stuff I never used.
- *Toggle Cavity* now reports the current cavity mode when toggled on.
- Fixed some descriptions and class names.
- *Open Most Recent* [SHIFT][ALT][R] works in more windows and not just the 3DVIEW.
- `handler.load_post.remove(...)` was commented out from `system.unregister` for so reason. It's now enabled again.

### Removed ###
- Operator *Smart Loopcut* (replaced with a keymap to the original Loopcut with `release_confirm` enabled)


## v0.2.0
*(29/Nov/21)*

### Added ###
- Operator *Delete and Grid Fill* combines Delete Faces and Fill Grid into a single operator. This new operator appears in the [X] (delete) panel automatically.
- *TAB History* is now exposed to users in the addon preferences
- HDRIS, Studio Lights, and Themes to the resources you can install along with MATCAPS.
- Keymap Override *Allow Gizmo Click*. Activate gizmos the instance you click on them instead of waiting for a [MOUSEDRAG] event.
- [D] keymap for switching objects in sculpt mode.
- [F] keymap for sculpt mode with confirm on release Enabled.
- [SHIFT][F] keymap for sculpt mode with confirm on release Enabled.

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
