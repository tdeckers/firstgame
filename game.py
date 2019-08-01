import gym
from gym import spaces
from gym.utils import seeding

import numpy as np

import pyglet
from pyglet import gl

FPS         = 60         # Frames per second
WINDOW_W    = 800
WINDOW_H    = 600

class Game(gym.Env):
    metadata = {
        'render.modes': ['human', 'rgb_array', 'state_pixels'],
        'video.frames_per_second' : FPS
    }    

    def __init__(self):        
        self.seed()
        self.reward = 0.0
        self.prev_reward = 0.0
        self.viewer = None
        self.action_space = spaces.MultiDiscrete([2,2,1])      # steer (1=left, 2=right), gas (1=fwd, 2=rev), brake
        self.observation_space = spaces.Tuple([
            #spaces.MultiDiscrete([self.car.max_velocity, 360]), # velocity, rotation
            spaces.MultiDiscrete([220, 360]), # velocity, rotation
            spaces.Box(low=0, high=np.inf, shape=(8,), dtype=np.float32)             # radars(8)
        ])

        self.score = 0
        self.prev_score = 0
        self.gate = 0
        self.crash = False

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def render(self, mode='human'):
        assert mode in ['human', 'state_pixels', 'rgb_array']

        if self.viewer is None:
            from gym.envs.classic_control import rendering
            self.viewer = rendering.Viewer(WINDOW_W, WINDOW_H)
            self.score_label = pyglet.text.Label('0000', font_size=36,
                x=20, y=100, anchor_x='left', anchor_y='center',
                color=(255,0,255,255))

        arr = None
        win = self.viewer.window
        win.switch_to()
        win.dispatch_events()

        self.score_label.text = "%04i" % self.reward
        self.score_label.draw()

        if mode=='rgb_array':
            VP_W = WINDOW_W
            VP_H = WINDOW_H
        elif mode == 'state_pixels':
            VP_W = WINDOW_W
            VP_H = WINDOW_H
        else:
            pixel_scale = 1
            if hasattr(win.context, '_nscontext'):
                pixel_scale = win.context._nscontext.view().backingScaleFactor()  # pylint: disable=protected-access
            VP_W = int(pixel_scale * WINDOW_W)
            VP_H = int(pixel_scale * WINDOW_H)

        gl.glViewport(0, 0, VP_W, VP_H)

        gl.glBegin(gl.GL_QUADS)
        s = WINDOW_W/40.0
        h = WINDOW_H/40.0
        gl.glColor4f(0,255,0,1)
        gl.glVertex3f(WINDOW_W, 0, 0)
        gl.glVertex3f(WINDOW_W, 5*h, 0)
        gl.glVertex3f(0, 5*h, 0)
        gl.glVertex3f(0, 0, 0)
        gl.glEnd()

    def reset(self):
        self.reward = 0.0
        self.prev_reward = 0.0

        return self.step(None)[0]        

    def step(self, action):
        dt = 1.0/FPS

        self.state = self.render()

        step_reward = 0
        done = False        

        if action is not None: # First step without action, called from reset()
            self.reward -= 0.1
            # credits for passing gate.
            if self.score == self.prev_score + 1:
                self.reward += 10
            if self.score == self.prev_score - 1:
                self.reward -= 20
            # TODO: credits for finishing lap?
            # big ding for hitting the track
            if self.crash:
                self.reward -= 100
                done = True
            step_reward = self.reward - self.prev_reward
            self.prev_reward = self.reward

        return self.state, step_reward, done, {}                