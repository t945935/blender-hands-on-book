"""Original reading corner; run using Blender --background --python this.py -- build|native|glb OUTPUT_DIR."""
import bpy, bmesh, json, sys
from pathlib import Path
from mathutils import Vector
args = sys.argv[sys.argv.index('--') + 1:]
MODE, ROOT = args[0], Path(args[1])
if MODE == 'build' and ROOT.exists() and any(ROOT.iterdir()):
    raise SystemExit('Build requires a new or empty output directory; do not overwrite reader examples.')
ROOT.mkdir(parents=True, exist_ok=True)
EXPORT_NAMES = ['Tray','Divider_01','Divider_02','Book_Cover','Book_Pages','Desk','Accent_Block']

def write(name, data):
    (ROOT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def bounds(obj):
    ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = ev.to_mesh()
    points = [ev.matrix_world @ v.co for v in mesh.vertices]
    result = [[min(p[i] for p in points) for i in range(3)], [max(p[i] for p in points) for i in range(3)]]
    ev.to_mesh_clear()
    return result

def material(name, color, roughness):
    m = bpy.data.materials.new(name); m.diffuse_color = (*color, 1); m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*color,1); p.inputs['Roughness'].default_value = roughness
    return m

def bevel(obj, amount):
    mod = obj.modifiers.new('Edge_Softness','BEVEL'); mod.width=amount; mod.segments=3
    return mod

def box(name, size, pos, mat, edge=.001, bottom_origin=False):
    bpy.ops.mesh.primitive_cube_add(size=1, location=pos)
    o=bpy.context.object; o.name=name
    for v in o.data.vertices:
        v.co=Vector((v.co.x*size[0],v.co.y*size[1],(v.co.z+(.5 if bottom_origin else 0))*size[2]))
    o.data.materials.append(mat)
    if edge: bevel(o,edge)
    return o

def camera(name, pos, target, scale):
    bpy.ops.object.camera_add(location=pos); o=bpy.context.object; o.name=name
    o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    o.data.type='ORTHO'; o.data.ortho_scale=scale; o.data.clip_start=.01; o.data.clip_end=100
    return o

def build():
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    s=bpy.context.scene; s.unit_settings.system='METRIC'; s.unit_settings.scale_length=1; s.unit_settings.length_unit='METERS'
    teal=material('Tray_Teal',(.025,.29,.27),.32)
    cream=material('Paper_Warm',(.83,.77,.63),.8)
    orange=material('Book_Terracotta',(.46,.12,.065),.5)
    deskmat=material('Desk_Sand',(.49,.37,.245),.65)
    accentmat=material('Accent_Mustard',(.8,.43,.07),.42)
    bg=material('Backdrop_Neutral',(.29,.31,.32),.9)
    vertices=[(-.18,-.12,.006),(.18,-.12,.006),(.18,.12,.006),(-.18,.12,.006),(-.18,-.12,.08),(.18,-.12,.08),(.18,.12,.08),(-.18,.12,.08)]
    faces=[(0,1,2,3),(1,0,4,5),(2,1,5,6),(3,2,6,7),(0,3,7,4)]
    mesh=bpy.data.meshes.new('Tray_ConnectedSurface'); mesh.from_pydata(vertices,[],faces); mesh.update()
    tray=bpy.data.objects.new('Tray',mesh); s.collection.objects.link(tray); tray.location=(-.15,.035,0); tray.data.materials.append(teal)
    mod=tray.modifiers.new('Wall_Thickness','SOLIDIFY'); mod.thickness=.006; mod.offset=-1; mod.use_even_offset=True; mod.use_rim=True
    bevel(tray,.0015)
    for i,x in enumerate([-.21,-.09],1): box('Divider_%02d'%i,(.005,.234,.052),(x,.035,.032),teal,.001)
    # One mesh with three connected-volume components: lower cover, upper cover, spine.
    coverparts=[box('CoverBottom',(.212,.282,.003),(.19,.02,.0015),orange,0),box('CoverTop',(.212,.282,.003),(.19,.02,.0335),orange,0),box('CoverSpine',(.004,.282,.029),(.086,.02,.0175),orange,0)]
    bpy.ops.object.select_all(action='DESELECT')
    for o in coverparts: o.select_set(True)
    bpy.context.view_layer.objects.active=coverparts[0]; bpy.ops.object.join(); bpy.context.object.name='Book_Cover'; bevel(bpy.context.object,.0008)
    box('Book_Pages',(.199,.269,.029),(.1935,.02,.0175),cream,.0005)
    box('Accent_Block',(.045,.035,.03),(.15,-.205,0),accentmat,.002,bottom_origin=True)
    box('Desk',(.9,.7,.05),(0,0,-.025),deskmat,.012)
    box('Backdrop',(200,200,.01),(0,0,-.062),bg,0)
    hero=camera('Camera_Hero',(.95,-1.3,1.25),(0,0,.005),1.22)
    camera('Camera_Front',(0,-1.5,.48),(0,0,.025),1.08)
    camera('Camera_Top',(0,0,2),(0,0,0),1.02)
    for name,pos,power,size in [('Key',(-.5,-.5,1.6),110,1.1),('Fill',(1,.3,1),65,1.0)]:
        bpy.ops.object.light_add(type='AREA',location=pos); o=bpy.context.object; o.name=name; o.data.energy=power; o.data.shape='DISK'; o.data.size=size; o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
    s.world.color=(.22,.22,.22); s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=32; s.cycles.use_denoising=True
    s.render.resolution_x=1000; s.render.resolution_y=1000; s.render.resolution_percentage=100
    s.render.image_settings.file_format='PNG'; s.view_settings.view_transform='AgX'
    s.camera=hero
    s.transform_orientation_slots[0].type='GLOBAL'; s.tool_settings.transform_pivot_point='MEDIAN_POINT'; s.tool_settings.use_proportional_edit_objects=False
    bpy.ops.object.select_all(action='DESELECT'); accent=bpy.data.objects['Accent_Block']; accent.select_set(True); bpy.context.view_layer.objects.active=accent
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D': area.spaces.active.region_3d.view_perspective='CAMERA'
    s.render.filepath=str(ROOT/'hero.png')
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'reading-corner.blend'))
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'chapter01-start.blend'))
    bpy.ops.object.select_all(action='DESELECT')
    for name in EXPORT_NAMES: bpy.data.objects[name].select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(ROOT/'reading-corner.glb'),export_format='GLB',use_selection=True,export_apply=True,export_cameras=False,export_lights=False)
    write('export-reference.json',{'names':EXPORT_NAMES,'bounds':{n:bounds(bpy.data.objects[n]) for n in EXPORT_NAMES},'version':bpy.app.version_string,'export_apply':True})
    for view in ['Hero','Front','Top']:
        s.camera=bpy.data.objects['Camera_'+view]; s.render.filepath=str(ROOT/(view.lower()+'.png')); bpy.ops.render.render(write_still=True)
    write('build-result.json',{'status':'passed','version':bpy.app.version_string,'engine':'CYCLES','device':'CPU','samples':32,'resolution':[1000,1000],'renders':['hero.png','front.png','top.png']})

def native():
    results=[]
    for file in ['reading-corner.blend','chapter01-start.blend']:
        bpy.ops.wm.open_mainfile(filepath=str(ROOT/file)); s=bpy.context.scene
        assert all(n in bpy.data.objects for n in EXPORT_NAMES+['Camera_Hero'])
        assert s.camera.name=='Camera_Hero' and bpy.context.mode=='OBJECT'
        assert bpy.context.view_layer.objects.active.name=='Accent_Block'
        assert [o.name for o in bpy.context.selected_objects]==['Accent_Block']
        assert s.unit_settings.system=='METRIC' and s.unit_settings.scale_length==1
        assert s.transform_orientation_slots[0].type=='GLOBAL'
        assert s.tool_settings.transform_pivot_point=='MEDIAN_POINT' and not s.tool_settings.use_proportional_edit_objects
        assert all(a.spaces.active.region_3d.view_perspective=='CAMERA' for sc in bpy.data.screens for a in sc.areas if a.type=='VIEW_3D')
        tray=bpy.data.objects['Tray']; assert len(tray.data.vertices)==8 and len(tray.data.polygons)==5
        assert [m.type for m in tray.modifiers]==['SOLIDIFY','BEVEL']
        solid=tray.modifiers[0]; assert abs(solid.thickness-.006)<1e-7 and solid.offset==-1 and solid.use_even_offset and solid.use_rim
        expected=[(0,0,1),(0,1,0),(-1,0,0),(0,-1,0),(1,0,0)]
        for p,n in zip(tray.data.polygons,expected): assert p.normal.dot(Vector(n))>.999
        bm=bmesh.new(); bm.from_mesh(tray.data); assert sum(e.is_boundary for e in bm.edges)==4
        bm.verts.ensure_lookup_table()
        reached={bm.verts[0]}; todo=list(reached)
        while todo:
            v=todo.pop()
            for e in v.link_edges:
                w=e.other_vert(v)
                if w not in reached: reached.add(w); todo.append(w)
        assert len(reached)==8; bm.free()
        ev=tray.evaluated_get(bpy.context.evaluated_depsgraph_get()); em=ev.to_mesh(); bm=bmesh.new(); bm.from_mesh(em)
        assert all(e.is_manifold for e in bm.edges); volume=bm.calc_volume(signed=True); assert volume>0; bm.free(); ev.to_mesh_clear()
        tb=bounds(tray); assert abs(tb[0][2])<1e-6 and abs(tb[1][2]-.08)<1e-6
        a=bpy.data.objects['Accent_Block']; assert all(abs(x-1)<1e-7 for x in a.scale)
        before=bounds(a); a.location.x+=.02; a.scale=(1.15,)*3; bpy.context.view_layer.update(); after=bounds(a)
        assert abs(after[0][2])<1e-6
        for n in ['Tray','Book_Cover','Book_Pages']:
            other=bounds(bpy.data.objects[n]); assert any(after[1][i]<other[0][i] or after[0][i]>other[1][i] for i in [0,1])
        db=bounds(bpy.data.objects['Desk']); assert all(after[0][i]>db[0][i] and after[1][i]<db[1][i] for i in [0,1])
        assert not [im.name for im in bpy.data.images if im.source=='FILE']
        results.append({'file':file,'active':'Accent_Block','mode':'OBJECT','hero_camera':True,'tray_surface_connected':True,'tray_normals':'inward walls, upward floor; negative offset adds thickness outward/down','evaluated_closed_manifold':True,'signed_volume_m3':volume,'tray_bounds_m':tb,'exercise_bounds_before_m':before,'exercise_bounds_after_m':after,'exercise_safe':True})
    write('native-check.json',{'status':'passed','checks':results})

def glb():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(ROOT/'reading-corner.glb'))
    meshes={o.name:o for o in bpy.context.scene.objects if o.type=='MESH'}
    ref=json.loads((ROOT/'export-reference.json').read_text(encoding='utf-8'))
    assert set(meshes)==set(ref['names']),list(meshes)
    deltas={n:max(abs(bounds(o)[j][i]-ref['bounds'][n][j][i]) for j in range(2) for i in range(3)) for n,o in meshes.items()}
    assert max(deltas.values())<1e-5,deltas
    write('glb-check.json',{'status':'passed','names':sorted(meshes),'tolerance_m':1e-5,'max_bound_deltas_m':deltas,'bounds_m':{n:bounds(o) for n,o in meshes.items()},'vertex_count_equality_required':False})

if MODE=='build': build()
elif MODE=='native': native()
elif MODE=='glb': glb()
else: raise ValueError(MODE)
print('PROTOTYPE_PASS',MODE)
