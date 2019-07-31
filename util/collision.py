from pymunk import Vec2d

accuracy = 0.1

# detect line/point collision
def line_point_hit(a, b, p):
    l = a.get_distance(b)
    d1 = a.get_distance(p)
    d2 = b.get_distance(p)
    if (d1+d2 >= l-accuracy and d1+d2 <= l+accuracy):
        return True
    return False

# http://jeffreythompson.org/collision-detection/line-line.php
def line_line_hit(a, b, c, d):
    # when lines are parallel, possible that ZeroDivisionError occurs. For now, catching the exception:
    # https://stackoverflow.com/questions/15866364/any-way-to-avoid-or-allow-division-by-zero-in-this-line-intersection-algorithm
    try:
        uA = ((d.x-c.x)*(a.y-c.y) - (d.y-c.y)*(a.x-c.x)) / ((d.y-c.y)*(b.x-a.x) - (d.x-c.x)*(b.y-a.y))
        uB = ((b.x-a.x)*(a.y-c.y) - (b.y-a.y)*(a.x-c.x)) / ((d.y-c.y)*(b.x-a.x) - (d.x-c.x)*(b.y-a.y))
    except ZeroDivisionError: # Lines are parallel
        return None
    if (uA >= 0 and uA <= 1 and uB >= 0 and uB <= 1):
        intersectionX = a.x + (uA * (b.x-a.x))
        intersectionY = a.y + (uA * (b.y-a.y))
        return Vec2d(intersectionX, intersectionY)
    return None