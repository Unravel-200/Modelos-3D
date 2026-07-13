import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
scene.unit_settings.length_unit = 'METERS'

# Fuente central de la Plaza: 20 m de diametro
# (Proyecto_Memoria_Definitivo_3_Dias_Terror_Intenso.txt, seccion 8.1)
# Profundidad visual: 0.40-0.60 m.
#
# VERSION FINAL DE BLOCKOUT (Fase 1): solo borde + piso + agua, sin
# nada en el centro. El usuario probo varias ideas de escultura central
# (angeles, figura con libro, manos con antorcha, columnas rotas, version
# de 3 niveles con corona) y ninguna convencio como blockout generado por
# script. Se decidio dejar el centro vacio por ahora.
#
# PENDIENTE: agregar detalle/escultura a la fuente en la fase de arte
# final (v0.18.0). Ver Checklist_Versiones, version 0.18.0.

OUTER_RADIUS = 10.0
RIM_THICK = 0.4
INNER_RADIUS = OUTER_RADIUS - RIM_THICK
RIM_HEIGHT = 0.5
WATER_DEPTH = 0.5

bpy.ops.mesh.primitive_cylinder_add(radius=OUTER_RADIUS, depth=RIM_HEIGHT,
                                     location=(0.0, 0.0, RIM_HEIGHT / 2.0), vertices=64)
rim_outer = bpy.context.active_object
rim_outer.name = "RimOuter"

bpy.ops.mesh.primitive_cylinder_add(radius=INNER_RADIUS, depth=RIM_HEIGHT + 0.2,
                                     location=(0.0, 0.0, RIM_HEIGHT / 2.0), vertices=64)
rim_cutter = bpy.context.active_object
rim_cutter.name = "RimCutter"

bool_mod = rim_outer.modifiers.new(name="Boolean", type='BOOLEAN')
bool_mod.operation = 'DIFFERENCE'
bool_mod.object = rim_cutter
bpy.context.view_layer.objects.active = rim_outer
bpy.ops.object.modifier_apply(modifier="Boolean")

bpy.ops.object.select_all(action='DESELECT')
rim_cutter.select_set(True)
bpy.ops.object.delete()

bpy.ops.mesh.primitive_cylinder_add(radius=INNER_RADIUS, depth=0.1,
                                     location=(0.0, 0.0, 0.05), vertices=64)
basin_floor = bpy.context.active_object
basin_floor.name = "BasinFloor"

bpy.ops.object.select_all(action='DESELECT')
rim_outer.select_set(True)
basin_floor.select_set(True)
bpy.context.view_layer.objects.active = rim_outer
bpy.ops.object.join()

mesh_obj = bpy.context.active_object
mesh_obj.name = "SM_Fountain_PlazaCentral_A"
mesh_obj.data.name = "SM_Fountain_PlazaCentral_A_Mesh"

bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
bpy.ops.object.mode_set(mode='OBJECT')

mat_stone = bpy.data.materials.new(name="M_Stone_FountainRim")
mat_stone.use_nodes = True
bsdf_s = mat_stone.node_tree.nodes.get("Principled BSDF")
if bsdf_s:
    bsdf_s.inputs["Base Color"].default_value = (0.62, 0.60, 0.56, 1.0)
    bsdf_s.inputs["Roughness"].default_value = 0.75
mesh_obj.data.materials.clear()
mesh_obj.data.materials.append(mat_stone)

water_z = RIM_HEIGHT - WATER_DEPTH
bpy.ops.mesh.primitive_cylinder_add(radius=INNER_RADIUS, depth=0.05,
                                     location=(0.0, 0.0, water_z), vertices=64)
water_obj = bpy.context.active_object
water_obj.name = "WaterSurface"

mat_water = bpy.data.materials.new(name="M_Water_FountainSurface")
mat_water.use_nodes = True
bsdf_w = mat_water.node_tree.nodes.get("Principled BSDF")
if bsdf_w:
    bsdf_w.inputs["Base Color"].default_value = (0.15, 0.35, 0.45, 1.0)
    bsdf_w.inputs["Roughness"].default_value = 0.05
    bsdf_w.inputs["Transmission Weight"].default_value = 0.7
water_obj.data.materials.clear()
water_obj.data.materials.append(mat_water)

bpy.ops.object.select_all(action='DESELECT')
mesh_obj.select_set(True)
water_obj.select_set(True)
bpy.context.view_layer.objects.active = mesh_obj
bpy.ops.object.join()

final_obj = bpy.context.active_object
final_obj.name = "SM_Fountain_PlazaCentral_A"
final_obj.data.name = "SM_Fountain_PlazaCentral_A_Mesh"

bpy.ops.mesh.primitive_cylinder_add(radius=OUTER_RADIUS, depth=RIM_HEIGHT,
                                     location=(0.0, 0.0, RIM_HEIGHT / 2.0), vertices=24)
collision_obj = bpy.context.active_object
collision_obj.name = "UCX_SM_Fountain_PlazaCentral_A_00"
collision_obj.display_type = 'WIRE'
collision_obj.hide_render = True

bpy.ops.wm.save_as_mainfile(
    filepath="C:\\Users\\jeffa\\Desktop\\Proyecto\\Modelos-3D\\Plaza\\SM_Fountain_PlazaCentral_A.blend")

print("RESULT_NAME:", final_obj.name)
print("RESULT_DIMS: X={:.3f} Y={:.3f} Z={:.3f}".format(*final_obj.dimensions))
