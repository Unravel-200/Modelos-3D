import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
scene.unit_settings.length_unit = 'METERS'

# Vestibulo de la Biblioteca Central: 12 x 15 m
# (Proyecto_Memoria_Definitivo_3_Dias_Terror_Intenso.txt, seccion 10.1)
ROOM_W = 12.0
ROOM_D = 15.0
FLOOR_THICK = 0.20
WALL_THICK = 0.25   # pared exterior/estructural (Guia, seccion 4)
WALL_H = 4.5        # altura de piso academico aproximada (18-20 m / 4 pisos)

MAIN_DOOR_W = 2.20   # coincide con ARC-LIB-001 (puerta principal doble)
INNER_DOOR_W = 1.80  # abertura hacia recepcion, mas angosta

parts = []

def add_box(name, size_x, size_y, size_z, loc):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size_x, size_y, size_z)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    parts.append(obj)
    return obj

half_w = ROOM_W / 2.0
half_d = ROOM_D / 2.0

# piso
add_box("Floor", ROOM_W, ROOM_D, FLOOR_THICK, (0.0, 0.0, -FLOOR_THICK / 2.0))

# pared frontal (entrada principal, en -Y), con hueco central de MAIN_DOOR_W
front_side_w = (ROOM_W - MAIN_DOOR_W) / 2.0
add_box("Wall_Front_L", front_side_w, WALL_THICK, WALL_H,
        (-half_w + front_side_w / 2.0, -half_d + WALL_THICK / 2.0, WALL_H / 2.0))
add_box("Wall_Front_R", front_side_w, WALL_THICK, WALL_H,
        (half_w - front_side_w / 2.0, -half_d + WALL_THICK / 2.0, WALL_H / 2.0))
# dintel sobre la puerta principal
add_box("Wall_Front_Header", MAIN_DOOR_W, WALL_THICK, WALL_H - 2.6,
        (0.0, -half_d + WALL_THICK / 2.0, WALL_H - (WALL_H - 2.6) / 2.0))

# pared trasera (hacia recepcion, en +Y), con hueco central de INNER_DOOR_W
back_side_w = (ROOM_W - INNER_DOOR_W) / 2.0
add_box("Wall_Back_L", back_side_w, WALL_THICK, WALL_H,
        (-half_w + back_side_w / 2.0, half_d - WALL_THICK / 2.0, WALL_H / 2.0))
add_box("Wall_Back_R", back_side_w, WALL_THICK, WALL_H,
        (half_w - back_side_w / 2.0, half_d - WALL_THICK / 2.0, WALL_H / 2.0))
add_box("Wall_Back_Header", INNER_DOOR_W, WALL_THICK, WALL_H - 2.6,
        (0.0, half_d - WALL_THICK / 2.0, WALL_H - (WALL_H - 2.6) / 2.0))

# paredes laterales completas (sin abertura, se conectaran a otras salas despues)
add_box("Wall_Left", WALL_THICK, ROOM_D, WALL_H, (-half_w + WALL_THICK / 2.0, 0.0, WALL_H / 2.0))
add_box("Wall_Right", WALL_THICK, ROOM_D, WALL_H, (half_w - WALL_THICK / 2.0, 0.0, WALL_H / 2.0))

bpy.ops.object.select_all(action='DESELECT')
for p in parts:
    p.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()

mesh_obj = bpy.context.active_object
mesh_obj.name = "SM_VestibuloBlockout_Library_A"
mesh_obj.data.name = "SM_VestibuloBlockout_Library_A_Mesh"

bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
bpy.ops.object.mode_set(mode='OBJECT')

mat_floor = bpy.data.materials.new(name="M_Floor_VestibuloBlockout")
mat_floor.use_nodes = True
bsdf_f = mat_floor.node_tree.nodes.get("Principled BSDF")
if bsdf_f:
    bsdf_f.inputs["Base Color"].default_value = (0.55, 0.53, 0.50, 1.0)
    bsdf_f.inputs["Roughness"].default_value = 0.6

mat_wall = bpy.data.materials.new(name="M_Wall_VestibuloBlockout")
mat_wall.use_nodes = True
bsdf_w = mat_wall.node_tree.nodes.get("Principled BSDF")
if bsdf_w:
    bsdf_w.inputs["Base Color"].default_value = (0.80, 0.79, 0.76, 1.0)
    bsdf_w.inputs["Roughness"].default_value = 0.8

mesh_obj.data.materials.clear()
mesh_obj.data.materials.append(mat_floor)
mesh_obj.data.materials.append(mat_wall)

mesh = mesh_obj.data
wall_idx = 1
for poly in mesh.polygons:
    coords = [mesh.vertices[v].co for v in poly.vertices]
    cz = sum(c.z for c in coords) / len(coords)
    if cz > 0.0:
        poly.material_index = wall_idx

# colision: piso + 4 paredes exteriores como cajas simples
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, -FLOOR_THICK / 2.0))
col_floor = bpy.context.active_object
col_floor.name = "UCX_SM_VestibuloBlockout_Library_A_00"
col_floor.scale = (ROOM_W, ROOM_D, FLOOR_THICK)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
col_floor.display_type = 'WIRE'
col_floor.hide_render = True

bpy.ops.wm.save_as_mainfile(
    filepath="C:\\Users\\jeffa\\Desktop\\Proyecto\\Modelos-3D\\Biblioteca\\SM_VestibuloBlockout_Library_A.blend")

print("RESULT_NAME:", mesh_obj.name)
print("RESULT_DIMS: X={:.3f} Y={:.3f} Z={:.3f}".format(*mesh_obj.dimensions))
