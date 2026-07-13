import bpy

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
scene.unit_settings.length_unit = 'METERS'

# Piso base de la Plaza Central: 45 x 45 m
# (Proyecto_Memoria_Definitivo_3_Dias_Terror_Intenso.txt, seccion 8.1)
# Solo geometria plana con material PROVISIONAL. El pavimento definitivo
# sera un material compartido para todo el campus (calles, aceras,
# plazas), a definir en una pasada aparte, no especifico de esta plaza.

PLAZA_SIZE = 45.0
FLOOR_THICK = 0.15

bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, -FLOOR_THICK / 2.0))
floor_obj = bpy.context.active_object
floor_obj.name = "SM_PlazaFloorBlockout_A"
floor_obj.scale = (PLAZA_SIZE, PLAZA_SIZE, FLOOR_THICK)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
floor_obj.data.name = "SM_PlazaFloorBlockout_A_Mesh"

bpy.context.scene.cursor.location = (0.0, 0.0, 0.0)
bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
bpy.ops.object.mode_set(mode='OBJECT')

mat = bpy.data.materials.new(name="M_PLACEHOLDER_Pavement")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs["Base Color"].default_value = (0.45, 0.44, 0.42, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.8
floor_obj.data.materials.clear()
floor_obj.data.materials.append(mat)

bpy.ops.wm.save_as_mainfile(
    filepath="C:\\Users\\jeffa\\Desktop\\Proyecto\\Modelos-3D\\Plaza\\SM_PlazaFloorBlockout_A.blend")

print("RESULT_NAME:", floor_obj.name)
print("RESULT_DIMS: X={:.3f} Y={:.3f} Z={:.3f}".format(*floor_obj.dimensions))
