import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
scene.unit_settings.length_unit = 'METERS'

# Vestibulo de la Biblioteca Central: 12 x 15 m
# (Proyecto_Memoria_Definitivo_3_Dias_Terror_Intenso.txt, seccion 10.1)
# Version 2: se agrega el hueco de la salida lateral en la pared derecha,
# para conectar con ARC-LIB-004 (puerta de servicio). Cierra el
# inventario de arquitectura de la Fase 1.

ROOM_W = 12.0
ROOM_D = 15.0
FLOOR_THICK = 0.20
WALL_THICK = 0.25
WALL_H = 4.5

MAIN_DOOR_W = 2.20
INNER_DOOR_W = 1.80
SIDE_DOOR_W = 1.10       # coincide con ARC-LIB-004 (puerta de servicio)
SIDE_DOOR_Y = -4.0        # posicion a lo largo de la pared derecha (cerca del frente)

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

add_box("Floor", ROOM_W, ROOM_D, FLOOR_THICK, (0.0, 0.0, -FLOOR_THICK / 2.0))

front_side_w = (ROOM_W - MAIN_DOOR_W) / 2.0
add_box("Wall_Front_L", front_side_w, WALL_THICK, WALL_H,
        (-half_w + front_side_w / 2.0, -half_d + WALL_THICK / 2.0, WALL_H / 2.0))
add_box("Wall_Front_R", front_side_w, WALL_THICK, WALL_H,
        (half_w - front_side_w / 2.0, -half_d + WALL_THICK / 2.0, WALL_H / 2.0))
add_box("Wall_Front_Header", MAIN_DOOR_W, WALL_THICK, WALL_H - 2.6,
        (0.0, -half_d + WALL_THICK / 2.0, WALL_H - (WALL_H - 2.6) / 2.0))

back_side_w = (ROOM_W - INNER_DOOR_W) / 2.0
add_box("Wall_Back_L", back_side_w, WALL_THICK, WALL_H,
        (-half_w + back_side_w / 2.0, half_d - WALL_THICK / 2.0, WALL_H / 2.0))
add_box("Wall_Back_R", back_side_w, WALL_THICK, WALL_H,
        (half_w - back_side_w / 2.0, half_d - WALL_THICK / 2.0, WALL_H / 2.0))
add_box("Wall_Back_Header", INNER_DOOR_W, WALL_THICK, WALL_H - 2.6,
        (0.0, half_d - WALL_THICK / 2.0, WALL_H - (WALL_H - 2.6) / 2.0))

# pared izquierda: completa, sin abertura
add_box("Wall_Left", WALL_THICK, ROOM_D, WALL_H, (-half_w + WALL_THICK / 2.0, 0.0, WALL_H / 2.0))

# pared derecha: con hueco para la salida lateral (ARC-LIB-004)
door_y0 = SIDE_DOOR_Y - SIDE_DOOR_W / 2.0
door_y1 = SIDE_DOOR_Y + SIDE_DOOR_W / 2.0
seg_front_len = door_y0 - (-half_d)   # tramo entre la esquina frontal y la puerta
seg_back_len = half_d - door_y1        # tramo entre la puerta y la esquina trasera

add_box("Wall_Right_Front", WALL_THICK, seg_front_len, WALL_H,
        (half_w - WALL_THICK / 2.0, -half_d + seg_front_len / 2.0, WALL_H / 2.0))
add_box("Wall_Right_Back", WALL_THICK, seg_back_len, WALL_H,
        (half_w - WALL_THICK / 2.0, half_d - seg_back_len / 2.0, WALL_H / 2.0))
add_box("Wall_Right_Header", WALL_THICK, SIDE_DOOR_W, WALL_H - 2.4,
        (half_w - WALL_THICK / 2.0, SIDE_DOOR_Y, WALL_H - (WALL_H - 2.4) / 2.0))

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
print("RESULT_SIDE_DOOR_Y:", SIDE_DOOR_Y)
