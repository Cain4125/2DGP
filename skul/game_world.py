import camera

world = [[], [], []]

def add_object(o, depth=1):
    world[depth].append(o)

def remove_object(o):
    for layer in world:
        if o in layer:
            layer.remove(o)
            return
    print('삭제하려는 객체가 월드에 없습니다.')

def update():
    for layer in world:
        for o in layer:
            o.update()

def render():
    cam_x, cam_y = int(camera.camera.x), int(camera.camera.y)
    for layer in world:
        for o in layer:
            o.draw(cam_x, cam_y)

def clear():
    global world
    for layer in world:
        layer.clear()
    world = [[], [], []]

def all_objects():
    for layer in world:
        for o in layer:
            yield o