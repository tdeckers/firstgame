import pyglet
from pyglet.window import key, mouse
from math import tan, radians, degrees, copysign, floor, cos, sin
import builtins
from pymunk import Vec2d, Poly
from itertools import chain

window = pyglet.window.Window(800, 600,caption="Game")
keymap = pyglet.window.key.KeyStateHandler()
window.push_handlers(keymap)
batch = pyglet.graphics.Batch()
car_batch = pyglet.graphics.Batch()
fps_display = pyglet.window.FPSDisplay(window=window)

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

class Track:
    def __init__(self):
        #group = pyglet.graphics.Group()
        self.outer_points = [112, 542, 315, 541, 476, 539, 609, 544, 700, 514, 721, 451, 734, 323, 736, 172, 692, 95, 628, 75, 514, 64, 445, 72, 440, 122, 414, 177, 404, 246, 345, 254, 321, 242, 301, 186, 290, 147, 276, 86, 250, 41, 166, 57, 78, 75, 48, 205, 29, 396, 47, 503, 112, 542]
        batch.add(int(len(self.outer_points) / 2), pyglet.gl.GL_LINE_STRIP, None, ('v2i', tuple(self.outer_points)))
        self.inner_points = [139, 472, 357, 462, 473, 456, 562, 464, 621, 453, 639, 422, 642, 386, 646, 312, 657, 263, 647, 188, 623, 155, 565, 149, 524, 148, 501, 192, 485, 244, 477, 298, 433, 327, 379, 332, 317, 335, 261, 309, 250, 265, 219, 220, 213, 180, 193, 138, 172, 134, 153, 149, 143, 210, 121, 372, 121, 451, 139, 472] 
        batch.add(int(len(self.inner_points) / 2), pyglet.gl.GL_LINE_LOOP, None, ('v2i', tuple(self.inner_points)))

    def get_outer_points(self):
        lines = []
        for i in range(0, len(self.outer_points), 2):
            lines.append((self.outer_points[i], self.outer_points[i+1]))
        return lines
    
    def get_inner_points(self):
        lines = []
        for i in range(0, len(self.inner_points), 2):
            lines.append((self.inner_points[i], self.inner_points[i+1]))
        return lines

class Car(pyglet.sprite.Sprite):            
    def __init__(self, x, y, angle=0.0, max_steering=40, max_acceleration=350.0):
        # size of car: 100 x 50
        image = pyglet.image.load('resources/car.png')
        image.anchor_x = int(image.width / 2)
        image.anchor_y = int(image.height / 2)
        pyglet.sprite.Sprite.__init__(self, image, x, y, batch=car_batch)
        self.scale = 0.4
        self.position_vector = Vec2d(x, y)
        self.velocity = Vec2d(0.0, 0.0)
        self.rotation = angle
        self.length = image.height
        self.max_acceleration = max_acceleration
        self.max_steering = max_steering
        self.max_velocity = 200
        self.brake_deceleration = 750
        self.free_deceleration = 200
        self.steer_rate = 175

        self.acceleration = 0.0
        self.steering = 0.0

        self.shape = car_batch.add(4, pyglet.gl.GL_LINE_LOOP, None, ('v2i', self.get_body_flat()))
        self.collision_point = None

    def handle_player(self, dt):
        if keymap[key.UP]:
            if self.velocity.x < 0:
                self.acceleration = self.brake_deceleration
            else:
                #self.acceleration += 200 * dt    
                self.acceleration = self.max_acceleration # Pedal = metal
        elif keymap[key.DOWN]:
            if self.velocity.x > 0:
                self.acceleration = -self.brake_deceleration
            else:
                self.acceleration = -self.max_acceleration # Pedal = metal
        elif keymap[key.SPACE]:
            if abs(self.velocity.x) > dt * self.brake_deceleration:
                self.acceleration = -copysign(self.brake_deceleration,self.velocity.x)
            else:
                self.acceleration = -1 * self.velocity.x / dt            
        else:
            if abs(self.velocity.x) > dt * self.free_deceleration:
                self.acceleration = -copysign(self.free_deceleration, self.velocity.x)
            else:
                if dt != 0:
                    self.acceleration = -1 * self.velocity.x / dt    
        
        # limit max accelleration.   
        if not keymap[key.SPACE]: # except when braking. 
            self.acceleration = max(-self.max_acceleration, min(self.acceleration, self.max_acceleration))

        if keymap[key.RIGHT]:
            self.steering += 50 + self.steer_rate * dt
        elif keymap[key.LEFT]:
            self.steering -= 50 + self.steer_rate * dt
        else:
            self.steering = 0
        
        # limit steering
        self.steering = max(-self.max_steering, min(self.steering, self.max_steering))

        self.update(dt)

    def update(self, dt):
        self.velocity += (self.acceleration * dt, 0)
        if self.velocity.x != 0:
            self.velocity.x = max(-self.max_velocity, min(self.velocity.x, self.max_velocity))

        if self.steering:
            turning_radius = self.length / tan(radians(self.steering))
            angular_velocity = self.velocity.x / turning_radius
        else:
            angular_velocity = 0

        self.position_vector +=  self.velocity.rotated_degrees(-self.rotation)  * dt
        self.rotation += degrees(angular_velocity) * dt

        # Don't drive off screen.
        self.position_vector.x = max(0, min(self.position_vector.x, window.width))
        self.position_vector.y = max(0, min(self.position_vector.y, window.height))

        self.x = self.position_vector.x
        self.y = self.position_vector.y

        self.shape.vertices = self.get_body_flat()

    # https://stackoverflow.com/questions/12161277/how-to-rotate-a-vertex-around-a-certain-point
    # for each corner, apply rotation around (x,y) 
    def get_body(self):
        p1 = (self.x - self.width/2, self.y - self.height/2)
        p2 = (self.x - self.width/2, self.y + self.height/2)
        p3 = (self.x + self.width/2, self.y + self.height/2)
        p4 = (self.x + self.width/2, self.y - self.height/2)
        center = self.position_vector.int_tuple
        q1 = rotate(center, p1, -self.rotation)
        q2 = rotate(center, p2, -self.rotation)
        q3 = rotate(center, p3, -self.rotation)
        q4 = rotate(center, p4, -self.rotation)
        return (q1, q2, q3, q4)

    def get_body_flat(self):
        body_points = tuple(chain(*self.get_body())) # flatten
        return tuple(int(i) for i in body_points) # convert floats to ints

    def draw_collision(self, point):
        hit = [point.x - 5, point.y - 5,
            point.x + 5, point.y + 5,
            point.x - 5, point.y + 5,
            point.x + 5, point.y - 5]
        if self.collision_point != None:
            self.collision_point.delete()
        self.collision_point = car_batch.add(4, pyglet.gl.GL_LINES, None, 
                ('v2i', [int(i) for i in hit]),
                ('c3B', (255, 0, 0, 255, 0, 0, 255, 0, 0, 255, 0, 0,))
            )                                            

    def remove_collision(self):
        if self.collision_point != None:
            self.collision_point.delete()
            self.collision_point = None

    def __repr__(self):
        return f"Car(pos={self.position_vector}, ang={self.angle})"

class Gamestate():
    def __init__(self):
        self.car = Car(155, 500)
        self.track = Track()
        self.debug_sprite = pyglet.text.Label('Sprite debug', font_size=10, font_name='Times New Roman',
                          x=790, y=590, anchor_x='right', anchor_y='center', batch=batch)
        self.debug_vel = pyglet.text.Label('Vel debug', font_size=10, font_name='Times New Roman',
                          x=790, y=575, anchor_x='right', anchor_y='center', batch=batch)   
        self.car_hit_point = None                       
    
    def handle_player(self, dt):
        self.car.handle_player(dt)

    def update(self, dt):
        self.debug_sprite.text = f"sprite x: {floor(self.car.x)}, y: {floor(self.car.y)}, dir: {floor(self.car.rotation)}"
        self.debug_vel.text = f"l: {round(self.car.velocity.x,1)}, dir: {floor(self.car.velocity.angle)}, accel: {round(self.car.acceleration, 1)}"
        self.handle_player(dt)
        self.detect_collision()
    
    def detect_collision(self):
        body_points = self.car.get_body()
        # Check outer track
        for i in range(len(self.track.get_outer_points())-1):
            track_point1 = self.track.get_outer_points()[i]
            track_point2 = self.track.get_outer_points()[i+1]

            # Check only 2 sides of the car is likely enough.
            # One side:
            body_point1 = body_points[1]
            body_point2 = body_points[2]
            hit_point = line_line_hit(Vec2d(track_point1), Vec2d(track_point2), Vec2d(body_point1), Vec2d(body_point2))                
            if (hit_point == None):
                  # Other side:
                  body_point1 = body_points[0]
                  body_point2 = body_points[3]
                  hit_point = line_line_hit(Vec2d(track_point1), Vec2d(track_point2), Vec2d(body_point1), Vec2d(body_point2))  
            if (hit_point == None):
                self.car.remove_collision()
            else:
                self.car.draw_collision(hit_point)
                return # Found collision, look no further.  

        # Check inner track.
        for i in range(len(self.track.get_inner_points())-1):
            track_point1 = self.track.get_inner_points()[i]
            track_point2 = self.track.get_inner_points()[i+1]

            # Check only 2 sides of the car is likely enough.
            # One side:
            body_point1 = body_points[1]
            body_point2 = body_points[2]
            hit_point = line_line_hit(Vec2d(track_point1), Vec2d(track_point2), Vec2d(body_point1), Vec2d(body_point2))                
            if (hit_point == None):
                  # Other side:
                  body_point1 = body_points[0]
                  body_point2 = body_points[3]
                  hit_point = line_line_hit(Vec2d(track_point1), Vec2d(track_point2), Vec2d(body_point1), Vec2d(body_point2))  
            if (hit_point == None):
                self.car.remove_collision()
            else:
                self.car.draw_collision(hit_point)
                return # Found collision, look no further.  

world = Gamestate()        

accuracy = 0.1

# detect line/point collision
def line_point_hit(a, b, p):
    l = a.get_distance(b)
    d1 = a.get_distance(p)
    d2 = b.get_distance(p)
    if (d1+d2 >= l-accuracy and d1+d2 <= l+accuracy):
        return True
    return False

def line_line_hit(a, b, c, d):
    uA = ((d.x-c.x)*(a.y-c.y) - (d.y-c.y)*(a.x-c.x)) / ((d.y-c.y)*(b.x-a.x) - (d.x-c.x)*(b.y-a.y))
    uB = ((b.x-a.x)*(a.y-c.y) - (b.y-a.y)*(a.x-c.x)) / ((d.y-c.y)*(b.x-a.x) - (d.x-c.x)*(b.y-a.y))
    if (uA >= 0 and uA <= 1 and uB >= 0 and uB <= 1):
        intersectionX = a.x + (uA * (b.x-a.x))
        intersectionY = a.y + (uA * (b.y-a.y))
        return Vec2d(intersectionX, intersectionY)
    return None

@window.event
def on_draw():
    window.clear()
    fps_display.draw() 
    batch.draw()
    car_batch.draw()

hit_point_v = None

@window.event
def on_mouse_motion(x, y, dx, dy):
    global hit_point_v
    hit_point = line_line_hit(Vec2d(112, 542), Vec2d(315, 541), Vec2d(0,0), Vec2d(x,y))
    if hit_point != None:
        hit = [hit_point.x - 5, hit_point.y - 5,
                                hit_point.x + 5, hit_point.y + 5,
                                hit_point.x - 5, hit_point.y + 5,
                                hit_point.x + 5, hit_point.y - 5]
        if hit_point_v != None:
            hit_point_v.delete()
        hit_point_v = batch.add(4, pyglet.gl.GL_LINES, None, 
            ('v2i', [int(i) for i in hit]),
            ('c3B', (255, 0, 0, 255, 0, 0, 255, 0, 0, 255, 0, 0,))
        )        
    else:
        if hit_point_v != None:
            hit_point_v.delete()
            hit_point_v = None


def update(dt):
    world.update(dt)

def start_up():
    pyglet.clock.schedule_interval(update, 1.0/60.0) # update at 60Hz
    window.clear()
    #window.flip() # ???
    window.set_visible(True)
    pyglet.app.run()

    # @window.event
    # def on_mouse_press(x, y, button, modifiers):
    #     if button == mouse.LEFT:
    #         print(f"x={x}, y={y}")
    #         track.inner_points.append(x)
    #         track.inner_points.append(y)

if __name__ == '__main__':
    start_up()