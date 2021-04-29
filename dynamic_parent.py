# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

bl_info = {
    "name": "Dynamic Parent",
    "author": "Roman Volodin, roman.volodin@gmail.com",
    "version": (1, 0, 0),
    "blender": (2, 83, 0),
    "location": "View3D > Tool Panel",
    "description": "Allows to create and disable an animated ChildOf constraint",
    "category": "Animation",
}

import bpy
import mathutils


def get_rotation_mode(obj):
    if obj.rotation_mode in ('QUATERNION', 'AXIS_ANGLE'):
        return obj.rotation_mode.lower()
    return 'euler'


def get_selected_objects(context):
    if context.mode not in ('OBJECT', 'POSE'):
        return

    if context.mode == 'OBJECT':
        active = context.active_object
        selected = [obj for obj in context.selected_objects if obj != active]

    if context.mode == 'POSE':
        active = context.active_pose_bone
        selected = [bone for bone in context.selected_pose_bones if bone != active]

    selected.append(active)
    return selected


def get_last_dymanic_parent_constraint(obj):
    if not obj.constraints:
        return
    const = obj.constraints[-1]
    if const.name.startswith("DP_") and const.influence == 1:
        return const


def insert_keyframe(obj, frame):
    rotation_mode = get_rotation_mode(obj)
    data_paths = (
         'location',
        f'rotation_{rotation_mode}',
         'scale',
    )
    for data_path in data_paths:
        obj.keyframe_insert(data_path=data_path, frame=frame)


def insert_keyframe_constraint(constraint, frame):
    constraint.keyframe_insert(data_path='influence', frame=frame)


def dp_keyframe_insert_obj(obj):
    obj.keyframe_insert(data_path="location")
    if obj.rotation_mode == 'QUATERNION':
        obj.keyframe_insert(data_path="rotation_quaternion")
    elif obj.rotation_mode == 'AXIS_ANGLE':
        obj.keyframe_insert(data_path="rotation_axis_angle")
    else:
        obj.keyframe_insert(data_path="rotation_euler")
    obj.keyframe_insert(data_path="scale")


def dp_keyframe_insert_pbone(arm, pbone):
    arm.keyframe_insert(data_path='pose.bones["'+pbone.name+'"].location')
    if pbone.rotation_mode == 'QUATERNION':
        arm.keyframe_insert(data_path='pose.bones["'+pbone.name+'"].rotation_quaternion')
    elif pbone.rotation_mode == 'AXIS_ANGLE':
        arm.keyframe_insert(data_path='pose.bones["'+pbone.name+'"].rotation_axis_angel')
    else:
        arm.keyframe_insert(data_path='pose.bones["'+pbone.name+'"].rotation_euler')
    arm.keyframe_insert(data_path='pose.bones["'+pbone.name+'"].scale') 


def dp_create_dynamic_parent_obj(op):
    obj = bpy.context.active_object
    scn = bpy.context.scene
    list_selected_obj = bpy.context.selected_objects

    if len(list_selected_obj) == 2:
        i = list_selected_obj.index(obj)
        list_selected_obj.pop(i)
        parent_obj = list_selected_obj[0]

        dp_keyframe_insert_obj(obj)
        bpy.ops.object.constraint_add_with_targets(type='CHILD_OF')
        last_constraint = obj.constraints[-1]

        if parent_obj.type == 'ARMATURE':
            last_constraint.subtarget = parent_obj.data.bones.active.name
            last_constraint.name = "DP_"+last_constraint.target.name+"."+last_constraint.subtarget
        else:
            last_constraint.name = "DP_"+last_constraint.target.name

        C = bpy.context.copy()
        C["constraint"] = last_constraint
        bpy.ops.constraint.childof_set_inverse(C, constraint=last_constraint.name, owner='OBJECT')

        current_frame = scn.frame_current
        scn.frame_current = current_frame-1
        obj.constraints[last_constraint.name].influence = 0
        obj.keyframe_insert(data_path='constraints["'+last_constraint.name+'"].influence')

        scn.frame_current = current_frame
        obj.constraints[last_constraint.name].influence = 1
        obj.keyframe_insert(data_path='constraints["'+last_constraint.name+'"].influence')

        for ob in list_selected_obj:
            ob.select_set(False)

        obj.select_set(True)
    else:
        op.report({'ERROR'}, "Two objects must be selected")

def dp_create_dynamic_parent_pbone(op):
    arm = bpy.context.active_object
    pbone = bpy.context.active_pose_bone
    scn = bpy.context.scene
    list_selected_obj = bpy.context.selected_objects

    if len(list_selected_obj) == 2 or len(list_selected_obj) == 1:
        if len(list_selected_obj) == 2:
            i = list_selected_obj.index(arm)
            list_selected_obj.pop(i)
            parent_obj = list_selected_obj[0]
            if parent_obj.type == 'ARMATURE':
                parent_obj_pbone = parent_obj.data.bones.active
        else:
            parent_obj = arm
            selected_bones = bpy.context.selected_pose_bones
            selected_bones.remove(pbone)
            parent_obj_pbone = selected_bones[0]

        dp_keyframe_insert_pbone(arm, pbone)
        bpy.ops.pose.constraint_add_with_targets(type='CHILD_OF')
        last_constraint = pbone.constraints[-1]

        if parent_obj.type == 'ARMATURE':
            last_constraint.subtarget = parent_obj_pbone.name
            last_constraint.name = "DP_"+last_constraint.target.name+"."+last_constraint.subtarget
        else:
            last_constraint.name = "DP_"+last_constraint.target.name

        C = bpy.context.copy()
        C["constraint"] = last_constraint
        bpy.ops.constraint.childof_set_inverse(C, constraint=last_constraint.name, owner='BONE')
        
        current_frame = scn.frame_current
        scn.frame_current = current_frame-1
        pbone.constraints[last_constraint.name].influence = 0
        arm.keyframe_insert(data_path='pose.bones["'+pbone.name+'"].constraints["'+last_constraint.name+'"].influence')
        
        scn.frame_current = current_frame
        pbone.constraints[last_constraint.name].influence = 1
        arm.keyframe_insert(data_path='pose.bones["'+pbone.name+'"].constraints["'+last_constraint.name+'"].influence')  
    else:
        op.report({'ERROR'}, "Two objects must be selected")


def disable_constraint(obj, const, frame):
    if type(obj) == bpy.types.PoseBone:
        matrix_final = obj.matrix
    else:
        matrix_final = obj.matrix_world

    insert_keyframe(obj, frame=frame-1)
    insert_keyframe_constraint(const, frame=frame-1)

    const.influence = 0
    if type(obj) == bpy.types.PoseBone:
        obj.matrix = matrix_final
    else:
        obj.matrix_world = matrix_final

    insert_keyframe(obj, frame=frame)
    insert_keyframe_constraint(const, frame=frame)
    return


def dp_clear(obj, pbone):
    dp_curves = []
    dp_keys = []
    for fcurve in obj.animation_data.action.fcurves:
        if "constraints" in fcurve.data_path and "DP_" in fcurve.data_path:
            dp_curves.append(fcurve)

    for f in dp_curves:
        for key in f.keyframe_points:
            dp_keys.append(key.co[0])

    dp_keys = list(set(dp_keys))
    dp_keys.sort()

    for fcurve in obj.animation_data.action.fcurves[:]:
        if fcurve.data_path.startswith("constraints") and "DP_" in fcurve.data_path:
            obj.animation_data.action.fcurves.remove(fcurve)
        else:
            for frame in dp_keys:
                for key in fcurve.keyframe_points[:]:
                    if key.co[0] == frame:
                        fcurve.keyframe_points.remove(key)
            if not fcurve.keyframe_points:
                obj.animation_data.action.fcurves.remove(fcurve)

    if pbone:
        obj = pbone
    for const in obj.constraints[:]:
        if const.name.startswith("DP_"):
            obj.constraints.remove(const)


class DYNAMIC_PARENT_OT_create(bpy.types.Operator):
    """Create a new animated Child Of constraint"""
    bl_idname = "dynamic_parent.create"
    bl_label = "Create Constraint"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        frame = context.scene.frame_current

        if obj.type == 'ARMATURE':
            obj = bpy.context.active_pose_bone
            const = get_last_dymanic_parent_constraint(obj)
            if const:
                disable_constraint(obj, const, frame)
            dp_create_dynamic_parent_pbone(self)
        else:
            const = get_last_dymanic_parent_constraint(obj)
            if const:
                disable_constraint(obj, const, frame)
            dp_create_dynamic_parent_obj(self)

        return {'FINISHED'}


class DYNAMIC_PARENT_OT_disable(bpy.types.Operator):
    """Disable the current animated Child Of constraint"""
    bl_idname = "dynamic_parent.disable"
    bl_label = "Disable Constraint"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode in ('OBJECT', 'POSE')

    def execute(self, context):
        frame = context.scene.frame_current
        objects = get_selected_objects(context)
        counter = 0

        if not objects:
            self.report({'ERROR'}, 'Nothing selected.')
            return {'CANCELLED'}

        for obj in objects:
            const = get_last_dymanic_parent_constraint(obj)
            if const is None:
                continue
            disable_constraint(obj, const, frame)
            counter += 1

        self.report({'INFO'}, f'{counter} constraints were disabled.')
        return {'FINISHED'}


class DYNAMIC_PARENT_OT_clear(bpy.types.Operator):
    """Clear Dynamic Parent constraints"""
    bl_idname = "dynamic_parent.clear"
    bl_label = "Clear Dynamic Parent"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        pbone = None
        obj = bpy.context.active_object
        if obj.type == 'ARMATURE':
            pbone = bpy.context.active_pose_bone

        dp_clear(obj, pbone)

        return {'FINISHED'}

class DYNAMIC_PARENT_OT_bake(bpy.types.Operator):
    """Bake Dynamic Parent animation"""
    bl_idname = "dynamic_parent.bake"
    bl_label = "Bake Dynamic Parent"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = bpy.context.active_object
        scn = bpy.context.scene

        if obj.type == 'ARMATURE':
            obj = bpy.context.active_pose_bone
            bpy.ops.nla.bake(frame_start=scn.frame_start, 
                             frame_end=scn.frame_end, step=1, 
                             only_selected=True, visual_keying=True,
                             clear_constraints=False, clear_parents=False, 
                             bake_types={'POSE'})
            for const in obj.constraints[:]:
                if const.name.startswith("DP_"):
                    obj.constraints.remove(const)
        else:
            bpy.ops.nla.bake(frame_start=scn.frame_start,
                             frame_end=scn.frame_end, step=1, 
                             only_selected=True, visual_keying=True,
                             clear_constraints=False, clear_parents=False, 
                             bake_types={'OBJECT'})
            for const in obj.constraints[:]:
                if const.name.startswith("DP_"):
                    obj.constraints.remove(const)

        return {'FINISHED'}


class DYNAMIC_PARENT_MT_clear_menu(bpy.types.Menu):
    """Clear or bake Dynamic Parent constraints"""
    bl_label = "Clear Dynamic Parent?"
    bl_idname = "DYNAMIC_PARENT_MT_clear_menu"

    def draw(self, context):
        layout = self.layout
        layout.operator("dynamic_parent.clear", text="Clear", icon="X")
        layout.operator("dynamic_parent.bake", text="Bake and clear", icon="REC")


class DYNAMIC_PARENT_PT_ui(bpy.types.Panel):
    """User interface for Dynamic Parent addon"""
    bl_label = "Dynamic Parent"
    bl_idname = "DYNAMIC_PARENT_PT_ui"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Dynamic Parent"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("dynamic_parent.create", text="Create", icon="KEY_HLT")
        col.operator("dynamic_parent.disable", text="Disable", icon="KEY_DEHLT")
        col.menu("DYNAMIC_PARENT_MT_clear_menu", text="Clear")


classes = (
    DYNAMIC_PARENT_OT_create,
    DYNAMIC_PARENT_OT_disable,
    DYNAMIC_PARENT_OT_clear,
    DYNAMIC_PARENT_OT_bake,
    DYNAMIC_PARENT_MT_clear_menu,
    DYNAMIC_PARENT_PT_ui,
)

register, unregister = bpy.utils.register_classes_factory(classes)

if __name__ == "__main__":
    register()
