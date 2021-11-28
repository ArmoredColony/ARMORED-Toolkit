import os
from . import paths
from . import extrapy


'''
Some blender property descriptions (such as keymap lists) are too large to inline 
with the rest of the code. Put them here...
'''


sculpting_keymaps = [
    '       1 - Clay Buildup',
    'ALT 1 - Clay',
    '       2 - Dam Standard',
    'ALT 2 - Standard',
    '       3 - Scrape',
    'ALT 3 - Flatten',
    '       4 - Move',
    'ALT 4 - Snake Hook',
    '       5 - Crease',
    'ALT 5 - Inflate',
    'ALT F - Set Pivot',
    'SHIFT W - Wireframe',
    'CTRL D - Add Multires Level',
    'ALT - Inverts Brush Stroke'
    ]

sculpting_keymaps = '\n'.join(sculpting_keymaps)


operator_keymaps = [
    '[Global]',
    'CTRL COMMA - Blender Preferences',

    '\n[3D View]',
    'T                      - Redo Panel',
    'Q                     - Border Select, Paint Select (if held down)',
    'QQ                   - Select Tools Pie',
    'SHIFT W          - Toggle Wireframe',
    'ALT W              - Toggle Overlays',
    'W                     - Toggle Move Gizmo',
    'CTRL SHIFT A  - Autosmooth',
    'ALT SHIFT R     - Open Most Recent',
    'CTRL R             - Rest on Ground',
    'ALT C               - Toggle Cavity',
    'ALT SHIFT C    - Cycle Cavity Types',
    'C (Mesh)         - Loopcut',
    'CTRL D           - Destructive Subdivision',
    'PAGE_UP        - Increase Subdivision Modifier Level',
    'PAGE_DOWN  - Decrease Subdivision Modifier Level',
    'CTRL SHIFT F - Marquee Zoom',
    'F5                    - Reload Scripts',

    # '\n\u2022Object',
    # 'SHIFT N - Move to New Collection',

    '\nThis isn\'t even half but the rest don\'t fit LMAO, I\'ll make a PDF with all my Operator Hotkeys later',

    # '\n\u2022Mesh',
    # 'SHIFT F - Select Linked Flat Faces',
    # 'ALT F - Make Face/F2 Addon',
    # 'D - Set Custom Orientation',
    # 'CTRL SHIFT LMOUSE - Select Shortest Path',
    # 'CTRL SHIFT E - Extract Faces',
    # 'CTRL SHIFT D - Duplicate Faces',
    # 'SHIFT SCROLL - Select More/Less',
    # 'CTRL SHIFT SCROLL UP - Select Adjacent Components',
    # 'B - Fast Bevel',
    # 'SHIFT B - Bridge Edges',
    # 'CTRL R - Rest on Ground',
    # 'ALT R - Select Edge Ring',
    # 'SHIFT C - Connect',
    # 'SHIFT V - Align Verts (Experimental)',
    # 'SHIFT NUMPAD_PLUS - Crease Selected',
    # 'SHIFT NUMPAD_MINUS - Uncrease Selected/All',
    # 'ALT DOUBLE_CLICK - Select Linked',
    # 'ALT 5 - Region to Loop',
    # 'ALT 1/2/3 - SubD in Edit Toggles',
    # 'CTRL ALT X,Y,Z - Align Verts to World Axis',
    # 'CTRL 1-9 - SubD Modifier Level in Edit',

    # '\n\u2022Curve',
    # 'CTRL SHIFT LMOUSE - Select SHortest Path',
    ]

operator_keymaps = '\n'.join(operator_keymaps)

smart_tab_functions = [
    'Skip Undo - pressing TAB  does not generate any undo history',
    'Grouped Undo - consecutive TAB presses are grouped into a single undo step',
    'Blender Default - each TAB press creates an individual undo step',
]

smart_tab_functions = '\n'.join(smart_tab_functions)


matcap_files = sorted(os.listdir(paths.AddonPaths.matcaps))
matcap_files = extrapy.add_to_list_elements(matcap_files, prefix='\u2022 ')
matcap_files = '\n'.join(matcap_files)

hdri_files = sorted(os.listdir(paths.AddonPaths.hdris))
hdri_files = extrapy.add_to_list_elements(hdri_files, prefix='\u2022 ')
hdri_files = '\n'.join(hdri_files)

studio_light_files = sorted(os.listdir(paths.AddonPaths.studio_lights))
studio_light_files = extrapy.add_to_list_elements(studio_light_files, prefix='\u2022 ')
studio_light_files = '\n'.join(studio_light_files)

theme_files = sorted(os.listdir(paths.AddonPaths.themes))
theme_files = extrapy.add_to_list_elements(theme_files, prefix='\u2022 ')
theme_files = '\n'.join(theme_files)