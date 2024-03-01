#!/bin/python

import time
import cv2
import tkinter as tk
from pynput import keyboard
import os
import signal
import random
import hashlib
import json
from playsound import playsound
import pathlib
import pyautogui

# CONSTANTS
CONFIG_LOC = None
JSON_LOC = os.environ.get("JSON_FILE_PATH")
LOCK_SOUND_LOC = os.environ.get("AUDIO_FILE_PATH_1")
UNLOCK_SOUND_LOC = os.environ.get("AUDIO_FILE_PATH_2")
WRONG_SOUND_LOC = os.environ.get("AUDIO_FILE_PATH_3")

string = ""
matched = None
password = ""
pyautogui.FAILSAFE = False  # Bypass pyautogui failsafe

unique_numbers = set()


# CHECK PLATFORM
if pathlib.Path.home() / ".config/screensaver":
    # Unix-based systems (Linux, macOS, BSD)
    CONFIG_LOC = pathlib.Path.home() / ".config" / "screensaver"
else:
    # Windows
    CONFIG_LOC = pathlib.Path.home() / "AppData" / "Roaming" / "screensaver"

CONFIG_LOC_FILENAME = "hash.txt"
VIDEO_LOC_FILENAME = os.path.expanduser(f"{CONFIG_LOC}/vid.json")


# Generate unique_numbers b/w a given range
def rand_unique(start, end):
    if len(unique_numbers) == end + 1:
        unique_numbers.clear()

    number = []

    while True:
        generatedNumber = random.randint(start, end)
        if generatedNumber not in unique_numbers:
            unique_numbers.add(generatedNumber)
            number.append(generatedNumber)
            break

    return number[0]


# Hash Function for password
def getPass(message):
    hash_object = hashlib.sha512(message.encode())
    hex_digest = hash_object.hexdigest()
    return hex_digest


# Play Aerial Videos
def playVideo():
    # Get the screen size
    screen_width, screen_height = pyautogui.size()

    # Move the cursor to the bottom right corner
    pyautogui.moveTo(screen_width, screen_height)
    pyautogui.click(button="left")

    with open(f"{VIDEO_LOC_FILENAME}", "r") as f:
        data = json.load(f)

    # Start Keylogger
    log.start()
    if os.path.exists(LOCK_SOUND_LOC):
        playsound(LOCK_SOUND_LOC)

    if data:
        while True:
            k = rand_unique(0, len(data) - 1)
            currURL = data[str(k)]

            root = tk.Tk()

            # Hide the cursor
            root.config(cursor="none")

            cap = cv2.VideoCapture(currURL)

            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frame = cv2.resize(
                    frame, (root.winfo_screenwidth(), root.winfo_screenheight())
                )
                cv2.putText(
                    frame,
                    time.strftime("%H:%M:%S %p"),
                    (50, root.winfo_screenheight() - 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    2,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )
                cv2.putText(
                    frame,
                    "Type Password to unlock",
                    (60, root.winfo_screenheight() - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA,
                )
                cv2.namedWindow("Video", cv2.WINDOW_FULLSCREEN | cv2.WINDOW_GUI_NORMAL)
                cv2.setWindowProperty(
                    "Video", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN
                )
                cv2.imshow("Video", frame)

                if cv2.waitKey(25) & 0xFF == ord("`"):
                    break

            cap.release()
            cv2.destroyAllWindows()


# Fill Screen with a black background first
def fillScreen():
    # Create a tkinter window
    root = tk.Tk()

    # Hide the cursor
    root.config(cursor="none")

    # Set the window to full screen
    root.attributes("-fullscreen", True)

    # Create a black canvas that fills the screen
    canvas = tk.Canvas(
        root,
        bg="black",
        width=root.winfo_screenwidth(),
        height=root.winfo_screenheight(),
        borderwidth=0,
    )
    canvas.pack()

    canvas.create_text(
        root.winfo_screenwidth() / 2,
        root.winfo_screenheight() / 2,
        text="",
        fill="white",
        font=("Helvetica", 72),
    )

    root.after(1000, playVideo)

    return root


# Save Credentials
def inputPass():
    def on_submit():
        global password
        password = entry.get()
        root.destroy()

    root = tk.Tk()
    root.title("Password Prompt")

    # set window size and position
    window_size = 200
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = int((screen_width / 2) - (window_size / 2))
    y = int((screen_height / 2) - (window_size / 2))
    root.geometry(f"{window_size}x{window_size}+{x}+{y}")

    # set window aspect ratio to 1:1
    root.resizable(width=False, height=False)

    # add password input field
    label = tk.Label(root, text="Please enter your password:")
    label.pack()
    entry = tk.Entry(root, show="*")
    entry.pack()

    # add submit button
    button = tk.Button(root, text="Submit", command=on_submit)
    button.pack()

    # run the main loop
    root.mainloop()


# Kill Script
def destroyScreen():
    pid = os.getpid()
    os.kill(pid, signal.SIGTERM)


# Keylogger Function
def listenKey():
    def on_key_press(key):
        global string
        try:
            # Quick Unlock
            if key == keyboard.Key.tab:
                playsound(UNLOCK_SOUND_LOC)
                destroyScreen()

            if key == keyboard.Key.enter:
                if getPass(string) == matched:
                    if os.path.exists(UNLOCK_SOUND_LOC):
                        playsound(UNLOCK_SOUND_LOC)
                    destroyScreen()
                else:
                    if os.path.exists(WRONG_SOUND_LOC):
                        playsound(WRONG_SOUND_LOC)
                    string = ""
            elif key == keyboard.Key.backspace:
                if len(string) > 0:
                    string = string.rstrip(string[-1])
            else:
                string += key.char
        except AttributeError as e:
            print(e)

    listener = keyboard.Listener(on_press=on_key_press)

    return listener


# Get logger object bu do not start Keylogger
log = listenKey()


# Check if credentials exists
if os.path.exists(f"{CONFIG_LOC}") and os.path.exists(
    f"{CONFIG_LOC}/{CONFIG_LOC_FILENAME}"
):
    with open(f"{CONFIG_LOC}/{CONFIG_LOC_FILENAME}", "r") as f:
        matched = str(f.readline()).strip(" ").rstrip("\n")

    if not matched:
        print("Credentials not saved properly!")

    else:
        # FillScreen with black
        rt = fillScreen()
        rt.mainloop()

# Sve if credentials does not exists
else:
    inputPass()
    val = getPass(password)

    os.mkdir(CONFIG_LOC)
    os.chdir(CONFIG_LOC)
    with open(f"{CONFIG_LOC_FILENAME}", "w") as f:
        f.write(val)

    data = None
    with open(f"{JSON_LOC}") as f:
        data = json.load(f)

    with open(f"{VIDEO_LOC_FILENAME}", "w") as f:
        json.dump(data, f)

    print("Credentials Saved!")
    print("Run the program again to enable lockscreen!")
