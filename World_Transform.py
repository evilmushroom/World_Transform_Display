bl_info = {
    "name": "World Transform Display and Edit",
    "author": "Your Name",
    "version": (1, 5),
    "blender": (3, 6, 9),
    "location": "View3D > Sidebar > Item Tab",
    "description": "Display and edit world transform for objects and bones with axis locking",
    "warning": "",
    "doc_url": "",
    "category": "Object",
}

import bpy
from bpy.props import FloatVectorProperty, StringProperty, BoolProperty, BoolVectorProperty
import mathutils
import json

class OBJECT_OT_CopyWorldTransform(bpy.types.Operator):
    bl_idname = "object.copy_world_transform"
    bl_label = "Copy World Transform"
    bl_description = "Copy the current world transform to clipboard"

    def execute(self, context):
        obj = context.active_object
        bone = context.active_pose_bone if obj and obj.type == 'ARMATURE' and context.mode == 'POSE' else None

        if obj or bone:
            if bone:
                world_matrix = obj.matrix_world @ bone.matrix
            else:
                world_matrix = obj.matrix_world

            transform_data = {
                "matrix": [list(row) for row in world_matrix]
            }
            context.window_manager.clipboard = json.dumps(transform_data)
            self.report({'INFO'}, "World transform copied to clipboard")
        else:
            self.report({'ERROR'}, "No object or bone selected")
            return {'CANCELLED'}
        return {'FINISHED'}

class OBJECT_OT_PasteWorldTransform(bpy.types.Operator):
    bl_idname = "object.paste_world_transform"
    bl_label = "Paste World Transform"
    bl_description = "Paste the world transform from clipboard"

    def execute(self, context):
        try:
            transform_data = json.loads(context.window_manager.clipboard)
            world_matrix = mathutils.Matrix([mathutils.Vector(row) for row in transform_data["matrix"]])
            
            for obj in context.selected_objects:
                if context.mode == 'POSE' and obj.type == 'ARMATURE':
                    for bone in obj.pose.bones:
                        if bone.bone.select:
                            self.apply_matrix_to_bone(obj, bone, world_matrix)
                else:
                    self.apply_matrix_to_object(obj, world_matrix)

            self.report({'INFO'}, "World transform pasted from clipboard")
        except:
            self.report({'ERROR'}, "Invalid clipboard data")
        return {'FINISHED'}

    def apply_matrix_to_object(self, obj, world_matrix):
        if obj.parent:
            obj.matrix_local = obj.parent.matrix_world.inverted() @ world_matrix
        else:
            obj.matrix_world = world_matrix

    def apply_matrix_to_bone(self, armature, bone, world_matrix):
        bone_matrix = armature.matrix_world.inverted() @ world_matrix
        bone.matrix = bone_matrix

class OBJECT_OT_ApplyWorldTransform(bpy.types.Operator):
    bl_idname = "object.apply_world_transform"
    bl_label = "Apply World Transform"
    bl_description = "Apply the current world transform to the selected objects or bones"

    def execute(self, context):
        scene = context.scene
        world_matrix = mathutils.Matrix.Translation(scene.world_transform_location) @ \
                       scene.world_transform_rotation.to_matrix().to_4x4() @ \
                       mathutils.Matrix.Diagonal(scene.world_transform_scale).to_4x4()

        # Store the active object
        active_obj = context.active_object

        # Apply transform to all selected objects
        for obj in context.selected_objects:
            if obj.type == 'ARMATURE' and context.mode == 'POSE':
                for bone in obj.pose.bones:
                    if bone.bone.select:
                        self.apply_matrix_to_bone(obj, bone, world_matrix, scene)
            else:
                self.apply_matrix_to_object(obj, world_matrix, scene)

        # Restore the active object
        context.view_layer.objects.active = active_obj

        bpy.context.view_layer.update()
        return {'FINISHED'}

    def apply_matrix_to_object(self, obj, world_matrix, scene):
        current_matrix = obj.matrix_world
        new_matrix = self.create_new_matrix(scene, current_matrix, world_matrix)

        if obj.parent:
            obj.matrix_local = obj.parent.matrix_world.inverted() @ new_matrix
        else:
            obj.matrix_world = new_matrix

        # Preserve original rotation mode
        rotation_mode = obj.rotation_mode
        obj.rotation_mode = 'XYZ'
        obj.rotation_mode = rotation_mode

        # Auto-keyframe if enabled
        if scene.tool_settings.use_keyframe_insert_auto:
            obj.keyframe_insert(data_path="location")
            if rotation_mode == 'QUATERNION':
                obj.keyframe_insert(data_path="rotation_quaternion")
            else:
                obj.keyframe_insert(data_path="rotation_euler")
            obj.keyframe_insert(data_path="scale")

    def apply_matrix_to_bone(self, armature, bone, world_matrix, scene):
        current_matrix = armature.matrix_world @ bone.matrix
        new_matrix = self.create_new_matrix(scene, current_matrix, world_matrix)
        bone_matrix = armature.matrix_world.inverted() @ new_matrix
        bone.matrix = bone_matrix

        # Preserve original rotation mode
        rotation_mode = bone.rotation_mode
        bone.rotation_mode = 'XYZ'
        bone.rotation_mode = rotation_mode

        # Auto-keyframe if enabled
        if scene.tool_settings.use_keyframe_insert_auto:
            bone.keyframe_insert(data_path="location")
            if rotation_mode == 'QUATERNION':
                bone.keyframe_insert(data_path="rotation_quaternion")
            else:
                bone.keyframe_insert(data_path="rotation_euler")
            bone.keyframe_insert(data_path="scale")

    def create_new_matrix(self, scene, current_matrix, world_matrix):
        new_loc = mathutils.Vector(current_matrix.to_translation())
        new_rot = current_matrix.to_quaternion()
        new_scale = mathutils.Vector(current_matrix.to_scale())

        target_loc = world_matrix.to_translation()
        target_rot = world_matrix.to_quaternion()
        target_scale = world_matrix.to_scale()

        for i in range(3):
            if not scene.lock_location[i]:
                new_loc[i] = target_loc[i]
            if not scene.lock_scale[i]:
                new_scale[i] = target_scale[i]

        if not any(scene.lock_rotation):
            new_rot = target_rot
        elif all(scene.lock_rotation):
            pass
        else:
            # Partial rotation locking
            euler_current = new_rot.to_euler()
            euler_target = target_rot.to_euler()
            for i in range(3):
                if not scene.lock_rotation[i]:
                    euler_current[i] = euler_target[i]
            new_rot = euler_current.to_quaternion()

        return mathutils.Matrix.Translation(new_loc) @ new_rot.to_matrix().to_4x4() @ mathutils.Matrix.Diagonal(new_scale).to_4x4()

class OBJECT_OT_UndoWorldTransform(bpy.types.Operator):
    bl_idname = "object.undo_world_transform"
    bl_label = "Undo World Transform"
    bl_description = "Undo the last applied world transform"

    def execute(self, context):
        scene = context.scene
        if scene.original_transform:
            try:
                original_transform = json.loads(scene.original_transform)
                scene.world_transform_location = original_transform["location"]
                scene.world_transform_rotation = original_transform["rotation"]
                scene.world_transform_scale = original_transform["scale"]
                bpy.ops.object.apply_world_transform()
                self.report({'INFO'}, "World transform undone")
            except:
                self.report({'ERROR'}, "Failed to undo world transform")
        else:
            self.report({'WARNING'}, "No previous transform to undo")
        return {'FINISHED'}

class OBJECT_OT_UpdateWorldTransform(bpy.types.Operator):
    bl_idname = "object.update_world_transform"
    bl_label = "Update World Transform"
    bl_description = "Update the world transform from the selected object or bone"
    
    def execute(self, context):
        obj = context.active_object
        bone = context.active_pose_bone if obj and obj.type == 'ARMATURE' and context.mode == 'POSE' else None

        if obj or bone:
            if bone:
                world_matrix = obj.matrix_world @ bone.matrix
            else:
                world_matrix = obj.matrix_world

            loc, rot, scale = world_matrix.decompose()

            context.scene.world_transform_location = loc
            context.scene.world_transform_rotation = rot.to_euler()
            context.scene.world_transform_scale = scale
        else:
            self.report({'ERROR'}, "No object or bone selected")
            return {'CANCELLED'}
        return {'FINISHED'}

class OBJECT_PT_WorldTransform(bpy.types.Panel):
    bl_idname = "OBJECT_PT_world_transform"
    bl_label = "World Transform"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        box = layout.box()
        row = box.row(align=True)
        row.operator("object.update_world_transform", text="", icon='IMPORT')
        row.operator("object.apply_world_transform", text="", icon='EXPORT')
        row.operator("object.undo_world_transform", text="", icon='LOOP_BACK')
        
        col = layout.column(align=True)
        col.prop(scene, "show_transform_details", text="Show Transform Details")
        
        if scene.show_transform_details:
            col.use_property_split = True
            col.use_property_decorate = False
            
            # Location
            col.label(text="Location:")
            for i, axis in enumerate(['X', 'Y', 'Z']):
                row = col.row(align=True)
                row.prop(scene, "world_transform_location", index=i, text=axis)
                row.prop(scene, "lock_location", index=i, text="", icon='LOCKED' if scene.lock_location[i] else 'UNLOCKED')
            
            # Rotation
            col.label(text="Rotation:")
            for i, axis in enumerate(['X', 'Y', 'Z']):
                row = col.row(align=True)
                row.prop(scene, "world_transform_rotation", index=i, text=axis)
                row.prop(scene, "lock_rotation", index=i, text="", icon='LOCKED' if scene.lock_rotation[i] else 'UNLOCKED')
            
            # Scale
            col.label(text="Scale:")
            for i, axis in enumerate(['X', 'Y', 'Z']):
                row = col.row(align=True)
                row.prop(scene, "world_transform_scale", index=i, text=axis)
                row.prop(scene, "lock_scale", index=i, text="", icon='LOCKED' if scene.lock_scale[i] else 'UNLOCKED')
        
        row = layout.row(align=True)
        row.operator("object.copy_world_transform", text="Copy", icon='COPYDOWN')
        row.operator("object.paste_world_transform", text="Paste", icon='PASTEDOWN')

        layout.prop(scene, "transform_orientation_slots", text="")

classes = (
    OBJECT_OT_CopyWorldTransform,
    OBJECT_OT_PasteWorldTransform,
    OBJECT_OT_UpdateWorldTransform,
    OBJECT_OT_ApplyWorldTransform,
    OBJECT_OT_UndoWorldTransform,
    OBJECT_PT_WorldTransform
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.world_transform_location = FloatVectorProperty(
        name="Location",
        subtype='TRANSLATION',
    )
    bpy.types.Scene.world_transform_rotation = FloatVectorProperty(
        name="Rotation",
        subtype='EULER',
    )
    bpy.types.Scene.world_transform_scale = FloatVectorProperty(
        name="Scale",
        subtype='XYZ',
        default=(1.0, 1.0, 1.0),
    )
    bpy.types.Scene.original_transform = StringProperty()
    bpy.types.Scene.show_transform_details = BoolProperty(
        name="Show Transform Details",
        description="Show or hide transform details",
        default=False
    )
    bpy.types.Scene.lock_location = BoolVectorProperty(
        name="Lock Location",
        description="Lock location axes",
        default=(False, False, False),
        size=3
    )
    bpy.types.Scene.lock_rotation = BoolVectorProperty(
        name="Lock Rotation",
        description="Lock rotation axes",
        default=(False, False, False),
        size=3
    )
    bpy.types.Scene.lock_scale = BoolVectorProperty(
        name="Lock Scale",
        description="Lock scale axes",
        default=(False, False, False),
        size=3
    )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    del bpy.types.Scene.world_transform_location
    del bpy.types.Scene.world_transform_rotation
    del bpy.types.Scene.world_transform_scale
    del bpy.types.Scene.original_transform
    del bpy.types.Scene.show_transform_details
    del bpy.types.Scene.lock_location
    del bpy.types.Scene.lock_rotation
    del bpy.types.Scene.lock_scale

if __name__ == "__main__":
    register()