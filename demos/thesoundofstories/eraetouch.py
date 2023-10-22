from functools import reduce
import mido
import time

# Convert 8-bit bytes to 7-bit format and compute the XOR checksum.
def bitize7chksum(data):
    bitized7Arr = sum(([sum((el & 0x80) >> (j+1) for j, el in enumerate(data[i:min(i+7, len(data))]))] + [el & 0x7F for el in data[i:min(i+7, len(data))]] for i in range(0, len(data), 7)), [])
    return bitized7Arr + [reduce(lambda x, y: x^y, bitized7Arr)]

# Enable API Mode for ERAE Touch.
def enable_api_mode(receiver_prefix_bytes):
    # Construct the SysEx message
    message = [0xF0, 0x00, 0x21, 0x50, 0x00, 0x01, 0x00, 0x01, 0x01, 0x01, 0x04, 0x01] + receiver_prefix_bytes + [0xF7]
    return message

def disable_api_mode():
    # Construct the SysEx message to disable API mode
    message = [0xF0, 0x00, 0x21, 0x50, 0x00, 0x01, 0x00, 0x01, 0x01, 0x01, 0x04, 0x02, 0xF7]
    return message

# Request Zone Boundary for zone 1.
def request_zone_boundary():
    return [0xF0, 0x00, 0x21, 0x50, 0x00, 0x01, 0x00, 0x01, 0x01, 0x01, 0x04, 0x10, 0x01, 0xF7]

# Clear Display for zone 1.
def clear_zone_display():
    return [0xF0, 0x00, 0x21, 0x50, 0x00, 0x01, 0x00, 0x01, 0x01, 0x01, 0x04, 0x20, 0x01, 0xF7]

# Draw a pixel in zone 1.
def draw_pixel(xpos, ypos, red, green, blue):
    return [0xF0, 0x00, 0x21, 0x50, 0x00, 0x01, 0x00, 0x01, 0x01, 0x01, 0x04, 0x21, 0x01] + [xpos, ypos, red, green, blue] + [0xF7]

# Draw a rectangle in zone 1.
def draw_rectangle(xpos, ypos, width, height, red, green, blue):
    return [0xF0, 0x00, 0x21, 0x50, 0x00, 0x01, 0x00, 0x01, 0x01, 0x01, 0x04, 0x22, 0x01] + [xpos, ypos, width, height, red, green, blue] + [0xF7]

def draw_image(zone, xpos, ypos, width, height, rgb_data):
    # Convert RGB data to 7-bit format
    rgb_data_bitized = bitize7chksum(rgb_data)
    message = [0xF0, 0x00, 0x21, 0x50, 0x00, 0x01, 0x00, 0x01, 0x01, 0x01, 0x04, 0x23, zone, xpos, ypos, width, height] + rgb_data_bitized + [0xF7]
    return message

def split_image_data(rgb_data):
    # 3 bytes per pixel, so 32 pixels = 96 bytes
    MAX_BYTES = 96
    return [rgb_data[i:i+MAX_BYTES] for i in range(0, len(rgb_data), MAX_BYTES)]

# Function to draw a rectangle
def draw_rectangle(zone, x, y, width, height, r, g, b):
    header = [0xF0, 0x00, 0x21, 0x50, 0x00, 0x01, 0x00, 0x01, 0x01, 0x01, 0x04, 0x22]
    footer = [0xF7]
    
    message = header + [zone, x, y, width, height, r, g, b] + footer
    return message

# Function to handle finger stream data
def handle_fingerstream_data(data):
    prefix = data[1:-3]  # Assuming receiver prefix bytes are between F0 and XYZ data
    finger_data = data[-3:-1]  # Assuming XYZ data is the second last before checksum

    return {
        "prefix": prefix,
        "finger_data": finger_data
    }

# Example usage:
receiver_prefix_bytes = [0x10, 0x11]  # Example prefix bytes. Adjust as needed.
print(f"print enable api mode: {enable_api_mode(receiver_prefix_bytes)}")
print(f"request_zone_boundary: {request_zone_boundary()}")
print(f"clear zone display: {clear_zone_display()}")
print(draw_pixel(5, 5, 127, 0, 0))  # Draw a red pixel at position (5,5) in zone 1.

def send_sysex_message(msg_list):
    # Create a MIDI port to send messages
    with mido.open_output() as outport:
        # Create a SysEx message from the list and send
        sysex_msg = mido.Message("sysex", data=msg_list[1:-1])  # Excluding the start and end bytes (240 and 247)
        outport.send(sysex_msg)

def send_sysex_message_with_delay(msg_list, delay=0.7):  # default delay is 0.5 seconds
    send_sysex_message(msg_list)
    time.sleep(delay)

# Example usage:
# receiver_prefix_bytes = [0x10, 0x11]  # Example prefix bytes. Adjust as needed.
# send_sysex_message(enable_api_mode(receiver_prefix_bytes))
# send_sysex_message(request_zone_boundary())
# send_sysex_message(clear_zone_display())
# send_sysex_message(draw_pixel(5, 5, 127, 0, 0))  # Draw a red pixel at position (5,5) in zone 1.
# send_sysex_message(clear_zone_display())

# # Testing
# rectangle_message = draw_rectangle(1, 10, 10, 50, 50, 127, 0, 0)
# print(rectangle_message)
#send_sysex_message(rectangle_message)
# send_sysex_message(clear_zone_display())

# data = [0xF0] + [0x01, 0x02, 0x03, 0x04] + [10, 20, 30] + [0xF7]
# fingerstream = handle_fingerstream_data(data)
# print(fingerstream)

def execute_sequence_with_image():
    receiver_prefix_bytes = [0x10, 0x11]  # Example prefix bytes.
    
    send_sysex_message_with_delay(disable_api_mode())
    send_sysex_message_with_delay(enable_api_mode(receiver_prefix_bytes))
    send_sysex_message_with_delay(clear_zone_display())
    send_sysex_message_with_delay(draw_pixel(5, 5, 127, 0, 0))

    # Example image data for a 2x2 image
    rgb_data = [0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0xFF, 0x00, 0x00, 0x00, 0xFF]
    
    sub_images = split_image_data(rgb_data)
    for sub_image in sub_images:
        send_sysex_message_with_delay(draw_image(1, 5, 3, 2, 2, sub_image))

    send_sysex_message_with_delay(draw_rectangle(1, 10, 10, 50, 50, 127, 0, 0))

execute_sequence_with_image()
