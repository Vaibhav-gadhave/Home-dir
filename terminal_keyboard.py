#!/usr/bin/env python3
import sys
import os
import subprocess
import re

# Ensure the script runs as root
if os.geteuid() != 0:
    print("Please run this script using sudo.")
    sys.exit(1)

# Find keyboard files directly inside Linux hardware symlinks
dev_path = None
by_path_dir = "/dev/input/by-path/"

if os.path.exists(by_path_dir):
    kbd_files = [f for f in os.listdir(by_path_dir) if "event-kbd" in f]
    
    if len(kbd_files) == 1:
        dev_path = os.path.join(by_path_dir, kbd_files[0])
    elif len(kbd_files) > 1:
        print("\nMultiple keyboard inputs detected. Please pick one:")
        for idx, f in enumerate(kbd_files):
            print(f" [{idx}] {f}")
        try:
            choice = int(input("\nEnter choice number: "))
            dev_path = os.path.join(by_path_dir, kbd_files[choice])
        except (ValueError, IndexError):
            print("Invalid selection.")
            sys.exit(1)

# Fallback check if symlink directory didn't resolve your hardware configuration
if not dev_path:
    try:
        with open("/proc/bus/input/devices", "r") as f:
            content = f.read()
        for section in content.split("\n\n"):
            if "EV=120013" in section or "kbd" in section.lower():
                match = re.search(r'event\d+', section)
                if match:
                    dev_path = f"/dev/input/{match.group(0)}"
                    break
    except Exception:
        pass

if not dev_path or not os.path.exists(dev_path):
    print("\nERROR: Failed to map a keyboard input line.")
    print("Please run: sudo ls -l /dev/input/by-path/")
    sys.exit(1)

# The updated visual grid featuring the standard nested up/down arrow configuration
LAYOUT = [
    "┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───────┐",
    "│ ~ │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │ 8 │ 9 │ 0 │ - │ = │ Back  │",
    "├───┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─────┤",
    "│ Tab │ Q │ W │ E │ R │ T │ Y │ U │ I │ O │ P │ [ │ ] │  \\  │",
    "├─────┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴┬──┴─────┤",
    "│ Caps │ A │ S │ D │ 𝐅 │ G │ H │ 𝐉 │ K │ L │ ; │ ' │ Enter  │",
    "├──────┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴─┬─┴────┬───┤",
    "│ Shift  │ Z │ X │ C │ V │ B │ N │ M │ , │ . │ / │Shift │ ↑ │",
    "├──────┬─┴──┬┴───┴───┴───┴───┴───┴───┴──┬┴───┼───┴┬───┬─┴─┬─┴─┐",
    "│ Ctrl │ Fn │ Win│       Space          │ Alt│Menu│ ← │ ↓ │ → │",
    "└──────┴────┴────┴──────────────────────┴────┴────┴───┴───┴───┘"
]

HIGHLIGHT = "\033[1;41;37m"  # High contrast bright red block background
RESET = "\033[0m"

def draw_keyboard(target_char=None):
    sys.stdout.write("\033[H") # Jump directly to home coordinate positions avoiding flickers
    for row in LAYOUT:
        if target_char and f" {target_char} " in row:
            highlighted = row.replace(f" {target_char} ", f" {HIGHLIGHT}{target_char}{RESET} ")
            sys.stdout.write(highlighted + "\n")
        elif target_char and target_char in ["Back", "Tab", "Caps", "Enter", "Shift", "Ctrl", "Fn", "Win", "Space", "Alt", "Menu"]:
            row_mod = row
            if target_char == "Back": row_mod = row_mod.replace(" Back  ", f"{HIGHLIGHT} Back  {RESET}")
            if target_char == "Tab": row_mod = row_mod.replace(" Tab ", f"{HIGHLIGHT} Tab {RESET}")
            if target_char == "Caps": row_mod = row_mod.replace(" Caps ", f"{HIGHLIGHT} Caps {RESET}")
            if target_char == "Enter": row_mod = row_mod.replace(" Enter  ", f"{HIGHLIGHT} Enter  {RESET}")
            if target_char == "Shift":
                row_mod = row_mod.replace(" Shift  ", f"{HIGHLIGHT} Shift  {RESET}")
                row_mod = row_mod.replace("Shift │", f"{HIGHLIGHT}Shift{RESET} │")
            if target_char == "Ctrl":
                row_mod = row_mod.replace(" Ctrl ", f"{HIGHLIGHT} Ctrl {RESET}")
                row_mod = row_mod.replace("│Ctrl│", f"│{HIGHLIGHT}Ctrl{RESET}│")
            if target_char == "Fn": row_mod = row_mod.replace(" Fn ", f"{HIGHLIGHT} Fn {RESET}")
            if target_char == "Win": row_mod = row_mod.replace(" Win│", f"{HIGHLIGHT} Win{RESET}│")
            if target_char == "Space": row_mod = row_mod.replace("       Space          ", f"{HIGHLIGHT}       Space          {RESET}")
            if target_char == "Alt": row_mod = row_mod.replace(" Alt│", f"{HIGHLIGHT} Alt{RESET}│")
            if target_char == "Menu": row_mod = row_mod.replace("│Menu│", f"│{HIGHLIGHT}Menu{RESET}│")
            sys.stdout.write(row_mod + "\n")
        else:
            sys.stdout.write(row + "\n")
    sys.stdout.flush()

os.system("clear")
draw_keyboard()

# Execute hardware event hook monitor
process = subprocess.Popen(["evtest", dev_path], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)

try:
    for line in process.stdout:
        if "(EV_KEY), code" in line and "value 1" in line:
            match = re.search(r'KEY_([A-Z0-9_]+)', line)
            if match:
                key = match.group(1)
                char = key
                
                # --- Standard Key Mapping Translations ---
                if key == "SPACE": char = "Space"
                elif key == "BACKSPACE": char = "Back"
                elif key == "ENTER": char = "Enter"
                elif key == "TAB": char = "Tab"
                elif key == "CAPSLOCK": char = "Caps"
                elif key in ["LEFTSHIFT", "RIGHTSHIFT"]: char = "Shift"
                elif key in ["LEFTCTRL", "RIGHTCTRL"]: char = "Ctrl"
                elif key in ["LEFTALT", "RIGHTALT"]: char = "Alt"
                elif key == "LEFTMETA": char = "Win"
                elif key == "MENU": char = "Menu"
                elif key == "MINUS": char = "-"
                elif key == "EQUAL": char = "="
                elif key == "LEFTBRACE": char = "["
                elif key == "RIGHTBRACE": char = "]"
                elif key == "BACKSLASH": char = "\\"
                elif key == "SEMICOLON": char = ";"
                elif key == "APOSTROPHE": char = "'"
                elif key == "COMMA": char = ","
                elif key == "DOT": char = "."
                elif key == "SLASH": char = "/"
                elif key == "GRAVE": char = "~"
                elif key == "F": char = "𝐅"
                elif key == "J": char = "𝐉"
                
                # --- Target Isolated Navigation Keys ---
                elif key == "UP": char = "↑"
                elif key == "DOWN": char = "↓"
                elif key == "LEFT": char = "←"
                elif key == "RIGHT": char = "→"
                
                # --- Top Functions & Nav Block Redirect Layers ---
                elif key in ["ESC", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"]:
                    char = "Fn"
                elif key in ["INSERT", "DELETE", "HOME", "END", "PAGEUP", "PAGEDOWN"]:
                    char = "Menu"
                
                draw_keyboard(char)
                
        elif "(EV_KEY), code" in line and "value 0" in line:
            draw_keyboard()
except KeyboardInterrupt:
    process.terminate()
    print("\nExiting cleanly.")

