import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
scene.unit_settings.length_unit = 'METERS'

# Banca de la Plaza Central: banca de exterior en concreto/piedra
# (distinta de la banca de madera del vestibulo de la biblioteca).

BENCH_LENGTH = 1.80
SEAT_DEPTH = 0.45
SEAT_HEIGHT = 0.45
SEAT_THICK = 0.08
SUPPORT_WIDTH = 0.12

parts = []

def add_box(name, size_x, size_y, size_z, loc):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size_x, size_y, size_z)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    parts.append(obj)
    return obj

# asiento de losa de concreto
add_box("Seat", BENCH_LENGTH, SEAT_DEPTH, SEAT_THICK, (0.0, 0.0, SEAT_HEIGHT))

# dos soportes solidos de piedra en los extremos (sin patas delgadas,
# estilo institucional resistente a la intemperie)
half_l = BENCH_LENGTH / 2.0 - SUPPORT_WIDTH / 2.0
for side, sign in (("L", -1), ("R", 1)):
    add_box("Support_{}".format(side), SUPPORT_WIDTH, SEAT_DEPTH * 0.85, SEAT_HEIGHT,
            (sign * half_l, 0.0, SEAT_HEIGHT / 2.0))

bpy.ops.object.select_all(action='DESELECT')
for p in parts:
    p.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()

mesh_obj = bpy.context.active_object
mesh_obj.name = "SM_Bench_PlazaCentral_A"
mesh_obj.data.name = "SM_Bench_PlazaCentral_A_Mesh"

bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
bpy.ops.object.mode_set(mode='OBJECT')

mat = bpy.data.materials.new(name="M_Concrete_PlazaBench")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.58, 0.57, 0.54, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.85
mesh_obj.data.materials.clear()
mesh_obj.data.materials.append(mat)

dims = mesh_obj.dimensions
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, SEAT_HEIGHT / 2.0))
collision_obj = bpy.context.active_object
collision_obj.name = "UCX_SM_Bench_PlazaCentral_A_00"
collision_obj.scale = (BENCH_LENGTH, SEAT_DEPTH, SEAT_HEIGHT)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
collision_obj.display_type = 'WIRE'
collision_obj.hide_render = True

bpy.ops.wm.save_as_mainfile(
    filepath="C:\\Users\\jeffa\\Desktop\\Proyecto\\Modelos-3D\\Plaza\\SM_Bench_PlazaCentral_A.blend")

print("RESULT_NAME:", mesh_obj.name)
print("RESULT_DIMS: X={:.3f} Y={:.3f} Z={:.3f}".format(*mesh_obj.dimensions))
