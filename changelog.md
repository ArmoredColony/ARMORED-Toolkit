# ARMORED TOOLKIT CHANGELOG


## v0.2.0 (LATEST)
*(21/Sep/21)*

**NEW**
- Keymap Override/Operator: *Maya Extrude*/*Armored Extrude* replace the default Extrude operator *E* with a "new" one that extrudes faces along their individual normals (like Maya) --avoids having to Extrude Cancel and Shrink Fatten aftwerards--.
- Operator: *Delete and Grid Fill* combines Delete Faces and Fill Grid into a single operator. This new operator appears in the *X* panel automatically.


## v0.1.3
*(16/Jul/21)*

**NEW**
- Keymap Override: *Focus with F* creates all the necessary keymaps 'fit view to selection' can also be done with F and not just NUMPAD_PERIOD (works for most of the main spaces such as Viewport, Outliner, Geometry Nodes, etc).
- Operator: *Set Custom Orientation* creates a temporaty orientation based on your selection, running the script from an empty area of the viewport goes back to Global pivot orientation (bound to D if *Operator Shurtcuts* is enabled).

**CHANGES**
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