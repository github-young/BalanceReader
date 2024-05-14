import serial
import time
import datetime as dt
import re
import io

offset_utc_plus_8 = dt.timezone(dt.timedelta(hours=8))


def get_now_time():
    return dt.datetime.now(dt.UTC).astimezone(offset_utc_plus_8)


def clean_ser_data(data_raw):
    data_clean = re.sub("[\r\nUS ]", "", data_raw)
    try:
        data = data_clean.split("g")[-2]
    except:
        data = "Error"
    return data, data_raw


def clean_sio_data(data_raw):
    try:
        data = re.sub("[\r\nUSg ]", "", data_raw)
    except:
        data = "Error"
    return data, data_raw


def read_from_ser(ser):
    now = get_now_time().strftime("%Y%m%d-%H:%M:%S.%f")[:-3]
    data_raw = ser.readline().decode('utf-8').strip()
    data, data_debug = clean_ser_data(data_raw)
    print(f"{now}, {data}, {data_debug}")
    ser.flushInput()
    ser.flushOutput()


def read_from_sio(ser):
    now = get_now_time().strftime("%Y%m%d-%H:%M:%S.%f")[:-3]
    data_raw = ser.readline()
    data, data_debug = clean_sio_data(data_raw)
    # return data_raw
    # print(f"{now}, {data}, {data_debug}")
    return data, data_debug, now


# Define the serial port parameters
port = '/dev/ttyS0'
baud_rate = 9600
parity = serial.PARITY_NONE
timeout = 0
record_interval = 1
second_passed = 0 - record_interval*2
total_time = 60*30 # seconds

# Open the serial port
ser = serial.Serial(port, baud_rate, parity=parity, timeout=timeout)
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser), encoding="utf-8", newline="\r")

first_line = "Time/s,Mass/g,Timestamp,Raw"
print(first_line)

# Create a loop that records data at the specified time interval
while second_passed <= total_time:
    loop_start_time = time.monotonic()
    # print(read_from_sio(sio))
    data, data_debug, now = read_from_sio(sio)
    print(f"{second_passed:<5},{data},{now},{data_debug}")
    second_passed += record_interval
    # Wait for the specified time interval before recording the next data point
    time.sleep(record_interval - time.monotonic() % 1)
    # time.sleep(record_interval - (time.monotonic() - loop_start_time))
