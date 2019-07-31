from math import radians, cos, sin, sqrt

# https://stackoverflow.com/questions/34372480/rotate-point-about-another-point-in-degrees-python
def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in degrees.
    """
    ox, oy = origin
    px, py = point

    angle_r = radians(angle)
    qx = ox + cos(angle_r) * (px - ox) - sin(angle_r) * (py - oy)
    qy = oy + sin(angle_r) * (px - ox) + cos(angle_r) * (py - oy)
    return qx, qy

def closest_point(target, point1, point2):
    if point1 == None:
        return point2
    if point2 == None:
        return point1
    d1 = sqrt( ((target.x-point1.x)**2)+((target.y-point1.y)**2) )
    d2 = sqrt( ((target.x-point2.x)**2)+((target.y-point2.y)**2) )
    if (d1 < d2):
        return point1
    else:
        return point2