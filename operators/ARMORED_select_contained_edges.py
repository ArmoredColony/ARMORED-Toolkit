# v1.1

import bpy
import bmesh
   
   
class ARMORED_OT_select_contained_edges(bpy.types.Operator):
    '''Converts your selection of faces to the contained edges (it subtracts the border loop).

(www.armoredColony.com)'''
    
    bl_idname = 'armored.select_contained_edges'
    bl_label = 'ARMORED Select Contained Edges'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        ob = context.edit_object
        me = ob.data
        bm = bmesh.from_edit_mesh(me)
        
        bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')

        original_selection = set(e for e in bm.edges if e.select)
        contained_edges = original_selection - set(e for e in bm.edges 
            if e.select and (e.is_boundary or not all(f.select for f in e.link_faces)))
        
        bpy.ops.mesh.select_all(action='DESELECT')

        for e in contained_edges:
            e.select = True
            
        bmesh.update_edit_mesh(me)
        return {'FINISHED'}


classes = (
    ARMORED_OT_select_contained_edges,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)