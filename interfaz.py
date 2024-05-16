import os
import pygame
import serial
import subprocess

# Initialize Pygame
pygame.init()

# Initialize joystick
joystick = pygame.joystick.Joystick(0)
joystick.init()

# Initialize serial communication
ser = serial.Serial('/dev/serial0', 9600)

# Start Hagen emulator
hagen_path = "/path/to/hagen/hagen-0.9.1-linux-x86_64/hagen"
subprocess.Popen([hagen_path, "-fullscreen"])

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Read joystick input
    buttons = joystick.get_numbuttons()
    for i in range(buttons):
        if joystick.get_button(i):
            ser.write(f"JOYSTICK_{i}\n".encode())

    # Read ROMs from USB
    line = ser.readline().decode().strip()
    if line:
        if line.startswith("ROM_"):
            rom_path = line[4:]
            subprocess.Popen(["qemu-system-x86", "64", "-cdrom", rom_path, "-m", "1024", "-smp", "2", "-boot", "d"])

# Clean up
ser.close()
pygame.quit()