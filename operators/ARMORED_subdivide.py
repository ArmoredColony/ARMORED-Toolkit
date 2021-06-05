# v1.2

import bpy, bmesh
from bpy.props import IntProperty, BoolProperty, FloatProperty


class ARMORED_OT_subdivide(bpy.types.Operator):
    '''Destructively adds 1 subdivision level to the selected objects (if a SubD modifier is present it will subtract a level from it to try to maintain overall polycount).

 (www.armoredColony.com)'''
    
    bl_idname = 'view3d.armored_subdivide'
    bl_label = 'ARMORED Subdivide'
    bl_options = {'REGISTER', 'UNDO'}

    subdivisions  : IntProperty   (name='Subdivisions',  default=1, min=1, max=20, options={'SKIP_SAVE', 'HIDDEN'})
    # smoothness    : FloatProperty (name='Smoothness',    default=0, min=0, max=1, options={'SKIP_SAVE', 'HIDDEN'})
    ngons         : BoolProperty  (name='Create N-Gons', default=True)
    limit_surface : BoolProperty  (name='Limit Surface', default=False)
    
    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        mode = context.object.mode
        previous_mode = False
        valid_obs = [ob for ob in context.selected_objects if ob.type in {'MESH'}]

        if not valid_obs:
            self.report({'WARNING'}, 'ARMORED Toolkit: No valid objects were found.')
            return {'CANCELLED'}

        # Get last SubD Mod from all objects.
        subd_mods = []
        for ob in valid_obs:
            try:
                subd_mods.append(next(mod for mod in reversed(ob.modifiers) if mod.type == 'SUBSURF' and mod.show_viewport))
            except StopIteration:
                pass

        if mode != 'OBJECT':
            if mode == 'EDIT':
                me = context.edit_object.data
                bm = bmesh.from_edit_mesh(me)

                sel_mode = context.tool_settings.mesh_select_mode[:]

                sel_components = next((v for v in bm.verts if v.select), None)
                if sel_components is not None:

                    if sel_mode[1]:
                        edges = set(e for e in bm.edges if e.select)

                        # If only one edge is selected, switch to vert mode so you can see the divisions being added.
                        if len(edges) == 1: 
                            bpy.ops.mesh.select_mode(type='VERT')
                
                    bpy.ops.mesh.subdivide('EXEC_DEFAULT', number_cuts=1, ngon=self.ngons)
                    return {'FINISHED'}

            previous_mode = mode
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        
        for mod in subd_mods:
            mod.show_viewport = False
            mod.levels -= 1

        original_active = context.object
        for ob in valid_obs:
            mod = ob.modifiers.new(name='temp subd', type='SUBSURF')
            mod.boundary_smooth = 'PRESERVE_CORNERS'
            mod.use_limit_surface = self.limit_surface

            context.view_layer.objects.active = ob
            bpy.ops.object.modifier_apply(modifier=mod.name)
            
        context.view_layer.objects.active = original_active
        
        for mod in subd_mods:
            mod.show_viewport = True

        if previous_mode:
            bpy.ops.object.mode_set(mode=previous_mode, toggle=False)

        return {'FINISHED'}


classes = (
    ARMORED_OT_subdivide,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)    


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)
