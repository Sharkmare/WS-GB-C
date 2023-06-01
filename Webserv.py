import os
import asyncio
import websockets

last_sent_frame = None  # Variable to store the last sent frame

async def send_frames(websocket):
    global last_sent_frame  # Declare the variable as global

    while True:
        # Check if key.frame exists
        if os.path.exists("key.frame"):
            with open("key.frame", "r", encoding="utf-8") as frame_file:
                frame_content = frame_file.read()

            if frame_content != "":
                if frame_content != last_sent_frame:
                    await websocket.send(frame_content)
                    last_sent_frame = frame_content  # Update the last sent frame

        await asyncio.sleep(0.1)  # Adjust the interval as needed

async def handle_client(websocket, path):
    await websocket.send("Connected to the server.")

    try:
        receive_task = asyncio.create_task(websocket.recv())
        send_task = asyncio.create_task(send_frames(websocket))

        while True:
            done, pending = await asyncio.wait([receive_task, send_task], return_when=asyncio.FIRST_COMPLETED)

            if receive_task in done:
                data = receive_task.result()
                if data == "exit":
                    break
                else:
                    with open("control.info", "w") as file:
                        file.write(data)

                receive_task = asyncio.create_task(websocket.recv())

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        await websocket.send("Game stopped.")

async def start_server():
    if os.path.exists("rom.info"):
        os.remove("rom.info")
    if os.path.exists("screenshot.info"):
        os.remove("screenshot.info")
    async with websockets.serve(handle_client, "localhost", 8899):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(start_server())
