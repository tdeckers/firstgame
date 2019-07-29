import pyglet
from pyglet.window import key, mouse
from math import tan, radians, degrees, copysign, floor
import builtins
from pymunk import Vec2d

window = pyglet.window.Window(800, 600,caption="Game")
keymap = pyglet.window.key.KeyStateHandler()
window.push_handlers(keymap)
batch = pyglet.graphics.Batch()
fps_display = pyglet.window.FPSDisplay(window=window)

class Track:
    def __init__(self):
        #group = pyglet.graphics.Group()
        self.outer_points = [112, 542, 315, 541, 476, 539, 609, 544, 700, 514, 721, 451, 734, 323, 736, 172, 692, 95, 628, 75, 514, 64, 445, 72, 440, 122, 414, 177, 404, 246, 345, 254, 321, 242, 301, 186, 290, 147, 276, 86, 250, 41, 166, 57, 78, 75, 48, 205, 29, 396, 47, 503]
        batch.add(int(len(self.outer_points) / 2), pyglet.gl.GL_LINE_LOOP, None, ('v2i', tuple(self.outer_points)))
        self.inner_points = [139, 472, 357, 462, 473, 456, 562, 464, 621, 453, 639, 422, 642, 386, 646, 312, 657, 263, 647, 188, 623, 155, 565, 149, 524, 148, 501, 192, 485, 244, 477, 298, 433, 327, 379, 332, 317, 335, 261, 309, 250, 265, 219, 220, 213, 180, 193, 138, 172, 134, 153, 149, 143, 210, 121, 372, 121, 451]
        batch.add(int(len(self.inner_points) / 2), pyglet.gl.GL_LINE_LOOP, None, ('v2i', tuple(self.inner_points)))

class Car(pyglet.sprite.Sprite):            
    def __init__(self, x, y, angle=0.0, max_steering=40, max_acceleration=350.0):
        # size of car: 100 x 50
        image = pyglet.image.load('resources/car.png')
        image.anchor_x = int(image.width / 2)
        image.anchor_y = int(image.height / 2)
        pyglet.sprite.Sprite.__init__(self, image, x, y, batch=batch)  
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
                self.acceleration -= 200 * dt
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
                    self.acceleration = -self.velocity.x / dt    
        
        # limit max accelleration.   
        if not keymap[key.SPACE]:     
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

    def __repr__(self):
        return f"Car(pos={self.position_vector}, ang={self.angle})"

class Debug(pyglet.text.document.FormattedDocument):    
    def __init__(game):
        pyglet.text.FormattedDocument.__init__()


class Gamestate():
    def __init__(self):
        self.car = Car(155, 500)
        self.track = Track()
        self.debug_sprite = pyglet.text.Label('Sprite debug', font_size=10, font_name='Times New Roman',
                          x=790, y=590, anchor_x='right', anchor_y='center', batch=batch)
        self.debug_body = pyglet.text.Label('Body debug', font_size=10, font_name='Times New Roman',
                          x=790, y=575, anchor_x='right', anchor_y='center', batch=batch)
        self.debug_vel = pyglet.text.Label('Vel debug', font_size=10, font_name='Times New Roman',
                          x=790, y=560, anchor_x='right', anchor_y='center', batch=batch)                          
    
    def handle_player(self, dt):
        self.car.handle_player(dt)

    def update(self, dt):
        self.debug_sprite.text = f"sprite x: {floor(self.car.x)}, y: {floor(self.car.y)}, dir: {floor(self.car.rotation)}"
        self.debug_vel.text = f"l: {round(self.car.velocity.x,1)}, dir: {floor(self.car.velocity.angle)}, accel: {round(self.car.acceleration, 1)}"
        self.handle_player(dt)

world = Gamestate()        

@window.event
def on_draw():
    window.clear()
    fps_display.draw() 
    batch.draw()

def update(dt):
    world.update(dt)

def start_up():
    pyglet.clock.schedule_interval(update, 1.0/60.0) # update at 60Hz
    window.clear()
    #window.flip() # ???
    window.set_visible(True)
    pyglet.app.run()

    # @window.event
    # def on_key_release(symbol, modifiers):
    #     if (symbol == key.RIGHT) or (symbol == key.LEFT):
    #         car.turn(0)
    #     elif (symbol == key.UP) or (symbol == key.DOWN):
    #         car.accel(0)

    # @window.event
    # def on_mouse_press(x, y, button, modifiers):
    #     if button == mouse.LEFT:
    #         print(f"x={x}, y={y}")
    #         track.inner_points.append(x)
    #         track.inner_points.append(y)


if __name__ == '__main__':
    start_up()