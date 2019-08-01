import numpy as np
import game

restart = False

if __name__ == '__main__':
    from pyglet.window import key
    a = np.array( [0, 1, 0] )
    def key_press(k, mod):
        global restart
        if k==0xff0d: restart = True
        if k==key.LEFT:  a[0] = 1
        if k==key.RIGHT: a[0] = 2
        if k==key.UP:    a[1] = 1
        if k==key.DOWN:  a[1] = 2
        if k==key.SPACE: a[2] = 1
    def key_release(k, mod):
        if k==key.LEFT and a[0] == 1:  a[0] = 0
        if k==key.RIGHT and a[0] == 2: a[0] = 0
        if k==key.UP and a[1] == 1:    a[1] = 0
        if k==key.DOWN and a[1] == 2:  a[1] = 0   
        if k==key.SPACE: a[2] = 0
    env = game.Game()
    #world.reset() # We're just starting.. no need to reset.
    env.render()
    env.viewer.window.on_key_press = key_press
    env.viewer.window.on_key_release = key_release

    isopen = True
    while isopen:
        env.reset()
        total_reward = 0.0
        steps = 0
        restart = False
        while True:
            s, r, done, info = env.step(a)
            total_reward += r
            if steps % 200 == 0 or done:
                print("\naction " + str(["{:+0.2f}".format(x) for x in a]))
                print("step {} total_reward {:+0.2f}".format(steps, total_reward))
                #import matplotlib.pyplot as plt
                #plt.imshow(s)
                #plt.savefig("test.jpeg")
            steps += 1
            isopen = env.render()
            #time.sleep(0.25)
            if done or restart or isopen == False:
                break