import cv2
from pyzbar import pyzbar
import threading
import ctypes
import time
import sys
import string

from evdev import InputDevice
from select import select

cardreader_input = "X^1234567890XXXXqwertzuiopXXXXasdfghjklXXXXXyxcvbnmXXXXXXXXXXXXXXXXXXXXXXX"


class qr_thread(threading.Thread):
    """
    Class for the thread that reads a QR-code.
    """
    def __init__(self, name, result):
        """
        Set the appropriate values.
        """
        threading.Thread.__init__(self)
        self.name = name
        self.result = result
    
    def run(self):
        """
        Read the camera continuosly and add the read code
        to the result dictionary.
        """
        # initalize the cam
        try:
            cap = cv2.VideoCapture(0)
            # initialize the cv2 QRCode detector
            detector = cv2.QRCodeDetector()
            while True:
                _, img = cap.read()

                barcodes = pyzbar.decode(img)
                if barcodes:
                    print("Decoded code =", barcodes[0].data , barcodes[0].data.decode("utf-8"))
                    self.result[self.name] = barcodes[0].data.decode("utf-8")
                    break

                if cv2.waitKey(1) == ord("q"):
                    break
        except:
            print(self.name, "Exception")
        finally:
            cap.release()
            print("released camera")
            sys.exit(0)
            
    def get_id(self): 
        """
        returns id of the respective thread 
        """
        if hasattr(self, '_thread_id'): 
            return self._thread_id 
        for id, thread in threading._active.items(): 
            if thread is self: 
                return id
        
    def raise_exception(self):
        """
        Raise an exception, ending the execution of the thread.
        """
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit)) 
        if res > 1: 
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0) 
        print(self.name, 'Raise exception method called') 
        
        
class card_thread(threading.Thread):
    """
    Class for the thread that reads an RFID reader.
    """
    def __init__(self, name, result, dev):
        """
        Set the appropriate values.
        """
        threading.Thread.__init__(self)
        self.name = name
        self.result = result
        self.dev = dev
    
    def run(self):
        """
        Read the RFID reader, adding the resulting string to the
        result dictionary and end execution.
        """
        res = ""
        try:
            while True:
                r,w,x = select([self.dev], [], [], 0.25)
                try:
                    for event in self.dev.read():
                        if event.type==1 and event.value==1:
                            #print( keys[ event.code ] )
                            if cardreader_input[event.code] in string.digits:
                                res += cardreader_input[event.code]
                            else:
                                self.result[self.name] = res
                                print(res, self.result)
                                print(self.name, "has exited")
                                sys.exit(0)
                except BlockingIOError:
                    pass
        
        except:
            print(self.name, "has exception")
        finally:
            print(self.name, "has exited")
            sys.exit(0)
        
            
    def get_id(self): 
        """
        returns id of the respective thread 
        """
        if hasattr(self, '_thread_id'): 
            return self._thread_id 
        for id, thread in threading._active.items(): 
            if thread is self: 
                return id
        
    def raise_exception(self):
        """
        Raise an exception in the thread, ending execution.
        """
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, ctypes.py_object(SystemExit)) 
        if res > 1: 
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0) 
        print(self.name, 'Raise exception method called') 
        
        
def read_input(deadline, dev):
    """
    Starts the QR-reader and the card reader and lets both
    accept input, returning the input from the device that
    outputs first.
    """
    
    # Construct empty result dictionary
    result = {}
    # Start the two threads, with appropriate names
    card_reader = card_thread("card", result, dev)
    qr = qr_thread("qr", result)
    card_reader.start()
    qr.start()
    
    # Start timer
    start = time.time()
    
    # Wait for one of the devices to output or for the deadline
    while (not result) and time.time() - start <= deadline:
        pass
    
    # Raise exceptions for the two threads, ending their execution
    qr.raise_exception()
    card_reader.raise_exception()
    
    # Wait for camera to exit
    time.sleep(1)
    
    # Return the value, UGLY, assuming only one has returned a value.
    if result:
        for value in result.values():
            return value
    else:
        return -1
    
    
if __name__ == "__main__":
    dev_path = "/dev/input/by-id/usb-StrongLink_USB_CardReader-event-kbd"
    dev = InputDevice(dev_path)
    
    for i in range(3):
        print(read_input(10, dev))
    
    print("exiting main program")
    
    

