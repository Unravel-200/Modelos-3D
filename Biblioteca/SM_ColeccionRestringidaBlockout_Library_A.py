import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
scene.unit_settings.length_unit = 'METERS'

# Coleccion restringida de la Biblioteca Central: 10 x 14 m
# (Proyecto_Memoria_Definitivo_3_Dias_Terror_Intenso.txt, seccion 10.1)
# Conectada detras de Vigilancia (SM_VigilanciaBlockout_Library_A), cuya
# pared trasera esta en Y=22.5 con hueco de 1.80 m centrado en X=0.
# Aqui van FUR-LIB-007/008 (estanterias), PRP-LIB-006 (libros) y
# ARC-LIB-002 (compuerta al sotano), en un paso posterior.

ROOM_W = 10.0
ROOM_D = 14.0
FLOOR_THICK = 0.20
WALL_THICK = 0.15
WALL_H = 4.5

VIGILANCIA_BACK_Y = 22.5
FRONT_DOOR_W = 1.80  # coincide con el hueco de vigilancia

ROOM_CENTER_Y = VIGILANCIA_BACK_Y + ROOM_D / 2.0

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
front_y = VIGILANCIA_BACK_Y
back_y = VIGILANCIA_BACK_Y + ROOM_D

add_box("Floor", ROOM_W, ROOM_D, FLOOR_THICK, (0.0, ROOM_CENTER_Y, -FLOOR_THICK / 2.0))

front_side_w = (ROOM_W - FRONT_DOOR_W) / 2.0
add_box("Wall_Front_L", front_side_w, WALL_THICK, WALL_H,
        (-half_w + front_side_w / 2.0, front_y + WALL_THICK / 2.0, WALL_H / 2.0))
add_box("Wall_Front_R", front_side_w, WALL_THICK, WALL_H,
        (half_w - front_side_w / 2.0, front_y + WALL_THICK / 2.0, WALL_H / 2.0))
add_box("Wall_Front_Header", FRONT_DOOR_W, WALL_THICK, WALL_H - 2.6,
        (0.0, front_y + WALL_THICK / 2.0, WALL_H - (WALL_H - 2.6) / 2.0))

# pared trasera cerrada por ahora: la salida real de esta sala es la
# compuerta oculta en el piso (ARC-LIB-002 / FUR-LIB-008), no una puerta.
add_box("Wall_Back", ROOM_W, WALL_THICK, WALL_H, (0.0, back_y - WALL_THICK / 2.0, WALL_H / 2.0))

add_box("Wall_Left", WALL_THICK, ROOM_D, WALL_H,
        (-half_w + WALL_THICK / 2.0, ROOM_CENTER_Y, WALL_H / 2.0))
add_box("Wall_Right", WALL_THICK, ROOM_D, WALL_H,
        (half_w - WALL_THICK / 2.0, ROOM_CENTER_Y, WALL_H / 2.0))

bpy.ops.object.select_all(action='DESELECT')
for p in parts:
    p.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()

mesh_obj = bpy.context.active_object
mesh_obj.name = "SM_ColeccionRestringidaBlockout_Library_A"
mesh_obj.data.name = "SM_ColeccionRestringidaBlockout_Library_A_Mesh"

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
bpy.ops.object.mode_set(mode='OBJECT')

mat_floor = bpy.data.materials.new(name="M_Floor_ColeccionRestringidaBlockout")
mat_floor.use_nodes = True
bsdf_f = mat_floor.node_tree.nodes.get("Principled BSDF")
if bsdf_f:
    bsdf_f.inputs["Base Color"].default_value = (0.55, 0.53, 0.50, 1.0)
    bsdf_f.inputs["Roughness"].default_value = 0.6

mat_wall = bpy.data.materials.new(name="M_Wall_ColeccionRestringidaBlockout")
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

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, ROOM_CENTER_Y, -FLOOR_THICK / 2.0))
col_floor = bpy.context.active_object
col_floor.name = "UCX_SM_ColeccionRestringidaBlockout_Library_A_00"
col_floor.scale = (ROOM_W, ROOM_D, FLOOR_THICK)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
col_floor.display_type = 'WIRE'
col_floor.hide_render = True

bpy.ops.wm.save_as_mainfile(
    filepath="C:\\Users\\jeffa\\Desktop\\Proyecto\\Modelos-3D\\Biblioteca\\SM_ColeccionRestringidaBlockout_Library_A.blend")

print("RESULT_NAME:", mesh_obj.name)
print("RESULT_DIMS: X={:.3f} Y={:.3f} Z={:.3f}".format(*mesh_obj.dimensions))
print("RESULT_CENTER_Y:", ROOM_CENTER_Y)
