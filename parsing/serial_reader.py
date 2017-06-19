import serial
import io
from send_to_server import server_post_data
import pylab as plt
import numpy as np

# packet information
start_delimiter = [b"\xdd", b"\xcc", b"\xbb", b"\xaa"]
end_delimiter = [b"\xaa", b"\xbb", b"\xcc", b"\xdd"]

# expected_payload_size = 26
expected_payload_size = 26


# global variables
start_match_index = 0
end_match_index = 0

# packet location flags
start_packet_flag = False
end_packet_flag = False
in_packet_flag = False

# animated plot
plt.ion()

# empty data for initialization
temp_list = [0] * 10
light_list = [0] * 10
ax1=plt.axes()

# -------------------  make plot
plt.figure(1)
# line 1
plt.subplot(211)
plt.ylim([0,6000]) # set the y-range to 10 to 40
plt.ylabel('Light (#)')
plt.title('Sensor Data (metric / last 10 seconds)')
line, = plt.plot(light_list)
# line 2
plt.subplot(212)
line2, = plt.plot(temp_list)
plt.ylim([15,35]) # set the y-range to 10 to 40
plt.ylabel('Temperature (*C)')
# -------------------


# results information
payload_bytes = []
payload_index = 0

# see if we have a match for the start delimiter
def check_start_delim(cur_byte):
    global start_match_index
    global start_packet_flag

    if cur_byte == start_delimiter[start_match_index]:
        start_match_index = start_match_index + 1
        if start_match_index == len(start_delimiter):
            # we have matched the start delimiter
            print("|start_packet|")
            start_packet_flag = True
            start_match_index = 0
            end_packet_flag = False
        else:
            start_packet_flag = False
    else:
        start_match_index = 0
        start_packet_flag = False


# see if we have a match for the end delimiter
def check_end_delim(cur_byte):
    global end_match_index
    global end_packet_flag

    if cur_byte == end_delimiter[end_match_index]:
        # ("match", cur_byte, "==", end_delimiter[end_match_index])
        end_match_index = end_match_index + 1
        if end_match_index == len(end_delimiter):
            end_packet_flag = True
            start_packet_flag = False
            end_match_index = 0
        else:
            end_packet_flag = False   # still in the the packet
    else:
        end_match_index = 0
        end_packet_flag = False


# build message packet
def create_message(message_byte_list):
    message_string = b''
    for byte in message_byte_list:
        message_string += byte
    return message_string.decode("utf-8")


# print final reults from packet / update graph
def print_packet():
    global payload_bytes
    global graph_flag
    global graph
    global plt
    length = int.from_bytes((payload_bytes[0]+payload_bytes[1]), byteorder='little')
    seq_num = int.from_bytes((payload_bytes[2]+payload_bytes[3]), byteorder='little')
    temp = int.from_bytes((payload_bytes[4]+payload_bytes[5]), byteorder='little')
    light = int.from_bytes((payload_bytes[6]+payload_bytes[7]), byteorder='little')
    message = create_message(payload_bytes[8:23])
    crc = int.from_bytes((payload_bytes[24]+payload_bytes[25]), byteorder='little')

    result_string = ( "{\n"
        + "\tlength: "+ str(length) + "\n"
        + "\tseqnum: "+ str(seq_num) + "\n"
        + "\ttemp: "+ str(temp) + "\n"
        + "\tlight: "+ str(light) + "\n"
        + "\tmessage: "+ str(message) + "\n"
        + "\tcrc: "+ str(crc) + "\n"
        + "}"
    )
    payload_bytes = []

    # print("hi")
    print(result_string)

    temp_list.append(temp)
    del temp_list[0]

    light_list.append(light)
    del light_list[0]

    # update light data
    line2.set_xdata(np.arange(len(temp_list)))
    line2.set_ydata(temp_list)

    # update light data
    line.set_xdata(np.arange(len(light_list)))
    line.set_ydata(light_list)

    plt.pause(0.1)
    plt.draw() # update the plot

    server_post_data(seq_num, temp, light, message)


# capture all bytes in the packet as a list
def build_packet(cur_byte):
    global payload_bytes
    global payload_index
    payload_bytes.append(cur_byte)
    payload_index += 1


# set packet globals back to a zero state
def reinitialize_globals():
    global payload_bytes
    global payload_index
    payload_bytes = []
    payload_index = 0


# Check packet size
# Return: T|F
def packet_check_size(payload_index, expected_payload_size):
    if payload_index == expected_payload_size:
        return True
    else:
        return False


# Check packet declaration
# Return: T|F
def packet_check_declaration(payload_bytes):
    if int.from_bytes(payload_bytes[0], byteorder='little') == 22 and int.from_bytes(payload_bytes[1], byteorder='little') == 0:
        return True
    else:
        return False


# Calculate CRC and compare to expected CRC
# Return: T|F
def packet_check_CRC(payload_bytes):
    expected_CRC = int.from_bytes((payload_bytes[24]+payload_bytes[25]), byteorder='little')

    # strip length from front and crc from back
    data_to_calc_crc = payload_bytes[2:23]

    # index tracking
    i = 1
    calculated_CRC = 0
    for index_byte in data_to_calc_crc:
        # convert byte to int
        index_data = int.from_bytes(index_byte, byteorder='little')
        calculated_CRC += (index_data * i)
        i+=1

    if calculated_CRC == expected_CRC:
        return True
    else:
        return False


# Handle the extra char from the delimiter tracking
def adjust_payload():
    global payload_bytes
    global payload_index
    payload_bytes = payload_bytes[1:-5]   #JACK: 5:-9
    payload_index = len(payload_bytes)


# process the captured payload
def process_payload_wrapper():
    global payload_bytes
    global payload_index
    global expected_payload_size

    global start_packet_flag
    global end_packet_flag

    start_packet_flag = False
    end_packet_flag = False

    adjust_payload()

    size_bool = packet_check_size(payload_index, expected_payload_size)
    if not size_bool:
        print("incorrectly sized packet")
        print("packet is = ", payload_index, "| expected = ", expected_payload_size)
        print(payload_bytes)
        reinitialize_globals()
        return


    # check declaration
    declaration_bool = packet_check_declaration(payload_bytes)
    if not declaration_bool:
        print("incorrectly declared packet")
        reinitialize_globals()
        return


    CRC_bool = packet_check_CRC(payload_bytes)
    if not CRC_bool:
        print("CRC is wrong")
        print("calculated CRC = ", calculated_CRC, "| expected = ", expected_CRC)
        reinitialize_globals()
        return

    # Packet is correct!
    print_packet()
    print("|end_packet(processed)|")


def process_bytes(cur_byte):
    global start_packet_flag
    global end_packet_flag
    global payload_bytes

    #print(start_packet_flag)
    if not start_packet_flag:
        check_start_delim(cur_byte)

    if start_packet_flag:
        check_end_delim(cur_byte)

    if start_packet_flag and not end_packet_flag:
        # found start sequnce, but haven't reached end yet
        build_packet(cur_byte)
    elif start_packet_flag and end_packet_flag:
        process_payload_wrapper()

    else:
        # not in the packet
        reinitialize_globals()


# /dev/tty.usbmodem14122
# Will need to be adjusted depending on computer
ser = serial.Serial('/dev/tty.usbmodem14122', baudrate=9600)


while True:
    x = ser.read()
    process_bytes(x)
