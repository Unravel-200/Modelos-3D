import bpy
import math

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
scene.unit_settings.length_unit = 'METERS'

# Farola de la Plaza Central: poste en forma de L (vertical + brazo
# horizontal), farol hexagonal colgando en la punta del brazo.

BASE_R = 0.22
BASE_H = 0.25
POLE_R = 0.06
POLE_H = 3.0
ARM_LEN = 1.3
ARM_R = 0.05
HEAD_SIZE = 0.35
HEAD_H = 0.45
CAP_H = 0.15

metal_parts = []

def add_cyl(name, radius, depth, loc, verts=16, rot=(0.0, 0.0, 0.0)):
    bpy.ops.mesh.primitive_cylinder_add(radius=radius, depth=depth, location=loc, vertices=verts)
    obj = bpy.context.active_object
    obj.name = name
    if rot != (0.0, 0.0, 0.0):
        obj.rotation_euler = rot
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    metal_parts.append(obj)
    return obj

# base
add_cyl("Base", BASE_R, BASE_H, (0.0, 0.0, BASE_H / 2.0))

# poste vertical
pole_top_z = BASE_H + POLE_H
add_cyl("Pole", POLE_R, POLE_H, (0.0, 0.0, BASE_H + POLE_H / 2.0))

# brazo horizontal en forma de L, sale desde la punta del poste hacia +X
arm_x = ARM_LEN / 2.0
add_cyl("Arm", ARM_R, ARM_LEN, (arm_x, 0.0, pole_top_z),
        rot=(0.0, math.radians(90.0), 0.0))

# pequeno codo/union donde el brazo se dobla (esfera pequena, disimula la union)
bpy.ops.mesh.primitive_uv_sphere_add(radius=POLE_R * 1.3, location=(0.0, 0.0, pole_top_z),
                                      segments=12, ring_count=8)
elbow = bpy.context.active_object
elbow.name = "Elbow"
metal_parts.append(elbow)

# farol hexagonal, colgando de la punta del brazo (baja un poco desde el brazo)
head_z = pole_top_z - HEAD_H / 2.0 - ARM_R
head_x = ARM_LEN
add_cyl("LanternHead", HEAD_SIZE / 2.0, HEAD_H, (head_x, 0.0, head_z), verts=6)

# remate inferior del farol (cono pequeno apuntando hacia abajo)
cap_z = head_z - HEAD_H / 2.0 - CAP_H / 2.0
bpy.ops.mesh.primitive_cone_add(radius1=HEAD_SIZE / 2.2, radius2=0.02, depth=CAP_H,
                                 location=(head_x, 0.0, cap_z), vertices=6,
                                 rotation=(math.radians(180.0), 0.0, 0.0))
cap = bpy.context.active_object
cap.name = "Cap"
metal_parts.append(cap)

# bombilla interior (emisiva)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(head_x, 0.0, head_z), segments=12, ring_count=8)
bulb = bpy.context.active_object
bulb.name = "Bulb"

bpy.ops.object.select_all(action='DESELECT')
for p in metal_parts:
    p.select_set(True)
bpy.context.view_layer.objects.active = metal_parts[0]
bpy.ops.object.join()

mesh_obj = bpy.context.active_object
mesh_obj.name = "SM_Lamppost_PlazaCentral_A"
mesh_obj.data.name = "SM_Lamppost_PlazaCentral_A_Mesh"

bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.03)
bpy.ops.object.mode_set(mode='OBJECT')

mat_metal = bpy.data.materials.new(name="M_Metal_Lamppost")
mat_metal.use_nodes = True
bsdf_m = mat_metal.node_tree.nodes.get("Principled BSDF")
if bsdf_m:
    bsdf_m.inputs["Base Color"].default_value = (0.08, 0.08, 0.09, 1.0)
    bsdf_m.inputs["Roughness"].default_value = 0.45
    bsdf_m.inputs["Metallic"].default_value = 0.7
mesh_obj.data.materials.clear()
mesh_obj.data.materials.append(mat_metal)

mat_bulb = bpy.data.materials.new(name="M_Emissive_LamppostBulb")
mat_bulb.use_nodes = True
bsdf_b = mat_bulb.node_tree.nodes.get("Principled BSDF")
if bsdf_b:
    bsdf_b.inputs["Base Color"].default_value = (1.0, 0.92, 0.75, 1.0)
    bsdf_b.inputs["Emission Color"].default_value = (1.0, 0.88, 0.6, 1.0)
    bsdf_b.inputs["Emission Strength"].default_value = 2.5
bulb.data.materials.clear()
bulb.data.materials.append(mat_bulb)

bpy.ops.object.select_all(action='DESELECT')
mesh_obj.select_set(True)
bulb.select_set(True)
bpy.context.view_layer.objects.active = mesh_obj
bpy.ops.object.join()

final_obj = bpy.context.active_object
final_obj.name = "SM_Lamppost_PlazaCentral_A"
final_obj.data.name = "SM_Lamppost_PlazaCentral_A_Mesh"

bpy.ops.mesh.primitive_cylinder_add(radius=BASE_R, depth=BASE_H + POLE_H,
                                     location=(0.0, 0.0, (BASE_H + POLE_H) / 2.0), vertices=12)
collision_obj = bpy.context.active_object
collision_obj.name = "UCX_SM_Lamppost_PlazaCentral_A_00"
collision_obj.display_type = 'WIRE'
collision_obj.hide_render = True

bpy.ops.wm.save_as_mainfile(
    filepath="C:\\Users\\jeffa\\Desktop\\Proyecto\\Modelos-3D\\Plaza\\SM_Lamppost_PlazaCentral_A.blend")

print("RESULT_NAME:", final_obj.name)
print("RESULT_DIMS: X={:.3f} Y={:.3f} Z={:.3f}".format(*final_obj.dimensions))
