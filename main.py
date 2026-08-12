from ursina import *
import random

app = Ursina()

window.title = "Corsa 3D"
window.borderless = False
window.fullscreen = False
window.exit_button.visible = False
window.fps_counter.enabled = False

# --- TERRENO ---
ground = Entity(model='plane', scale=100, texture='grass', collider='box', color=color.green.tint(-.2))

# --- MACCHINA STILE SUPERCAR ---
car = Entity(position=(0, 0.3, 0), collider='box')
body = Entity(model='cube', color=color.orange, scale=(1.3, 0.35, 2.4), position=(0, 0.15, 0), parent=car)
cabin = Entity(model='cube', color=color.black, scale=(1.0, 0.25, 1.0), position=(0, 0.4, -0.1), parent=car)
nose = Entity(model='cube', color=color.orange, scale=(1.1, 0.2, 0.5), position=(0, 0.05, 1.3), parent=car)
spoiler = Entity(model='cube', color=color.black, scale=(1.2, 0.08, 0.25), position=(0, 0.55, -1.15), parent=car)
spoiler_l = Entity(model='cube', color=color.black, scale=(0.08, 0.3, 0.25), position=(-0.55, 0.35, -1.15), parent=car)
spoiler_r = Entity(model='cube', color=color.black, scale=(0.08, 0.3, 0.25), position=(0.55, 0.35, -1.15), parent=car)

wheel_positions = [(-0.65, -0.15, 0.85), (0.65, -0.15, 0.85), (-0.65, -0.15, -0.85), (0.65, -0.15, -0.85)]
for wp in wheel_positions:
    Entity(model='cube', color=color.black, scale=(0.28, 0.28, 0.28), position=car.position + Vec3(*wp), parent=car)

car_speed = 0
max_speed = 22
acceleration = 14
turn_speed = 90
friction = 6

# --- CAMERA TERZA PERSONA ---
camera.parent = car
camera.position = (0, 4, -10)
camera.rotation_x = 15
camera.fov = 90

# --- SUONI ---
try:
    engine_sound = Audio('sounds/engine.wav', loop=True, autoplay=True, volume=0.3)
except:
    engine_sound = None

try:
    skid_sound = Audio('sounds/skid.wav', loop=False, autoplay=False, volume=0.5)
except:
    skid_sound = None

skid_cooldown = 0

# --- CHECKPOINT ---
checkpoint_positions = [
    (15, 0.5, 15), (-15, 0.5, 25), (-25, 0.5, -5),
    (0, 0.5, -20), (20, 0.5, -10)
]
checkpoints = []
for i, pos in enumerate(checkpoint_positions):
    ring = Entity(model='circle', color=color.yellow, scale=4,
                   position=pos, rotation_x=90, double_sided=True,
                   collider='box')
    Text(text=str(i + 1), parent=ring, y=1.2, scale=15, color=color.black, billboard=True)
    checkpoints.append(ring)

current_checkpoint = 0
time_left = 60
game_over = False
win = False

# --- UI ---
timer_text = Text(text="Tempo: 60", position=(-0.85, 0.45), scale=2, color=color.white)
checkpoint_text = Text(text="Checkpoint: 1/5", position=(-0.85, 0.38), scale=2, color=color.white)
status_text = Text(text="", position=(0, 0.1), scale=3, origin=(0, 0), color=color.yellow)


def update():
    global car_speed, current_checkpoint, time_left, game_over, win, skid_cooldown

    if game_over:
        if engine_sound:
            engine_sound.volume = 0
        return

    time_left -= time.dt
    if time_left <= 0:
        time_left = 0
        game_over = True
        status_text.text = "TEMPO SCADUTO!\nPremi R per ricominciare"
    timer_text.text = f"Tempo: {int(time_left)}"

    if held_keys['w']:
        car_speed = min(car_speed + acceleration * time.dt, max_speed)
    elif held_keys['s']:
        car_speed = max(car_speed - acceleration * time.dt, -max_speed / 2)
    else:
        if car_speed > 0:
            car_speed = max(car_speed - friction * time.dt, 0)
        elif car_speed < 0:
            car_speed = min(car_speed + friction * time.dt, 0)

    turning = False
    if abs(car_speed) > 0.1:
        turn_dir = 0
        if held_keys['a']:
            turn_dir = -1
            turning = True
        elif held_keys['d']:
            turn_dir = 1
            turning = True
        car.rotation_y += turn_dir * turn_speed * time.dt * (1 if car_speed > 0 else -1)

    car.position += car.forward * car_speed * time.dt
    car.x = clamp(car.x, -48, 48)
    car.z = clamp(car.z, -48, 48)

    if engine_sound:
        speed_ratio = abs(car_speed) / max_speed
        engine_sound.volume = 0.25 + speed_ratio * 0.35
        try:
            engine_sound.pitch = 0.8 + speed_ratio * 0.9
        except:
            pass

    skid_cooldown -= time.dt
    if skid_sound and turning and abs(car_speed) > max_speed * 0.6 and skid_cooldown <= 0:
        skid_sound.play()
        skid_cooldown = 0.8

    if current_checkpoint < len(checkpoints):
        target = checkpoints[current_checkpoint]
        if distance(car.position, target.position) < 3:
            target.color = color.gray
            current_checkpoint += 1
            checkpoint_text.text = f"Checkpoint: {min(current_checkpoint + 1, len(checkpoints))}/{len(checkpoints)}"
            time_left += 10

            if current_checkpoint == len(checkpoints):
                game_over = True
                win = True
                status_text.text = "HAI VINTO!\nPremi R per ricominciare"


def input(key):
    if key == 'r':
        restart()


def restart():
    global current_checkpoint, time_left, game_over, win, car_speed
    car.position = (0, 0.3, 0)
    car.rotation_y = 0
    car_speed = 0
    current_checkpoint = 0
    time_left = 60
    game_over = False
    win = False
    status_text.text = ""
    checkpoint_text.text = "Checkpoint: 1/5"
    for ch in checkpoints:
        ch.color = color.yellow
    if engine_sound:
        engine_sound.volume = 0.25


Sky()
app.run()
