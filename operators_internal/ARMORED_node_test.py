# import bpy


# class CustomNodeTree(bpy.types.NodeTree):
#     '''A custom node tree type'''
#     bl_idname='CustomNodeTree'
#     bl_label='Custom Node Tree'
#     bl_icon='BLENDER'

# class CustomNode(bpy.types.Node):
#     @classmethod
#     def poll(cls, ntree):
#         return ntree.bl_idname == 'CustomNodeTree'


# class CustomSimpleInputNode(CustomNode):
#     '''A simple input node'''
#     bl_idname = 'CustomSimpleInputNode'
#     bl_label = 'Simple Input Node'
#     bl_icon = 'PLUS'
    
#     # NOTE: does not get drawn automatically
#     intProp = bpy.props.IntProperty()
    
#     def init(self, context):
#         # NOTE: no elements will be drawn for output sockets
#         self.outputs.new('NodeSocketInt', "output")
#         # self.inputs.new('NodeSocketInt', "input")
        
#     def copy(self, node):
#         print("copied node", node)
        
#     def free(self):
#         print("Node removed", self)
        
#     # NOTE: input sockets are drawn by their respective methods
#     #   but output ones DO NOT for some reason, do it manually
#     #   and connect the drawn value to the output socket
#     def draw_buttons(self, context, layout):
#         # create a slider for int values
#         layout.prop(self, 'intProp')
    
#     #def draw_label(self):
#     #   return "this label is shown"
    

# import nodeitems_utils


# class CustomNodeCategory(nodeitems_utils.NodeCategory):
#     @classmethod
#     def poll(cls, context):
#         return context.space_data.tree_type == 'CustomNodeTree'
    

# node_categories = [
#     CustomNodeCategory("CUSTOMINPUTNODES", "Custom Input Nodes", items=[
#         nodeitems_utils.NodeItem("CustomSimpleInputNode",
#             label="Simple Input", settings={"intProp":repr(1.0)}),
#         nodeitems_utils.NodeItem("CustomSimpleInputNode"),
#         ]),
# ]



# classes=(
#         CustomNodeTree,
#         CustomSimpleInputNode,
#     )
    
# def register():
#     for cls in classes:
#         bpy.utils.register_class(cls)
#     nodeitems_utils.register_node_categories("CUSTOM_NODES", node_categories)


# def unregister():
#     nodeitems_utils.unregister_node_categories("CUSTOM_NODES")
#     for cls in classes:
#         bpy.utils.unregister_class(cls)


# if __name__=='__main__':
#     try:
#         nodeitems_utils.unregister_node_categories("CUSTOM_NODES")
#     finally:
#         register()
        