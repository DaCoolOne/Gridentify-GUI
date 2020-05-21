from pyglet.gl import glClearColor

from scenes import SceneManager, UsernameSelectScene

from constants import GRID_SIZE
import pyglet.sprite

USERNAME = ""

window = pyglet.window.Window(width=GRID_SIZE * 5, height=GRID_SIZE * 5)
window.config.alpha_size = 8

# Create a human player:
scene_manager = SceneManager()
scene_manager.add_scene("USERNAME", UsernameSelectScene(scene_manager, window))

scene_manager.change_scene("USERNAME")


@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    scene_manager.current_scene.on_mouse_drag(x, y, dx, dy, buttons, modifiers)


@window.event
def on_mouse_motion(x, y, dx, dy):
    scene_manager.current_scene.on_mouse_motion(x, y, dx, dy)


@window.event
def on_mouse_release(x, y, buttons, modifiers):
    scene_manager.current_scene.on_mouse_release(x, y, buttons, modifiers)


@window.event
def on_mouse_press(x, y, button, modifiers):
    scene_manager.current_scene.on_mouse_press(x, y, button, modifiers)


@window.event
def on_key_press(symbol, modifiers):
    scene_manager.current_scene.on_key_press(symbol, modifiers)


@window.event
def on_text(text):
    scene_manager.current_scene.on_text(text)


@window.event
def on_draw():
    glClearColor(0, 0, 0, 1)
    window.clear()

    scene_manager.current_scene.on_draw(window)


pyglet.app.run()
