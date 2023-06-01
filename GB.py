import os
import time
from PIL import Image, ImageChops
from pyboy import PyBoy, WindowEvent
from io import BytesIO

# Set the path to the directory containing the SDL DLLs
sdl_dll_directory = "./libraries"

# Set the environment variable
os.environ["PYSDL2_DLL_PATH"] = sdl_dll_directory

# Create a PyBoy instance
gameboy = PyBoy("./RomExample.rom",disable_renderer=False)

previous_frame = None
pressed_buttons = set()
release_delay = 2  # Delay in frame ticks

resize_percent = 100  # Adjust the percentage as needed

try:
    frame_count = 0
    changed_data_count = 0
    skip_write_frames = 0  # Number of frames to skip writing if not enough changes
    max_skip_frames = 1  # Maximum number of frames to skip

    while not gameboy.tick():
        # Release previously pressed buttons
        for button in pressed_buttons:
            gameboy.send_input(button)
        pressed_buttons.clear()

        # Update the display
        frame_count += 1

        if frame_count % 1 == 0:
            # Take a screenshot of the Game Boy window
            screenshot_buffer = BytesIO()
            gameboy.botsupport_manager().screen().screen_image().save(screenshot_buffer, format="PNG")
            screenshot_buffer.seek(0)

            # Load the screenshot image
            screenshot = Image.open(screenshot_buffer)

            # Resize the screenshot
            new_width = int(screenshot.width * resize_percent / 100)
            new_height = int(screenshot.height * resize_percent / 100)
            resized_screenshot = screenshot.resize((new_width, new_height))

            # Convert the resized screenshot to a text-based representation
            text_representation = ""
            current_color = None
            for y in range(resized_screenshot.height):
                for x in range(resized_screenshot.width):
                    pixel = resized_screenshot.getpixel((x, y))
                    r, g, b = pixel[:3]
                    color_tag = f"<color=#{r:02x}{g:02x}{b:02x}>"
                    if color_tag != current_color:
                        if current_color:
                            text_representation += "</color>"
                        current_color = color_tag
                        text_representation += current_color
                    text_representation += "█"
                text_representation += "\n"

            if previous_frame is not None:
                # Calculate the difference between the current and previous frames
                diff_image = ImageChops.difference(resized_screenshot, previous_frame)
                changed_data = diff_image.getbbox()
                if changed_data:
                    # Count the number of changed pixels
                    changed_data_count += sum([(y2 - y1 + 1) * (x2 - x1 + 1) for x1, y1, x2, y2 in [changed_data]])
                else:
                    changed_data_count = 0

                if changed_data_count > 0:
                    # Reset the skip counter if changes occurred
                    skip_write_frames = max_skip_frames

                if skip_write_frames > 0:
                    # Decrement the skip counter
                    skip_write_frames -= 1

                if skip_write_frames == 0:
                    # Save the text representation to the key.frame file
                    with open("key.frame", "w", encoding="utf-8") as file:
                        file.write(text_representation)

            previous_frame = resized_screenshot

        # Read commands from control.info file if it exists
        if os.path.exists("control.info"):
            with open("control.info", "r") as control_file:
                commands = control_file.readlines()
            os.remove('control.info')
            # Process commands
            button_map = {
                "UP": (WindowEvent.PRESS_ARROW_UP, WindowEvent.RELEASE_ARROW_UP),
                "DOWN": (WindowEvent.PRESS_ARROW_DOWN, WindowEvent.RELEASE_ARROW_DOWN),
                "LEFT": (WindowEvent.PRESS_ARROW_LEFT, WindowEvent.RELEASE_ARROW_LEFT),
                "RIGHT": (WindowEvent.PRESS_ARROW_RIGHT, WindowEvent.RELEASE_ARROW_RIGHT),
                "START": (WindowEvent.PRESS_BUTTON_START, WindowEvent.RELEASE_BUTTON_START),
                "SELECT": (WindowEvent.PRESS_BUTTON_SELECT, WindowEvent.RELEASE_BUTTON_SELECT),
                "A": (WindowEvent.PRESS_BUTTON_A, WindowEvent.RELEASE_BUTTON_A),
                "B": (WindowEvent.PRESS_BUTTON_B, WindowEvent.RELEASE_BUTTON_B)
            }
            for command in commands:
                command = command.strip()
                if command in button_map:
                    press_event, release_event = button_map[command]
                    gameboy.send_input(press_event)
                    pressed_buttons.add(release_event)
                elif command == "EXIT":
                    # Process EXIT command
                    gameboy.stop()
                    break
                elif command == "PAUSE":
                    # Process PAUSE command
                    gameboy.send_input(WindowEvent.PAUSE_TOGGLE)

except Exception as e:
    print(f"Error: {str(e)}")
finally:
    gameboy.stop()
