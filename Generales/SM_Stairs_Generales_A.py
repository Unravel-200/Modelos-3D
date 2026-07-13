import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
scene.unit_settings.length_unit = 'METERS'

# Escalera principal de Estudios Generales, en forma de U (dos tramos con
# descanso en el medio), sube una altura de piso completa (4.5 m).
# v2: escalones tipo losa (no macizos) sobre zancas delgadas, para que el
# espacio de abajo quede transitable, no cerrado.
# Dimensiones segun Guia_Dimensiones_Blender_Unreal_Proyecto_Memoria.txt,
# seccion 5: ancho 2.20 m, huella 0.30 m, contrahuella ~0.17 m,
# descanso 2.20 x 2.20 m, baranda 1.05-1.10 m.

FLOOR_HEIGHT = 4.5
FLIGHT_WIDTH = 2.20
N_STEPS_PER_FLIGHT = 13
STEP_RISE = FLOOR_HEIGHT / (N_STEPS_PER_FLIGHT * 2)
STEP_RUN = 0.30
TREAD_THICK = 0.05
LANDING_DEPTH = 2.20
LANDING_THICK = 0.20
GAP_BETWEEN_FLIGHTS = 0.20
RAIL_H = 1.08
RAIL_THICK = 0.06
STRINGER_THICK = 0.06

parts = []

def add_box(name, size_x, size_y, size_z, loc):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (size_x, size_y, size_z)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    parts.append(obj)
    return obj

# --- tramo 1: escalones tipo losa (solo la huella, no macizos) ---
flight1_x0 = 0.0
for i in range(N_STEPS_PER_FLIGHT):
    step_top_z = STEP_RISE * (i + 1)
    step_y0 = STEP_RUN * i
    add_box("Step1_{:02d}".format(i), FLIGHT_WIDTH, STEP_RUN, TREAD_THICK,
            (flight1_x0 + FLIGHT_WIDTH / 2.0, step_y0 + STEP_RUN / 2.0, step_top_z - TREAD_THICK / 2.0))

flight1_top_y = STEP_RUN * N_STEPS_PER_FLIGHT
flight1_top_z = STEP_RISE * N_STEPS_PER_FLIGHT

# zancas delgadas (soporte) bajo el borde exterior de cada escalon del
# tramo 1, en vez de una viga diagonal continua (mas simple y sin riesgo
# de error de rotacion)
for i in range(N_STEPS_PER_FLIGHT):
    step_top_z = STEP_RISE * (i + 1)
    step_y0 = STEP_RUN * i
    support_h = step_top_z - TREAD_THICK
    if support_h > 0.02:
        for side, x in (("L", flight1_x0 + STRINGER_THICK / 2.0),
                        ("R", flight1_x0 + FLIGHT_WIDTH - STRINGER_THICK / 2.0)):
            add_box("Support1_{:02d}_{}".format(i, side), STRINGER_THICK, STEP_RUN * 0.8, support_h,
                    (x, step_y0 + STEP_RUN / 2.0, support_h / 2.0))

# --- descanso: losa delgada (no bloque macizo hasta el piso) ---
landing_x0 = flight1_x0
landing_x1 = flight1_x0 + FLIGHT_WIDTH + GAP_BETWEEN_FLIGHTS + FLIGHT_WIDTH
landing_w = landing_x1 - landing_x0
add_box("Landing", landing_w, LANDING_DEPTH, LANDING_THICK,
        (landing_x0 + landing_w / 2.0, flight1_top_y + LANDING_DEPTH / 2.0,
         flight1_top_z - LANDING_THICK / 2.0))

# columnas delgadas de soporte del descanso (4 puntos, no relleno)
for cx in (landing_x0 + 0.15, landing_x1 - 0.15):
    for cy in (flight1_top_y + 0.15, flight1_top_y + LANDING_DEPTH - 0.15):
        add_box("LandingSupport", 0.12, 0.12, flight1_top_z - LANDING_THICK,
                (cx, cy, (flight1_top_z - LANDING_THICK) / 2.0))

landing_top_y = flight1_top_y + LANDING_DEPTH

# --- tramo 2: escalones tipo losa, arranca en el mismo borde donde
# termina el tramo 1 (Y=flight1_top_y), baja en -Y mientras sube en Z ---
flight2_x0 = flight1_x0 + FLIGHT_WIDTH + GAP_BETWEEN_FLIGHTS
for i in range(N_STEPS_PER_FLIGHT):
    step_top_z = flight1_top_z + STEP_RISE * (i + 1)
    step_y0 = flight1_top_y - STEP_RUN * (i + 1)
    add_box("Step2_{:02d}".format(i), FLIGHT_WIDTH, STEP_RUN, TREAD_THICK,
            (flight2_x0 + FLIGHT_WIDTH / 2.0, step_y0 + STEP_RUN / 2.0, step_top_z - TREAD_THICK / 2.0))

total_height = flight1_top_z + STEP_RISE * N_STEPS_PER_FLIGHT  # = FLOOR_HEIGHT

for i in range(N_STEPS_PER_FLIGHT):
    step_top_z = flight1_top_z + STEP_RISE * (i + 1)
    step_y0 = flight1_top_y - STEP_RUN * (i + 1)
    support_h = step_top_z - TREAD_THICK - flight1_top_z
    if support_h > 0.02:
        for side, x in (("L", flight2_x0 + STRINGER_THICK / 2.0),
                        ("R", flight2_x0 + FLIGHT_WIDTH - STRINGER_THICK / 2.0)):
            add_box("Support2_{:02d}_{}".format(i, side), STRINGER_THICK, STEP_RUN * 0.8, support_h,
                    (x, step_y0 + STEP_RUN / 2.0, flight1_top_z + support_h / 2.0))

# --- barandas ---
add_box("Rail_Flight1_Outer", RAIL_THICK, flight1_top_y, RAIL_H,
        (flight1_x0 - RAIL_THICK / 2.0, flight1_top_y / 2.0, flight1_top_z / 2.0 + RAIL_H / 2.0))
add_box("Rail_Flight2_Outer", RAIL_THICK, flight1_top_y, RAIL_H,
        (flight2_x0 + FLIGHT_WIDTH + RAIL_THICK / 2.0, flight1_top_y / 2.0,
         (flight1_top_z + total_height) / 2.0 + RAIL_H / 2.0))
add_box("Rail_Landing_Outer", landing_w, RAIL_THICK, RAIL_H,
        (landing_x0 + landing_w / 2.0, landing_top_y + RAIL_THICK / 2.0,
         flight1_top_z + RAIL_H / 2.0))
add_box("Rail_Center", RAIL_THICK, LANDING_DEPTH, RAIL_H,
        ((flight1_x0 + FLIGHT_WIDTH + flight2_x0) / 2.0, flight1_top_y / 2.0,
         flight1_top_z / 2.0 + RAIL_H / 2.0))

bpy.ops.object.select_all(action='DESELECT')
for p in parts:
    p.select_set(True)
bpy.context.view_layer.objects.active = parts[0]
bpy.ops.object.join()

mesh_obj = bpy.context.active_object
mesh_obj.name = "SM_Stairs_Generales_A"
mesh_obj.data.name = "SM_Stairs_Generales_A_Mesh"

bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
bpy.ops.object.mode_set(mode='OBJECT')

mat = bpy.data.materials.new(name="M_Concrete_Stairs")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.60, 0.58, 0.55, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.7
mesh_obj.data.materials.clear()
mesh_obj.data.materials.append(mat)

# colision: solo cascaras delgadas por escalon serian ideales, pero para
# blockout basta con una caja por tramo mas la losa del descanso (deja
# libre el espacio por debajo, a diferencia de v1)
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(flight1_x0 + FLIGHT_WIDTH / 2.0,
                                                      flight1_top_y / 2.0, flight1_top_z / 2.0))
col1 = bpy.context.active_object
col1.name = "UCX_SM_Stairs_Generales_A_00"
col1.scale = (FLIGHT_WIDTH, flight1_top_y, flight1_top_z)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
col1.display_type = 'WIRE'
col1.hide_render = True

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(flight2_x0 + FLIGHT_WIDTH / 2.0,
                                                      flight1_top_y / 2.0,
                                                      (flight1_top_z + total_height) / 2.0))
col2 = bpy.context.active_object
col2.name = "UCX_SM_Stairs_Generales_A_01"
col2.scale = (FLIGHT_WIDTH, flight1_top_y, total_height - flight1_top_z)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
col2.display_type = 'WIRE'
col2.hide_render = True

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(landing_x0 + landing_w / 2.0,
                                                      flight1_top_y + LANDING_DEPTH / 2.0,
                                                      flight1_top_z - LANDING_THICK / 2.0))
col3 = bpy.context.active_object
col3.name = "UCX_SM_Stairs_Generales_A_02"
col3.scale = (landing_w, LANDING_DEPTH, LANDING_THICK)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
col3.display_type = 'WIRE'
col3.hide_render = True

bpy.ops.wm.save_as_mainfile(
    filepath="C:\\Users\\jeffa\\Desktop\\Proyecto\\Modelos-3D\\Generales\\SM_Stairs_Generales_A.blend")

print("RESULT_NAME:", mesh_obj.name)
print("RESULT_DIMS: X={:.3f} Y={:.3f} Z={:.3f}".format(*mesh_obj.dimensions))
print("RESULT_TOTAL_HEIGHT:", total_height)
