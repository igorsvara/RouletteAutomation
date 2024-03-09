import time
import threading
from pynput import mouse, keyboard

BETTING_POS = (1476, 878)
GIRO_VELOCE = (496, 961)
# Variabili globali per indicare lo stato di esecuzione del programma
e = threading.Event()
e.clear()
program_running = False
program_stopped = False


def key_pressed(key):
    global program_running, program_stopped, e

    try:
        if key.char == "e":
            print(f"Program stopped by E")
            # TODO: trova un modo intelligente per killare il processo worker

            # Activate the event to kill the worker
            program_stopped = True
            e.set()
            e.clear()

            return False
        elif key.char == "r":
            if program_running:
                e.clear()
                print(f"Program paused by R")
            else:
                e.set()
                print(f"Program resumed by R")
            program_running = not program_running
    except AttributeError:
        pass


def worker_function():
    global program_running, e
    mouse_c = mouse.Controller()
    print("Worker initiated")

    while True:
        e.wait()
        if program_stopped:
            return False

        mouse_c.position = BETTING_POS
        mouse_c.click(mouse.Button.left, 1)

        mouse_c.position = GIRO_VELOCE
        mouse_c.click(mouse.Button.left, 1)

        print(f"Bet placed {time.ctime()}")
        time.sleep(2)


def main():
    with keyboard.Listener(on_press=key_pressed) as listener:
        print("Listener initiated")

        worker_thread = threading.Thread(target=worker_function)
        worker_thread.start()

        worker_thread.join()
        listener.join()


if __name__ == "__main__":
    main()
