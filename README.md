# WS-GB-C
Websocket based Gameboy/Color emulation

# TODO:

Write version that handles multiple WS for efficient sendng of chunked data instead of pushing all data over 1 WS
This should both update more efficiently but also mean we can partially redraw the screen. Hopefully without tearing
