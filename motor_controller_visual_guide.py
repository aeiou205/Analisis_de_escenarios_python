import cv2
import os
import time
import serial
from manager_orders import Manager_Picker_Orders, POLICY


class Move_Motors: 

    __rotation_degs = {
            11: (158),
            21: (145),
            31: (125),
            41: (53),
            51: (5),
            12: (132),
            22: (120),
            32: (90),
            42: (40),
            52: (14),
            13: (107),
            23: (92),
            33: (68),
            43: (36),
            53: (5),
        }   


    __serial_comm = None

    def __init__(self, port, time_sleep = 2):
        self.__port = port
        self.__time_sleep = time_sleep
        # self.setup()

    def setup(self):
        print("\n"*2)
        print("".center(50,"-"))
        print("\n")
        print("setup connection to motors ..".center(50," "))
        print("\n")

        print(f"try to connecto to port {self.__port}".center(50," "))
        self.__serial_comm = serial.Serial(self.__port, 9600, timeout=1)
        time.sleep(2)

        print("conection stablished ..".center(50," "))

        print("\n")
        print("".center(50,"-"))
        print("\n"*2) 

    def target_location( self, location, qty):
        """_summary_
            send to physical system the target location to set the visual reference
            and display the visual code 
        Args:
            location (code str): the location to take the items and the spot to display the visual code
            the association codes atach to the place are organized as:
                |----|----|----|
                | 1  |  2 |  3 | 
                |----|----|----|
                | 4  | 5  | 6  | 
                |----|----|----|
                | 7  | 8  | 9  | 
                |----|----|----|
                | 10 | 11 | 12 | 
                |----|----|----|
                | 13 | 14 | 15 |
                |----|----|----|

            led_counter (_type_): the number of items to take. the code to display is:
                #items         physical lasser          visual code
                    1           1 dot ON                    0*
                    2           2 dot ON                    **
                    3           1 dot ON & 1 dot BLINK      *+
                    4           1 dot BLINK & 1 dot ON      +*
                    5           1 dot BLINK & 1 dot BLINK   ++

                note:   - the symbol * denote permant led ON
                        - the symbol + denote blink led ON


        ***********************************
        *         messages structure      *
        ***********************************
        *
        *      I:X:THETA:D
        *      1:0:100:2
        *     
        *      I: header message
        *      X: num motor, a digit in range 0-3
        *      THETA: angle to set the motor, a number in range 0-180
        *      D: digit to display in the visual guide, a digit in range 0-5"""

        
        num_motor = (location%10)
        degs = self.__rotation_degs[location]

        cmd2motors = "A:"+str(num_motor)+":"+str(degs)+":"+str(qty)
        self.__serial_comm.write( str.encode(f'{cmd2motors}') )
        time.sleep(self.__time_sleep)
        
        print(cmd2motors)

def main():

    theVisualGuide = Move_Motors(port = 'COM3', time_sleep=2)

    manager_orders =  Manager_Picker_Orders( file_orders="orders_new.csv", policy = POLICY.BY_ORDER_SEQUENTIAL, max_orders=6 )

    while True:
        item = manager_orders.pick_item()
        if item is not None:
            print(item)
            # TODO: send command to arduino
            theVisualGuide.target_location(item.loc_in_rack, item.qty)
            time.sleep(4)
            
        else:
            break


if __name__== "__main__":
    main()




