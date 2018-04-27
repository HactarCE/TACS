import math

FRAMERATE = 60

# TODO just make a proper vector class that has all these operations

def reduce_vector(vector, scalar):
    angle = math.atan2(*vector[::-1])
    mag = math.hypot(*vector) - scalar
    if mag > 0:
        return (mag * math.cos(angle), mag * math.sin(angle))
    else:
        return (0, 0)

def radian_angle_from_to(vec1, vec2):
    return math.atan2(vec2[1] - vec1[1], vec2[0] - vec1[0])

def rot_vector(vector, degrees):
    return rot_vector_r(vector, math.radians(degrees))

def rot_vector_r(vector, radians):
    x, y = vector
    sin, cos = math.sin(radians), math.cos(radians)
    return (cos * x + sin * y, sin * x + cos * y)

def add_vector(vector1, vector2):
    return (vector1[0] + vector2[0], vector1[1] + vector2[1])

def optimize_rects(rect_list):
    # TODO not actually sure whether this helps much
    # print('in', rect_list)
    new_list = []
    for r in rect_list:
        new_list = _add_rect_optimized(new_list, r)
    # print('out', new_list)
    return new_list

def _add_rect_optimized(rect_list, new):
    new_list = []
    for r in rect_list:
        if new and new.contains(r):
            if new not in new_list:
                new_list.append(new)
        else:
            if new and r.contains(new):
                new = None
            new_list.append(r)
    if new and new not in new_list:
        new_list.append(new)
    return new_list
