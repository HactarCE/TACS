import math

FRAMERATE = 60

# TODO just make a proper vector class that has all these operations

def pythag(*args):
    # maybe use math.hypot() instead?
    return math.sqrt(sum(args))

def radian_angle_from_to(vec1, vec2):
    return math.atan2(vec2[1] - vec1[1], vec2[0] - vec1[0])

def rot_vector(vector, degrees):
    return rot_vector_r(vector, math.radians(degrees))

def rot_vector_r(vector, radians):
    x, y = vector
    sin, cos = math.sin(radians), math.cos(radians)
    return (sin * x + cos * y, cos * x + sin * y)

def optimize_rects(rect_list):
    # TODO add logic for combining Rects, or at least removing Rects that are
    # completely contained by others
    return rect_list
