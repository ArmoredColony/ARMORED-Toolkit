# ARMORED TOOLKIT CHANGELOG

## v0.7.0
*01/Apr/2023*

### Added
- UI Buttons **Align Objects** to the snapping menu in the VIEW3D header. Aligns selected objects to the active object in the X, Y or Z axis.
- Operator **Circle Deform** creates a curve circle deformer for the selected objects with the correct size and orientation
- Operator **Rename** batch renames the selected objects by their dimensions (default), vertex count or creation order.
- Operator **Filter Objects with Ngons/Triangles/Non-Quads** deselects any objects that do not match the specified criteria.
- Operator **Remove Modifiers** removes specific modifiers from the selected objects (by type, name or all).
- Operator **Camera from View** creates a camera based on the current view.
- Operator **Rename** renames the object selected in the viewport.
- Operator **Render** renders all, the selected or the active scene camera to a specified location without opening the render window.
- Operator **Filter Objects by Sides** will deselect any objects that do not match the specified filter (ngons, triangles or non-quads).

### Changed
- Operators **Lattice Deform**, **Curve Deform** and **Circle Deform** will no longer be parented to anything by default.
- Operator **Classic Mirror**: if the last modifier in the stack is a SUBSURF type, the mirror modifier will move up one position (keeping the SUBRURF last).
- Operator **Subdivide**: I did something to it, don't remember what.
- Operator **Transfer Data** renames the object data to match the object name.
- Preferences: made EEVEE AO and SSR a little stronger.


## v0.6.3
*10/Jan/2023*

### Added
- Operator **Control Loops** uses the bevel tool to create control loops for subdivision surfaces.
- Operator **Cursor to Selected**: move the cursor to the selected element and rotate it to match its normal.

## Changed
- Operator **Clear Location** will automatically switch between the active center or the selection bounds center (can still be overriden in the redo panel).

## Fixed
- Operator **Curve Deform** was not placing the curve correctly in the Z (vertical) axis.


## v0.6.2
*09/Dec/2022*

## Added
- Operator **Curve Deform**: create an automatically sized curve deformer and assign it to all selected objects.

## Changed
- Operator **Classic Mirror** now uses default merge and bisect thresholds.


## v0.6.1
*08/Dec/2022*

### Changed
- Addon Preferences **Load Preferences** loads a few more prefences than before (check tooltip).
- Addon Preferences **Load Theme** now loads a Matcap and HDRI that matches the Armored Colony Theme.


## v0.6.0
*04/Dec/2022*

### Added
- Operator **Transfer Data**: 'Duplicate the `object.data` of the active object to all selected objects and optionally turn them into linked duplicates.

### Changed
- Operator **Vitaly Poke** is more accurate. Also works with multi-object editing.
- Operator **Lattice** panel properties got renamed/reordered to be more intuitive.
- Operator **Primitives** got rewritten for future expandability. Also supports scaling inside the modal and toggling between CURSOR/WORLD alignment when creating the greometry.

### Fixed
- Operator **Clear Location** was NOT keeping the relative positions between objects when the property `as_group` (now called `keep_relative`) was enabled.
- Operator **Muscle Rig** was NOT placing the Empty Controllers at the right location. The `matrix_world` multiplication order was incorrect.
- Operator **Delete Mirrored** would sometimes crash at the poll method.
- Operator **Focus** would NOT run in Node editors because `NODE_EDITOR` is not a context mode you can poll, duuuuh.
- Preferences **Load Armored Colony Theme** now loads my latest theme (someone said it looked like Maya and XSI had a baby).


## v0.5.4
*18/Nov/2022*

### Added
- Operator **Clear Location**: Similar to Blender's clear location (ALT G), but this version can optionally keep the relative locations between the selected objects and move them as a group to world zero.

### Fixed
- Operator **Delete Mirrored** would crash if you ran the script with a selection and tried transforming that selection afterwards. Fixed by adding  `bm.select_flush_mode()`.
- Operator **Select Hard Edges**: `edge_angle` propertry no longer goes to negative values.

### Changed
- Operators **Classic Mirror** and **Delete Mirrored** have smaller default thresholds `0.0001 m`.


## v0.5.3
*17/Nov/2022*

### Fixed
- Operator **Delete Mirrored** would always delete geometry based on the object's origin, even when the mirror modifier had a different object plugged into `mirror_object`.


## v0.5.2
*15/Nov/2022*

### Changed
- Operators **Increase/Decrease SubD Mod Level** will now only adjust the subdivision level without changing any other settings like `use_limit_surface` or `quality`.


## v0.5.1
*14/Nov/2022*

### Changed
- Renamed **Subdivision Set** to **Fast Subdivision**.
- Operator **Fast Subdivision** now defaults to `use_limit_surface = True` and `quality = 1`. The potential performance boost isn't as great as disabling it entirely but its more consistent. Setting it to `False` could actually lower performance significantly in some situations (SubD level 3 and above with my typical mesh resolutions would become slower).

### Fixed
- Broken Keymap PFD buttom in the addon preferences. The file had been removed by accident.


## v0.5.0
*03/Nov/2022*

### Added
- Operator **Hide**: A hide toggle. When called on selected objects it will hide normally, if called again (and your selection did not change) it will unhide the previously hidden objects.
- Operator **Mask from Selected**: Creates a sculpt mask from vertices selected in Edit Mode.
- Operator **Set Brush**: Lets you create hotkey brush presets (if you make an 'hPolish' brush, you can hotkey it through Blender's Keymap Editor)
- File **ARMORED_export.py**: Will now house multiple export Operators.

### Changed
- Operator **Lattice**: Lattice deformer rotation now matches the Active Object's rotation by default (optional).
- Operator **Fast Crease**: Increased functionality thanks to `bmesh`, such as creasing without changing your selection or creasing all by angle.
- Operator **Focus**: Split into individual Operators for different contexts (makes it easier to hotkey from the search menu).
- Operator **Classic Mirror**: Now defaults to mirroring in the *X* axis only.
- File **SubD View in Edit**: Apparently I added a bunch of empty space to the code for no reason, that seems to be it.
- Operator **Subdivision Set** : `use_limit_surface` now defaults to `False`, for way faster subdivisions at the expense of accuracy.

### Fixed
- Operator **Center Vertices**: Did not work correctly if the object's origin was not at the world origin.
- Operator **Compare**: uses `bl_rna.identifier == 'Collection'` instead of creating a new collection type property.

### Removed
- Operator **Export FBX**: Now part of multiple Operators in the **ARMORED_export.py** file.


## v0.4.7
*08/Sep/2022*

### Fixed
- Operator **Fast Crease**: would sometimes think nothing was selected because it was using outdated object data.


## v0.4.6
*07/Sep/2022*

### Changed
- Operator **Select by Trait**: The pop up will now appear even when nothing was found/selected (so you can be sure its working).
- Operator **Silhouette**: now saves ALL your current viewport settings to a JSON file before modifying them to mimic a silhouette mode. Running the operator again will read that file and restore your viewport to the exact same settings.
- Operator **Fast Crease**: now works with vertex creasing.
- Operator **Subdivision Set**: now disables `use_limit_surface` by default when applying the SUBSURF modifier (faster but less accurate)..

### Fixed
- Operator **Lattice**: sanity fix (replaced one instance of `bpy.context` for `context`). Realistically, there was no need for this change since it does not affect anything.


## v0.4.5
*30/Ago/2022*

### Changed
- Operator **Muscle Rig**: Now allows changing lattice resolution similar to the **Lattice** Operator.


## v0.4.4
*30/Ago/2022*

### Added
- Operator **Muscle Rig** (bundled with **Lattice** script): Creates a lattice around your selection and hooks the control points to 3 Empties aligned vertically. Made to be used with vertical cyber muscle kitbash.

### Changed
- Operator **Lattice**: Now works with multiple selections.
- Operator **Remesh**: Blender Voxel Remesh can now preserve vertex colors natively. This script is relegated to simply enabling it.
- Operator Shortcuts keymaps:
    + I'm too lazy today, they're inconsequential anyway.


## v0.4.3
*03/Jun/2022*

### Added
- Resources: Another studio HDRI I really like.

### Changed
- Operator **Lattice**: `scale_offset` property is now a vector so each dimension can be adjusted independently.
- Operator **Single Subdivision Level** was renamed to **Adjust Subdivision Level**
- Operator **Adjust Subdivision Level** will no longer add a new Subsurf Modifier if an existing disabled/invisible one is found.
- Operator Shortcuts keymaps:
    + I'm too lazy today, they're inconsequential anyway.

### Fixed
- Operator **Primitives**: modal primitives no longer crash in Blender 3.2


## v0.4.2
*09/May/2022*

### Added
- Keymap Override **Wireframe Selected** (EXPERIMENTAL): displays the wireframe for any object you select, similar to other DCCs.

## v0.4.1
*05/May/2022*

### Added
- Theme **Candy Neutral**: gray background, white UI and red selections. Works well with black, gray and white matcaps.
- Operator **Classic Mirror**: creates a mirror modifier with my usual settings. If the modifier already exists, it duplicates and applies it.

### Changed
- Operator **Flatten**: now includes a flatten to AVERAGE mode (the new default).
- Operator **Toggle Tool**: can now specify the fallback tool (the tool that runs when the gizmo is active but you don't click on it directly) (defaults to `builtin.select_box` which is my personal preference).
- Operator Shortcuts keymaps:
    + &plus; [CTRL][ALT][X] for **Classic Mirror** operator.
    + &plus; [ALT][F] activates `mesh.f2` operator.
- Operators **Duplicate** and **Extract** no longer activate the move tool automatically.


## v0.4.0
*27/Apr/2022*

### Added
- Operators **Select Ngons/Triangles/Non-Quads**: all individual operators, which will select the specified polygons and open an error window if any are found (error window helps when selected polygons are too small or just hard to see).
- Operator **Circularize**: extracted (copy pasted) the **Make Circle** operator from the LoopTools addon (only thing I used from it).
- Operator **Delete Mirrored**: deletes unnecessary geometry that's already being generated by the mirror modifier.
- Operator **Symmetrize**: similar to Blender's but it symmetrizes all the geometry regardless of your selection.
- Operator **Smart Delete**: deletes components based on your selection mode (vertex, edge, face) without aditional menus.
- Operator **Flatten**: flattens your selection to the nearest axis or the active face.

### Changed
- Operator **Single Subdivision Level** was split and renamed to **Increase SubD mod level** and **Decrease SubD mod level** and drawn menus were removed since the operators can be searched and hotkeyed individually now..
- Operators **Increase SubD mod level** and **Decrease SubD mod level**: no longer affect render levels or generate undo history (no more Redo panel).
- Operator **Subdivision Set**: no longer generates Undo history (no more Redo panel).
- Operator **Lattice**: added the option of clearning all mesh transforms before applying the lattice.
- Operator **Vitaly Poke**: added an extra option *Deselect Corners* which allows deselecting only the corner triangles instead of all triangles.
- Operator Shortcuts keymaps:
    + &plus; [CTRL][ALT][X] to **Symmetrize** in X.
    + &plus; [CTRL][ALT][F] to **Flatten** Selection.
    - &minus; [CTRL][ALT] [X]/[Y]/[Z] to set vertex positions to world center X, Y and Z (wasn't using them).

### Fixed
- Operator **Autosmooth**: now works without toggling between object and edit mode under the hood (should be faster when the selected objects have slow modifiers).
- Operator **Lattice**: now works even if the mesh origin is offset (positioned at bounding box center by default).
- Operator **Focus**: removed a leftover debug print.
- Operator **Single Subdivision Level**: raised an exception when the active object was not part of the selection.
- Operator **Open Most Recent**: now removes the file from the recent files list if it doesn't exist (SOMETIMES?!).


## v0.3.4
*11/Apr/2022*

### Added
- Operator **Toggle Overlays**: Toggles the visibility of Overlays AND Gizmos. 
- Keymap Override **Transform with Gizmos**: Pressing [G][S] or [R] activates the Gizmo version of the Move, Scale and Rotate Tools'
- Some extra primitives have been replaced with modals so you can adjust their segments (when applicable) with the scroll wheel.
- New Lambert like matcap from NVil but it's a little harsh sometimes.

### Changed
- Operator **Isolate Cycle** was renamed to **Compare**.

### Fixed
- Operator **Focus** now works with more than one object in Edit mode.
- Operator **Compare** now works with collections inside other collections.
- Operator **Switch Color Modes** sometimes threw an error when searched from a window that was not part of the `VIEW3D` area.
- Loopcut Keymap Exception: "... has no attribute `release_confirm`".

### Removed
- Some deprecated operators that were not even visible to users from within blender anymore (**Select Through** was among them); if I ever want that operator back I need to put more thought into it (hard-coded keymaps were a bad idea).


## v0.3.3
*25/Mar/2022*

### Added
- Operator **Switch Color Modes**: Switches back and forth between two viewport color modes (Vertex color and Object color by default).

### Changed
- ZBrush Sculpting keymaps: Vertex Paint Mode now shares hotkeys with Sculpt mode, such as changing brush size with [S] with `release_confirm` enabled, isolating with [TAB] and focusing with [F].
    + &plus; [V] to Switch Color Modes.
    + &plus; [ALT][V] to Toggle Silhouette mode.
- Operator Shortcuts keymaps:
    + &plus; [V] to Switch Color Modes.


## v0.3.2
*(20/Mar/2022)*

### Added
- **PDF Keymap List** in the Addon Preferences

### Changed
- Transform with Gizmos keymaps:
    + &plus; [G] to activate the Move Tool (this override used to only work for the Scale and Rotate tools but now affects all three).
- Operator Shortcuts keymaps:
    - &minus; [CTRL][R] to rest on ground in Edit Mode.
    - &minus; [ALT][SHIFT][DOUBLE_LMB] to select linked toggle (it conflicted with Blender's loop selection or something.)

### Removed
- Video link buttons for the **Keymap Overrides** --at least until I have actual videos I can link to.


## v0.3.1
*(11/Mar/2022)*

### Changed
- Operator **Focus** now has a dedicated operator for Edit Mode, which fixes some keymap priority issues with binding to [F].
- Sculpting Setup keymap override is renamed to ZBrush Sculpting an is focused on emulating my ZBrush hotkeys). Added some extra keymaps to achieve this (navigation not included):
    + &plus; [S] to change brush size.
    + &plus; [SHIFT][S] to change brush intensity.
    + &plus; [Q] to switch active object (subtool).
    + &plus; Double [Q] to switch active object and then frame it.
    + &plus; [SHIFT][F] to toggle wireframe.
    + &plus; [TAB] enters local view instead of switching to edit mode.


## v0.3.0
*(10/Mar/2022)*

### Added
- Operator **Remesh** (Sculpt Mode): Same as regular voxel remesh but with vertex color preservation.
- [CTRL][R] keymap for the new remesh operator.
- Operator **Isolate Cycle** (Outliner): based on your outliner selections, isolate 1 object and cycle to the next/previous one using the SCROll wheel. Also works with entire collections.
- Operator **Scale Unmasked (Sculpt Mode)** is a macro than sets pivot to unmasked (while in sculpt mode) and activates the default modal resize operator.
- Operator **Node Stats** (Geometry Nodes Workspace): prints node information: name, type, inputs, outputs, etc.

### Changed
- **Armored Focus** now used in sculpt mode too. While hovering the mesh, runs `view3d.view_center_pick`; while hovering empty canvas space, runs `view3d.view_all`, 
- Operator Shortcuts keymaps:
    + &plus; Local view (isolate) keymaps now have `frame_selected` set to False.
- Sculpting Setup keymaps:
    + &plus; [S] to scale.
    + &plus; [F] to focus).
    + &plus; Brush scale and Brush intensity now have `release_confirm` enabled.
    + &plus; Probably other stuff.
    - &minus; [D] to switch objects.
    - &minus; [*] trivial stuff I never used.
- **Toggle Cavity** now reports the current cavity mode when toggled on.
- Fixed some descriptions and class names.
- **Open Most Recent** [SHIFT][ALT][R] works in more windows and not just the 3DVIEW.
- `handler.load_post.remove(...)` was commented out from `system.unregister` for so reason. It's now enabled again.

### Removed
- Operator **Smart Loopcut** (replaced with a keymap to the original Loopcut with `release_confirm` enabled)


## v0.2.0
*(29/Nov/2021)*

### Added
- Operator **Delete and Grid Fill** combines Delete Faces and Fill Grid into a single operator. This new operator appears in the [X] (delete) panel automatically.
- **TAB History** is now exposed to users in the addon preferences
- HDRIS, Studio Lights, and Themes to the resources you can install along with MATCAPS.
- Keymap Override **Allow Gizmo Click**. Activate gizmos the instance you click on them instead of waiting for a [MOUSEDRAG] event.
- [D] keymap for switching objects in sculpt mode.
- [F] keymap for sculpt mode with confirm on release Enabled.
- [SHIFT][F] keymap for sculpt mode with confirm on release Enabled.

### Changed
- **Maya Cube** primitive is now a modal and allows adding segments with [MOUSESCROLL].
- **Armored Focus** is now bound to the F key again when **Operator Keymaps** are enabled.
- **Armored Focus** operator was simplified and performance was increased.
- [ALT+E] now activates **Extrude along normals** when **Operator Keymaps** are enabled instead of displaying the extrude menu.
- Updated the **Armored Colony** theme preset to be more consistent (red UI highlights have black text whenever possible).
- Added, Polished and even Removed a poop ton of addon code.


## v0.1.3
*(16/Jul/2021)*

### Added
- Keymap Override: **Focus with F** creates all the necessary keymaps 'fit view to selection' can also be done with F and not just NUMPAD_PERIOD (works for most of the main spaces such as Viewport, Outliner, Geometry Nodes, etc).
- Operator: **Set Custom Orientation** creates a temporaty orientation based on your selection, running the script from an empty area of the viewport goes back to Global pivot orientation (bound to D if **Operator Shurtcuts** is enabled).

### Changed
- Operator: Toggle Transform now goes back to the previous tool instead of defaulting to Box Select.
- Operator: Toggle Transform (renamed to Toggle) now toggles any tool with the input **idname** when creating a custom KMI.
- Customize: System preferences now load once with a button instead of being a toggle, preventing my preferences from overriding the user's preferences un.expectedly.
- All properties in the addon preferences have more detailed descriptions of what they do/enable--but no video links yet--.
- Plus some minor operator edits I can't recall.

### Fixed
- `load_post` events being managed incorrectly caused some user preferences to reset unexpectedly.


## v0.1.2
*(06/Jul/2021)*
- BUGFIX: Addon was deleting default blender matcaps LMAO, but only with certain custom builds (99.99% of users were unnafected).


## v0.1.1
*(04/Jul/2021)*
- BUGFIX: Resource paths were NOT being created when needed, preventing the addon from being enabled.


## v0.1.0
*(03/Jul/2021)*
- FIRST PUBLIC RELEASE.
