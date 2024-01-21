from machine import UART, Pin

tx_pin = Pin(4, Pin.OUT)
rx_pin = Pin(5, Pin.IN)
uart = UART(1, baudrate=250000, rx=rx_pin)

def receiveDMXChannels(channel):
    while True:    
        pre_dmx_data = uart.read()
        while uart.any() == 0:
            pass
        dmx_data = uart.read()
        ### print("PRE", dmx_data[0], len(dmx_data))
        
        dataArray = bytearray(dmx_data)
            
        for i in range(len(dataArray[2:])):
            channelValue = dataArray[2:][i]
            if(i == channel):
                print(channel + 1, ". ->", channelValue)

receiveDMXChannels()