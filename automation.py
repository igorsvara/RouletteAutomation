import os
import time
import csv
import threading
from pynput import mouse, keyboard
from PIL import Image, ImageChops, ImageGrab
import numpy as np


# TODO: ordina questo macello
csv_path = "results.csv"

with open(csv_path, "w") as file:
    c_writer = csv.writer(file)
    c_writer.writerow(["Date", "Time", "Bet amount", "Bet outcome", "P of this eoutcome"])

BETTING_POS = (1476, 878)
GIRO_VELOCE = (496, 961)

GIRO_VELOCE_SCREEN = (442, 906)
GIRO_VELOCE_SCREEN_SIZE = (129, 122)
GIRO_VELOCE_COORD = (GIRO_VELOCE_SCREEN[0], GIRO_VELOCE_SCREEN[1],
                     GIRO_VELOCE_SCREEN[0] + GIRO_VELOCE_SCREEN_SIZE[0],
                     GIRO_VELOCE_SCREEN[1] + GIRO_VELOCE_SCREEN_SIZE[1])
giro_v = Image.open("giro_veloce.png")
giro_v_array = np.array(giro_v)

BET_LOST_SCREEN = (777, 1050)
BET_LOST_SCREEN_SIZE = (96, 23)
BET_LOST_COORD = (BET_LOST_SCREEN[0], BET_LOST_SCREEN[1],
                  BET_LOST_SCREEN[0] + BET_LOST_SCREEN_SIZE[0], BET_LOST_SCREEN[1] + BET_LOST_SCREEN_SIZE[1])
b_lost = Image.open("bet_lost.png")
b_lost_array = np.array(b_lost)

# Variabili globali per indicare lo stato di esecuzione del programma
e = threading.Event()
e.clear()
program_running = False
program_stopped = False

fibonacci = [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4184]
bet_amount_idx = 0
previous_bet_info = []
win_prob = 12/37

def get_current_datetime():
    current_date = time.strftime("%d/%m/%y")
    current_time = time.strftime("%H:%M:%S")
    return current_date, current_time


def capture_screen():
    screenshot = ImageGrab.grab(bbox=GIRO_VELOCE_COORD)
    return screenshot


def key_pressed(key):
    global program_running, program_stopped, e

    try:
        if key.char == "e":
            print(f"Program stopped by E")
            # Salvo l'ultima giocata
            compute_outcome()
            os._exit(1)

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


def can_bet():
    tmp = ImageGrab.grab(bbox=GIRO_VELOCE_COORD)
    tmp_array = np.array(tmp)
    return np.array_equiv(giro_v_array, tmp_array)


def did_bet_lost():
    # TODO: velocizza il match con uno screen grayscale
    tmp = ImageGrab.grab(bbox=BET_LOST_COORD)
    tmp_array = np.array(tmp)
    return np.array_equiv(b_lost_array, tmp_array)


def click_n_times(mouse_c, num, delay):
    for i in range(num):
        mouse_c.click(mouse.Button.left)
        time.sleep(delay)


'''
Questa procedura resetta l'indice nel caso in cui si e' verificata una vincita.
Inoltre calcola la probabilita' e salva nell'excel il risultato della giocata
'''
def compute_outcome():
    global bet_amount_idx, previous_bet_info

    if previous_bet_info:   # list is not empty
        last_bet_amount = fibonacci[bet_amount_idx - 1]
        outcome_prob = (1-win_prob)**bet_amount_idx
        if not did_bet_lost():
            outcome_prob = outcome_prob / (1-win_prob) * win_prob
            bet_amount_idx = 0
            # Bet won, profit two times the bet
            last_bet_amount *= -2
        previous_bet_info.append(last_bet_amount * (-1))
        previous_bet_info.append(outcome_prob * 100)
        with open(csv_path, "a", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(previous_bet_info)

def place_bet(mouse_c):
    global bet_amount_idx, previous_bet_info

    # Excel population and index reset
    compute_outcome()

    mouse_c.position = BETTING_POS
    # Click con delay
    click_n_times(mouse_c, fibonacci[bet_amount_idx], 0.1)

    mouse_c.position = GIRO_VELOCE
    mouse_c.click(mouse.Button.left, 1)

    mouse_c.position = (GIRO_VELOCE[0] + 200, GIRO_VELOCE[1] - 200)

    current_date, current_time = get_current_datetime()
    previous_bet_info = [current_date, current_time, fibonacci[bet_amount_idx]]

    bet_amount_idx += 1


def worker_function():
    global program_running, e
    mouse_c = mouse.Controller()
    print("Worker initiated")

    while True:
        e.wait()
        if program_stopped:
            return False

        if can_bet():
            place_bet(mouse_c)

        time.sleep(1)


def main():
    with keyboard.Listener(on_press=key_pressed) as listener:
        print("Listener initiated")

        worker_thread = threading.Thread(target=worker_function)
        worker_thread.start()

        worker_thread.join()
        listener.join()


# TODO: trova un modo per memorizzare anche l'ultima bet senza doverne fare ancora uno (if end -> dump array of previous outcome)
if __name__ == "__main__":
    main()
