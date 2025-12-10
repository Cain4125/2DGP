import time

frame_time = 0.0

running = None
stack = None

def change_mode(mode):
    global stack
    if (len(stack) > 0):
        # execute the current mode's finish function
        stack[-1].finish()
        # remove the current mode
        stack.pop()
    stack.append(mode)
    mode.enter()


def push_mode(mode):
    global stack
    if (len(stack) > 0):
        stack[-1].pause()
    stack.append(mode)
    mode.enter()


def pop_mode():
    global stack
    if (len(stack) > 0):
        # execute the current mode's finish function
        stack[-1].finish()
        # remove the current mode
        stack.pop()

    # execute resume function of the previous mode
    if (len(stack) > 0):
        stack[-1].resume()


def quit():
    global running
    running = False


def run(start_mode):
    global running, stack
    running = True
    stack = [start_mode]
    start_mode.enter()

    global frame_time
    frame_time = 0.0
    current_time = time.time()

    while running:
        stack[-1].handle_events()
        stack[-1].update()
        stack[-1].draw()

        new_time = time.time()
        frame_time = new_time - current_time
        current_time = new_time

        if frame_time > 0.05:
            frame_time = 0.05
        # print(f'Frame Time: {frame_time}, Frame Rate: {frame_rate}')

    # repeatedly delete the top of the stack
    while (len(stack) > 0):
        stack[-1].finish()
        stack.pop()

