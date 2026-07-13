import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
scene.unit_settings.length_unit = 'METERS'

# Sotano 1 de la Biblioteca Central: 45 x 35 m
# (Proyecto_Memoria_Definitivo_3_Dias_Terror_Intenso.txt, seccion 10.1)
# Se accede unicamente por la compuerta oculta en el piso de la Coleccion
# Restringida (ARC-LIB-002 / FUR-LIB-008), no por una pared: es una
# conexion vertical, no horizontal como las salas anteriores.
#
# Posicionado debajo de la planta baja: el subsuelo de los pisos ya
# construidos (vestibulo, recepcion, vigilancia, coleccion restringida)
# esta en Z=-0.20. El sotano cuelga debajo de eso.
# Centrado en X=0, Y=29.5 (bajo la Coleccion Restringida), para que la
# compuerta caiga dentro de su area.

ROOM_W = 45.0
ROOM_D = 35.0
WALL_THICK = 0.30   # muro de sotano, mas grueso (estructural/subterraneo)
FLOOR_THICK = 0.20
CEILING_Z = -0.20    # subsuelo de la planta baja
ROOM_H = 3.5          # techo bajo, tipico de sotano/deposito
CENTER_X = 0.0
CENTER_Y = 29.5

floor_top_z = CEILING_Z - ROOM_H
floor_center_z = floor_top_z - FLOOR_THICK / 2.0
wall_center_z = (floor_top_z + CEILING_Z) / 2.0

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
add_box("Floor", ROOM_W, ROOM_D, FLOOR_THICK, (CENTER_X, CENTER_Y, floor_center_z))

# techo (subsuelo de la planta baja, cierra el sotano por arriba)
add_box("Ceiling", ROOM_W, ROOM_D, FLOOR_THICK, (CENTER_X, CENTER_Y, CEILING_Z + FLOOR_THICK / 2.0))

# 4 paredes perimetrales, sin aberturas (se accede solo por la compuerta
# desde arriba; ARC-LIB-003, la puerta metalica pesada, se colocara mas
# adelante como division interna, no como salida hacia el exterior)
add_box("Wall_Front", ROOM_W, WALL_THICK, ROOM_H,
        (CENTER_X, CENTER_Y - half_d + WALL_THICK / 2.0, wall_center_z))
add_box("Wall_Back", ROOM_W, WALL_THICK, ROOM_H,
        (CENTER_X, CENTER_Y + half_d - WALL_THICK / 2.0, wall_center_z))
add_box("Wall_Left", WALL_THICK, ROOM_D, ROOM_H,
        (CENTER_X - half_w + WALL_THICK / 2.0, CENTER_Y, wall_center_z))
add_box("Wall_Right", WALL_THICK, ROOM_D, ROOM_H,
        (CENTER_X + half_w - WALL_THICK / 2.0, CENTER_Y, wall_center_z))

# marcador de referencia (no se exporta, solo guia visual): posicion
# aproximada de la compuerta, dentro de la Coleccion Restringida (X=2, Y=32)
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(2.0, 32.0, CEILING_Z))
hatch_marker = bpy.context.active_object
hatch_marker.name = "REF_HatchPosition_DoNotExport"
hatch_marker.empty_display_size = 0.5

bpy.ops.object.select_all(action='DESELECT')
for p in parts:
    p.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()

mesh_obj = bpy.context.active_object
mesh_obj.name = "SM_Sotano1Blockout_Library_A"
mesh_obj.data.name = "SM_Sotano1Blockout_Library_A_Mesh"

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
bpy.ops.object.mode_set(mode='OBJECT')

mat_floor = bpy.data.materials.new(name="M_Floor_Sotano1Blockout")
mat_floor.use_nodes = True
bsdf_f = mat_floor.node_tree.nodes.get("Principled BSDF")
if bsdf_f:
    bsdf_f.inputs["Base Color"].default_value = (0.30, 0.29, 0.28, 1.0)  # concreto oscuro
    bsdf_f.inputs["Roughness"].default_value = 0.85

mat_wall = bpy.data.materials.new(name="M_Wall_Sotano1Blockout")
mat_wall.use_nodes = True
bsdf_w = mat_wall.node_tree.nodes.get("Principled BSDF")
if bsdf_w:
    bsdf_w.inputs["Base Color"].default_value = (0.35, 0.33, 0.31, 1.0)  # concreto/mamposteria
    bsdf_w.inputs["Roughness"].default_value = 0.9

mesh_obj.data.materials.clear()
mesh_obj.data.materials.append(mat_floor)
mesh_obj.data.materials.append(mat_wall)

mesh = mesh_obj.data
wall_idx = 1
for poly in mesh.polygons:
    coords = [mesh.vertices[v].co for v in poly.vertices]
    cz = sum(c.z for c in coords) / len(coords)
    if cz > floor_center_z + FLOOR_THICK:
        poly.material_index = wall_idx

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(CENTER_X, CENTER_Y, floor_center_z))
col_floor = bpy.context.active_object
col_floor.name = "UCX_SM_Sotano1Blockout_Library_A_00"
col_floor.scale = (ROOM_W, ROOM_D, FLOOR_THICK)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
col_floor.display_type = 'WIRE'
col_floor.hide_render = True

bpy.ops.wm.save_as_mainfile(
    filepath="C:\\Users\\jeffa\\Desktop\\Proyecto\\Modelos-3D\\Biblioteca\\SM_Sotano1Blockout_Library_A.blend")

print("RESULT_NAME:", mesh_obj.name)
print("RESULT_DIMS: X={:.3f} Y={:.3f} Z={:.3f}".format(*mesh_obj.dimensions))
print("RESULT_FLOOR_TOP_Z:", floor_top_z)
