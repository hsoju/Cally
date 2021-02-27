import bmesh
from xml.etree import ElementTree as et
from .prettify import pretty_print
from ..xmesh.xvert import XVertex
from ..xmesh.xface import XFace
from ..xmesh.xmap import WeightMap


def generate_vertices(obj, submap: dict, weight: str) -> list:
    """Constructs vertices with each representing an xmf vertex tag.

    Args:
        obj (): A bpy mesh object containing geometric data.
        submap (dict): A dictionary mapping each submesh to its corresponding bone and material ids.
        weight (str): A string determining bone weight assignment for all vertices.

    Returns:
        A list of vertex objects.

    """
    xverts = []

    groups = {g.index: WeightMap.lookup(g.name) for g in obj.vertex_groups}

    xcol = ['1', '1', '1']
    bone_id = submap[obj.name][1]
    xinfls = {bone_id: 1}

    if weight == 'MANUAL':
        for v in obj.data.vertices:
            coords = obj.matrix_world @ v.co
            xcoords = [coords[0], coords[1], coords[2]]
            xnorms = [v.normal[0], v.normal[1], v.normal[2]]
            next_vert = XVertex(xcoords, xnorms, xcol, xinfls)
            xverts.append(next_vert)
    else:
        for v in obj.data.vertices:
            coords = obj.matrix_world @ v.co
            xcoords = [coords[0], coords[1], coords[2]]
            xnorms = [v.normal[0], v.normal[1], v.normal[2]]
            if len(v.groups) != 0:
                xinfls = {}
                for g in v.groups:
                    xinfls[str(groups[g.group])] = g.weight
            next_vert = XVertex(xcoords, xnorms, xcol, xinfls)
            xverts.append(next_vert)
    return xverts


def generate_faces(obj, verts: list) -> list:
    """Constructs faces with each representing an xmf face tag.

    Args:
        obj (): A bpy mesh object containing geometric data.
        verts (list): A list of vertex objects.

    Returns:
        A list of face objects.

    """
    xfaces = []

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method='BEAUTY', ngon_method='BEAUTY')
    uv_layer = bm.loops.layers.uv.active

    for face in bm.faces:
        next_face = XFace()
        for v, l in zip(face.verts, face.loops):
            v_idx = v.index
            uv_coords = l[uv_layer].uv
            next_uv = [uv_coords[0], uv_coords[1]]
            if next_uv in verts[v_idx].uv:
                next_face.ix.append([v_idx, verts[v_idx].uv.index(next_uv)])
            else:
                next_face.ix.append([v_idx, len(verts[v_idx].uv)])
                verts[v_idx].uv.append(next_uv)
        xfaces.append(next_face)

    bm.free()
    return xfaces


def create_submesh(name: str, submap: dict, faces: list) -> et.Element:
    """Generates a submesh xmf tag.

    Args:
        name (str): A string referring to the name of the submesh.
        submap (dict): A dictionary mapping each submesh to its corresponding bone and material ids.
        faces (list): A list of face objects.

    Returns:
        An xml Element representing a single submesh.

    """
    sub = et.Element('submesh')
    sub.attrib['numfaces'] = str(len(faces))
    sub.attrib['numlodsteps'] = '0'
    sub.attrib['numsprings'] = '0'
    sub.attrib['nummorphs'] = '0'
    sub.attrib['numtexcoords'] = '1'
    sub.attrib['material'] = str(submap[name][2])
    return sub


def fill_submesh(sub: et.Element, verts: list, faces: list, scale: float):
    """Places xmf tags for vertices and faces into a submesh xmf tag.

    Args:
        sub (et.Element): An xml Element for a single submesh.
        verts (list): A list of vertex objects.
        faces (list): A list of face objects.
        scale (float): A float determining scaling factor for mesh on export.
    """
    v_id = 0
    v_ids = []
    for x in range(0, len(verts)):
        v_ids.append([])
        for y in range(0, len(verts[x].uv)):
            elem_vert = verts[x].parse(v_id, y, scale)
            sub.append(elem_vert)
            v_ids[x].append(v_id)
            v_id += 1
    sub.attrib['numvertices'] = str(v_id)
    for face in faces:
        elem_face = face.parse(v_ids)
        sub.append(elem_face)


def export_xmf(context, filepath: str, submap: dict,
               scale: float, weight: str, pretty: bool):
    """Writes a new xmf file containing the selected meshes geometric data.

    Args:
        context (): A bpy context containing data in the current 3d view.
        filepath (str): A string pointing to the output location of the xmf file.
        submap (dict): A dictionary mapping each submesh to its corresponding bone and material ids.
        scale (float): A float determining scaling factor for mesh on export.
        weight (str): A string determining bone weight assignment for all vertices.
        pretty (bool): A boolean determining whether xmf file should be formatted.
    """
    objs = [obj for obj in context.selected_objects if obj.type == 'MESH']

    root = et.Element('mesh')
    root.attrib['numsubmesh'] = str(len(objs))

    for obj in objs:
        xverts = generate_vertices(obj, submap, weight)
        xfaces = generate_faces(obj, xverts)

        sub = create_submesh(obj.name, submap, xfaces)
        fill_submesh(sub, xverts, xfaces, scale)
        root.append(et.Comment(obj.name))
        root.append(sub)

    xtext = et.tostring(root).decode('utf8')
    xtext = pretty_print(xtext) if pretty else xtext

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("<HEADER MAGIC=\"XMF\" VERSION=\"919\"/>")
        f.write("%s" % xtext)


# TODO Finish this
def import_xmf(context, filepath: str):
    """Parses an xmf file into meshes.

    Args:
        context (): A bpy context containing data in the current 3d view.
        filepath (str): A string specifying the file path of the xml object.
    """
    mesh = []
    with open(filepath, 'r') as f:
        pass
    pass
