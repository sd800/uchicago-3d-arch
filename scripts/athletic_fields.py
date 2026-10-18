"""Bounded Stagg Field refinement from mapped pitches and university aerials.

Eight lanes, eight tennis courts plus two practice halves, and opposed ball
infields are source-backed. Small fittings and unmapped soccer lines are photo
interpretations, not surveyed geometry. All objects use the landscape layer.
"""
import math
import numpy as np
from shapely.geometry import Point, Polygon, LineString, box
from shapely.ops import unary_union
from shapely import affinity

REGION = box(78, 1242, 380, 1427)
REFERENCE = 'https://athletics.uchicago.edu/sports/2023/6/12/facilities-athletic-fields.aspx'


def local(g, center, east, north):
    return affinity.affine_transform(g, [east[0], north[0], east[1], north[1], *center])


def layout(ctx):
    center = np.array([189.55, 1336.60])
    east = np.array([1., .0105]); east /= np.linalg.norm(east)
    north = np.array([-east[1], east[0]])
    spine = LineString([(0, -37.4), (0, 37.4)])
    inner = spine.buffer(39.55, quad_segs=40)
    outer = spine.buffer(39.55 + 8 * 1.22, quad_segs=40)
    # Retain the mapped western sprint extension and keep real paths/buildings clear.
    chute = box(-51.2, -60, -39.55, 84)
    mask = unary_union([ctx.footprints, ctx.roadarea, ctx.walkarea, ctx.kerb])
    track = local(outer.difference(inner).union(chute), center, east, north).intersection(ctx.scope).difference(mask)
    playing = [f['poly'].buffer(1) for f in ctx.features if f['tags'].get('leisure') == 'pitch' and REGION.covers(f['poly'].centroid)]
    tree_exclusion = unary_union([local(outer.union(chute), center, east, north), *playing, box(310, 1307, 375, 1410)])
    return {'center': center, 'east': east, 'north': north, 'spine': spine,
            'inner': inner, 'track': track, 'tree_exclusion': tree_exclusion, 'original': next(f['poly'] for f in ctx.features if f['id'] == 2425728)}


def handles(g, tags):
    return tags.get('sport') in ['tennis', 'baseball', 'soccer;american_football'] and REGION.covers(g.representative_point())


def refine(ctx, plan):
    env = ctx.env
    clear = unary_union([ctx.footprints, ctx.roadarea, ctx.walkarea, ctx.kerb])
    stats = {'reference': REFERENCE, 'track_lanes': 8, 'regulation_tennis_courts': 0,
             'practice_half_courts': 0, 'ball_infields': [], 'soccer_pitches': 1,
             'geometry_level': 'optimized outdoor facilities', 'paint_clearance_m': .018}
    before = sum(len(m.faces) for parts in ctx.eg.values() for m in parts)

    def surface(g, material, z=.13, thickness=.035):
        env(g.difference(clear).intersection(ctx.scope), z, thickness, material)

    def paint(g, material='Marking', width=.11):
        if g.geom_type not in ['Polygon', 'MultiPolygon']:
            g = g.buffer(width / 2, cap_style=2, join_style=2)
        surface(g, material, .183, .012)

    def rail(a, b, z, radius=.045, material='Furniture'):
        if np.linalg.norm(np.array(a) - np.array(b)) < .001:
            return
        ctx.eg[material].append(ctx.cylinder((*a, z), (*b, z), radius, 6))

    def post(p, h, radius=.055, material='Furniture'):
        ctx.eg[material].append(ctx.cylinder((*p, .165), (*p, .165 + h), radius, 6))

    def fence(line, height=2.7, spacing=5.5):
        coords = list(line.coords)
        for a, b in zip(coords[:-1], coords[1:]):
            edge = LineString([a, b])
            for distance in np.linspace(0, edge.length, max(2, math.ceil(edge.length / spacing) + 1)):
                q = edge.interpolate(distance); post(q.coords[0], height)
            for z in [.5, 1.45, height + .165]:
                rail(a, b, z, .026)

    def goal(center, east, direction, width=7.32, height=2.44, depth=1.75):
        c = np.asarray(center); east = np.asarray(east); direction = np.asarray(direction)
        a, b = c - east * width / 2, c + east * width / 2
        post(a, height, .07, 'LightStone'); post(b, height, .07, 'LightStone')
        rail(a, b, height + .165, .07, 'LightStone')
        rear = [a - direction * depth, b - direction * depth]
        for p, q in zip([a, b], rear):
            post(q, 1.55, .035)
            ctx.eg['Furniture'].append(ctx.cylinder((*p, height + .165), (*q, 1.715), .027, 6))
            rail(p, q, .23, .026)
        rail(*rear, .23, .026); rail(*rear, 1.715, .026)
        for t in np.linspace(0, 1, 7):
            p = rear[0] * (1 - t) + rear[1] * t
            post(p, 1.55, .013)

    # The inner kerb is 0.30 m inside the standard 400 m lane-one measurement line.
    center, east, north = plan['center'], plan['east'], plan['north']
    project = lambda g: local(g, center, east, north)
    surface(project(plan['inner']), 'Grass')
    track = plan['track']
    for lane in range(9):
        edge = project(plan['spine'].buffer(39.55 + lane * 1.22, quad_segs=40).boundary)
        paint(edge.buffer(.055).intersection(track.buffer(.08)))
    # A clean finish stripe across the straight; avoid fabricated radial webs.
    paint(project(LineString([(39.55, -30), (49.31, -30)])).intersection(track.buffer(.1)), width=.16)
    for lane in range(9):
        x = -51.2 + lane * 1.22
        paint(project(LineString([(x, -57), (x, 82)])).intersection(track), width=.10)

    # Football field uses the existing mapped orientation and regulation proportions.
    raw = next(f['poly'] for f in ctx.features if f['id'] == 182018490)
    fc = np.array(raw.centroid.coords[0]); fe = east; fn = north
    fp = lambda g: local(g, fc, fe, fn)
    fw, fl = 48.768, 109.728
    turf = fp(box(-fw/2, -fl/2, fw/2, fl/2))
    surface(turf, 'FieldTurf')
    for k in range(10):
        if k % 2 == 0:
            surface(fp(box(-fw/2, -45.72+k*9.144, fw/2, -45.72+(k+1)*9.144)), 'FieldStripe', .169, .012)
    paint(turf.boundary, width=.16)
    for y in np.linspace(-45.72, 45.72, 21):
        paint(fp(LineString([(-fw/2, y), (fw/2, y)])), width=.13)
    hashes = []
    for y in np.linspace(-44.8056, 44.8056, 99):
        for x in [-fw/2+.8, -3.2, 3.2, fw/2-.8]:
            hashes.append(fp(LineString([(x-.36, y), (x+.36, y)])).buffer(.055, cap_style=2))
    paint(unary_union(hashes))
    # Source aerial shows goalposts at the north and south end zones.
    for sign in [-1, 1]:
        c = fc + fn * sign * (fl/2+1.0)
        post(c, 3.1, .15, 'GoalPost')
        rail(c-fe*2.82, c+fe*2.82, 3.265, .105, 'GoalPost')
        for p in [c-fe*2.82, c+fe*2.82]:
            ctx.eg['GoalPost'].append(ctx.cylinder((*p, 3.265), (*p, 7.0), .085, 8))
    stats['football_field_m'] = [fw, fl]
    stats['lane_one_length_m'] = round(2*74.8 + 2*math.pi*(39.55+.3), 3)

    # Eight full tennis courts and two practice halves retain their mapped positions.
    courts = [f for f in ctx.features if f['tags'].get('sport') == 'tennis' and REGION.covers(f['poly'].centroid)]
    apron = unary_union([f['poly'].buffer(3.5, join_style=2) for f in courts])
    surface(apron, 'CourtApron', .13, .032)
    for f in courts:
        p = f['poly']; cc = np.array(p.centroid.coords[0])
        coords = np.array(p.minimum_rotated_rectangle.exterior.coords)[:4]
        vectors = np.roll(coords, -1, axis=0) - coords
        v = vectors[np.argmax(np.linalg.norm(vectors, axis=1))]; v /= np.linalg.norm(v)
        if v[1] < 0: v = -v
        u = np.array([v[1], -v[0]])
        half = p.area < 200
        length = 11.885 if half else 23.77
        court = lambda g: local(g, cc, u, v)
        playing = court(box(-5.485, -length/2, 5.485, length/2))
        surface(playing, 'Court', .166, .013)
        lines = [playing.boundary]
        for x in [-4.115, 4.115]:
            lines.append(court(LineString([(x, -length/2), (x, length/2)])))
        if half:
            # Southern practice courts use a northern rebound wall, not a fake mid-court net.
            net_y = length/2
            lines += [court(LineString([(-4.115, net_y-6.4), (4.115, net_y-6.4)])),
                      court(LineString([(0, net_y-6.4), (0, net_y)]))]
            a, b = cc-u*6.1+v*(net_y+1.1), cc+u*6.1+v*(net_y+1.1)
            fence(LineString([a, b]), 2.8, 6.1)
            stats['practice_half_courts'] += 1
        else:
            for y in [-6.4, 6.4]:
                lines.append(court(LineString([(-4.115, y), (4.115, y)])))
            lines.append(court(LineString([(0, -6.4), (0, 6.4)])))
            a, b = cc-u*6.4, cc+u*6.4
            post(a, 1.07, .065); post(b, 1.07, .065)
            for z in [.35, .66, 1.18]: rail(a, b, z, .022)
            for t in np.linspace(0, 1, 9): post(a*(1-t)+b*t, .91, .012)
            stats['regulation_tennis_courts'] += 1
        paint(unary_union([line.buffer(.045, cap_style=2, join_style=2) for line in lines]))
    # Fence only the outer perimeter; leave the east access opening clear.
    fence(LineString([(84.5, 1249), (83.0, 1417), (125.0, 1417), (127.0, 1269)]), 2.9)

    # Baseball NW home faces southeast; softball SE home faces northwest.
    for ident, home, first, third, base_m, radius, kind in [
        (182019200, (250.6, 1408.0), (1, 0), (0, -1), 27.432, 39.5, 'baseball'),
        (1374170524, (365.9, 1268.4), (-1, 0), (0, 1), 18.288, 27.0, 'softball'),
    ]:
        p = next(f['poly'] for f in ctx.features if f['id'] == ident)
        home, a, b = map(np.asarray, [home, first, third])
        surface(p, 'Grass')
        arc = [home+a*radius*math.cos(t)+b*radius*math.sin(t) for t in np.linspace(0, math.pi/2, 40)]
        dirt = Polygon([home, *arc]).intersection(p)
        diamond = Polygon([home, home+a*base_m, home+(a+b)*base_m, home+b*base_m])
        if kind == 'baseball': dirt = dirt.difference(diamond.buffer(-3.0))
        surface(dirt, 'Infield', .17, .012)
        # Mound and batter area join the connected infield rather than float above it.
        mound = home+(a+b)*(18.44/math.sqrt(2) if kind=='baseball' else 13.11/math.sqrt(2))
        surface(Point(mound).buffer(2.6 if kind=='baseball' else 2.0, quad_segs=12), 'Infield', .17, .012)
        for point in [home, home+a*base_m, home+(a+b)*base_m, home+b*base_m]:
            paint(box(point[0]-.24, point[1]-.24, point[0]+.24, point[1]+.24))
        for vec in [a, b]: paint(LineString([home, home+vec*min(radius*2, 100)]).intersection(p), width=.12)
        fence(LineString([home-a*8+b*3, home-a*8-b*5, home+a*3-b*5]), 5.0 if kind=='baseball' else 3.8, 4.0)
        stats['ball_infields'].append({'kind':kind,'home':home.tolist(),'facing':((a+b)/math.sqrt(2)).tolist(),'base_spacing_m':base_m})

    # The natural-turf soccer field shares the east grass/outfield, as the aerial shows.
    sc = np.array([342.0, 1358.0]); se = east; sn = north
    soccer = lambda g: local(g, sc, se, sn)
    outline = box(-30.5, -50, 30.5, 50)
    lines = [outline.boundary, LineString([(-30.5, 0), (30.5, 0)]), Point(0,0).buffer(9.15, quad_segs=28).boundary]
    for sign in [-1,1]:
        y = sign*50
        lines += [LineString([(-20.16,y),(-20.16,y-sign*16.5),(20.16,y-sign*16.5),(20.16,y)]),
                  LineString([(-9.16,y),(-9.16,y-sign*5.5),(9.16,y-sign*5.5),(9.16,y)])]
        goal(sc+sn*y, se, -sign*sn)
    paint(unary_union([soccer(line).buffer(.055, cap_style=2, join_style=2) for line in lines]))
    # Keep new access strips short, connected and outside active playing surfaces.
    path = LineString([(375.2, 1260.0), (375.2, 1330.0), (384.0, 1339.0)])
    surface(path.buffer(.9, cap_style=2, join_style=2), 'Paving', .10, .04)
    for yy in [1307, 1381]:
        ctx.eg['Furniture'].append(ctx.boxmesh(241.8, yy, .32, 1.0, 4.2, .16))
    after = sum(len(m.faces) for parts in ctx.eg.values() for m in parts)
    stats['added_triangles'] = after - before
    stats['secondary_dimensions'] = 'Mapped locations; regulation court and ball-base dimensions. Track geometry, soccer markings, goals, fences and small furniture are approximate photographic interpretations.'
    return stats
