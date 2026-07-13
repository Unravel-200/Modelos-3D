import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
scene.unit_settings.length_unit = 'METERS'

# Set de mesa + 4 sillas para la Soda de Estudios Generales.

TABLE_W = 1.20
TABLE_D = 0.75
TABLE_H = 0.75
TABLE_TOP_THICK = 0.04
LEG_SIZE = 0.05

CHAIR_SEAT_W = 0.42
CHAIR_SEAT_D = 0.42
CHAIR_SEAT_H = 0.45
CHAIR_BACK_H = 0.40

table_parts = []
chair_parts = []

def add_box(name, size_x, size_y, size_z, loc, target_list):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size_x, size_y, size_z)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    target_list.append(obj)
    return obj

# --- mesa ---
# la tapa se apoya justo sobre las patas (que llegan hasta TABLE_H -
# TABLE_TOP_THICK), no hay hueco entre ambas
add_box("TableTop", TABLE_W, TABLE_D, TABLE_TOP_THICK,
        (0, 0, TABLE_H - TABLE_TOP_THICK / 2.0), table_parts)
half_tw = TABLE_W / 2.0 - LEG_SIZE / 2.0 - 0.05
half_td = TABLE_D / 2.0 - LEG_SIZE / 2.0 - 0.05
for i, (sx, sy) in enumerate(((-1, -1), (-1, 1), (1, -1), (1, 1))):
    add_box("TableLeg_{:02d}".format(i), LEG_SIZE, LEG_SIZE, TABLE_H - TABLE_TOP_THICK,
            (sx * half_tw, sy * half_td, (TABLE_H - TABLE_TOP_THICK) / 2.0), table_parts)

bpy.ops.object.select_all(action='DESELECT')
for p in table_parts:
    p.select_set(True)
bpy.context.view_layer.objects.active = table_parts[0]
bpy.ops.object.join()
table = bpy.context.active_object
table.name = "Table"

# --- 4 sillas alrededor de la mesa ---
chair_positions = [
    (0.0, -TABLE_D / 2.0 - 0.35, 0.0),
    (0.0, TABLE_D / 2.0 + 0.35, 180.0),
    (-TABLE_W / 2.0 - 0.35, 0.0, -90.0),
    (TABLE_W / 2.0 + 0.35, 0.0, 90.0),
]
all_chairs = []
for idx, (cx, cy, cangle) in enumerate(chair_positions):
    single_chair_parts = []
    add_box("Seat_{:02d}".format(idx), CHAIR_SEAT_W, CHAIR_SEAT_D, 0.05,
            (0.0, 0.0, CHAIR_SEAT_H), single_chair_parts)
    add_box("Back_{:02d}".format(idx), CHAIR_SEAT_W, 0.04, CHAIR_BACK_H,
            (0.0, -CHAIR_SEAT_D / 2.0 + 0.02, CHAIR_SEAT_H + CHAIR_BACK_H / 2.0), single_chair_parts)
    half_cw = CHAIR_SEAT_W / 2.0 - 0.04
    half_cd = CHAIR_SEAT_D / 2.0 - 0.04
    for j, (sx, sy) in enumerate(((-1, -1), (-1, 1), (1, -1), (1, 1))):
        add_box("Leg_{:02d}_{}".format(idx, j), 0.04, 0.04, CHAIR_SEAT_H,
                (sx * half_cw, sy * half_cd, CHAIR_SEAT_H / 2.0), single_chair_parts)

    bpy.ops.object.select_all(action='DESELECT')
    for p in single_chair_parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = single_chair_parts[0]
    bpy.ops.object.join()
    chair = bpy.context.active_object
    chair.name = "Chair_{:02d}".format(idx)

    # el origen tras el join queda en el punto del primer trozo creado
    # (el asiento, no el piso). Se re-centra en el piso real (world Z=0
    # bajo el centro de la silla) ANTES de rotar/reposicionar, para no
    # hundir la silla al moverla.
    bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

    chair.rotation_euler[2] = __import__("math").radians(cangle)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=False)
    chair.location = (cx, cy, 0.0)
    bpy.ops.object.transform_apply(location=True, rotation=False, scale=False)
    all_chairs.append(chair)

bpy.ops.object.select_all(action='DESELECT')
for c in all_chairs:
    c.select_set(True)
bpy.context.view_layer.objects.active = all_chairs[0]
bpy.ops.object.join()
chairs = bpy.context.active_object
chairs.name = "Chairs"

bpy.ops.object.select_all(action='DESELECT')
table.select_set(True)
chairs.select_set(True)
bpy.context.view_layer.objects.active = table
bpy.ops.object.join()

mesh_obj = bpy.context.active_object
mesh_obj.name = "SM_DiningSet_Soda_A"
mesh_obj.data.name = "SM_DiningSet_Soda_A_Mesh"

bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
bpy.ops.object.mode_set(mode='OBJECT')

mat = bpy.data.materials.new(name="M_Plastic_SodaFurniture")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.75, 0.15, 0.12, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.5
mesh_obj.data.materials.clear()
mesh_obj.data.materials.append(mat)

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, TABLE_H / 2.0))
collision_obj = bpy.context.active_object
collision_obj.name = "UCX_SM_DiningSet_Soda_A_00"
collision_obj.scale = (TABLE_W, TABLE_D, TABLE_H)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
collision_obj.display_type = 'WIRE'
collision_obj.hide_render = True

bpy.ops.wm.save_as_mainfile(
    filepath="C:\\Users\\jeffa\\Desktop\\Proyecto\\Modelos-3D\\Generales\\SM_DiningSet_Soda_A.blend")

print("RESULT_NAME:", mesh_obj.name)
print("RESULT_DIMS: X={:.3f} Y={:.3f} Z={:.3f}".format(*mesh_obj.dimensions))
