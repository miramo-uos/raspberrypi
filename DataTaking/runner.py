from serial import Serial
import Adafruit_DHT
from db_connector import query
from tty_connector import PMS7003, MIRA
from time import time, sleep
import os
import glob
import subprocess

ttylist = glob.glob("/dev/ttyUSB*")
MIRAPORT = ttylist[0]
PMSPORT = ttylist[1]

def main():
    time0 = time()
    radontime0 = time()
    serial_arg = "cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2"
    dev_serial = subprocess.check_output(serial_arg, shell=True)
    dev_serial = int(dev_serial, 16) # Hexadecimal to decimal 4byte integer
    mira = MIRA(MIRAPORT)
    ser = Serial(PMSPORT, 9600, timeout=1)
    dust = PMS7003()
    port_error_counter = 0
    is_first = True
    reset_flag = False
    while True:
        h, t = Adafruit_DHT.read_retry(Adafruit_DHT.DHT22, 4)
        if h is not None and t is not None:
            print("Temperature = {0:0.1f}*c Humidity = {1:0.1f}%".format(t,h))
        else:
            print('read error')
        ser.flushInput()
        buffer = ser.read(1024)

        if(dust.protocol_chk(buffer)):
            print("DATA read success")
            if time() - time0 > 60:
                d1_0, d2_5, d10_0 = dust.print_serial(buffer)
                if time() - radontime0 > 60*60:
                    radon = mira.get_value()
                    print(f'radon: {radon}')
                    radontime0 = time()
                else:
                    if is_first:
                        radon = mira.get_value()
                        is_first = False
                    else:
                        radon = None
                query(dev_serial=dev_serial, radon=radon, temp=t, hum=h, d1_0=d1_0, d2_5=d2_5, d10_0=d10_0)
                time0 = time()
                port_error_counter = 0
            else:
                print('Updating interval is 60s.')
        else:
            print("DATA read fail...")
            port_error_counter += 1
            if port_error_counter > 10:
                if not reset_flag:
                    del ser
                    del mira
                    ser = Serial(MIRAPORT, 9600, timeout=1)
                    mira = MIRA(PMSPORT)
                    reset_flag = True
                    port_error_counter = 0
                else:
                    os.system('sudo shutdown -r now')
        sleep(60)

    ser.close()

if __name__ == '__main__':
    main()
