from machine import UART, Pin

# Konfiguriere UART für RS-485-Kommunikation
tx_pin = Pin(4, Pin.OUT)  # Oder Pin(1), Pin(4), etc.
rx_pin = Pin(5, Pin.IN)
uart = UART(1, baudrate=250000, rx=rx_pin)

def pulse(l, t):

    for i in range(20):

        l.duty(int(math.sin(i / 10 * math.pi) * 500 + 500))

        time.sleep_ms(t)

def receive_specific_dmx_channels(channel_numbers):
    num_channels = max(channel_numbers)  # Maximaler Kanal, der verarbeitet wird
    while True:
        # Warte auf Start des DMX-Rahmens (Break-Signal und Mark Before Break)
        ### print("RUNNING")
        
        predmx_data = uart.read()
        while uart.any() == 0:
            pass
        dmx_data = uart.read()
        ### print("PRE", dmx_data[0], len(dmx_data))
        
        #while True:
        #    if dmx_data is not None and dmx_data[0] == 0:
        #        print("START VALUE:", dmx_data[0])
        #        break
        #    else:
        #        dmx_data = uart.read()
        dataArray = bytearray(dmx_data)
            
        for i in range(len(dataArray[2:])):
            channelValue = dataArray[2:][i]
            if(i == 0):
                #ledPin = Pin(15, Pin.OUT)
                #pwm12 = machine.PWM(ledPin)
                #pwm12.freq(500)
                #pwm12.duty_u16(channelValue * 4)
                print(channelValue)
            
            #print(i + 1, channelValue)

        '''while True:
            #mbb_byte = uart.read(1)
            #print(mbb_byte)
            if mbb_byte is not None:
                print(mbb_byte, mbb_byte[0])
            else:
                print("-------")
            if mbb_byte is not None and mbb_byte[0] == 0xFF:
                print("Mark Before Break:", mbb_byte[0])
                break  # Warte auf 0xFF, das das Mark Before Break (MBB)-Signal darstellt'''

        # Lesen der gewünschten Kanäle
        #dmx_data = uart.read(num_channels)
        #dmx_data = uart.read()

        # Verarbeite die empfangenen Daten für die gewünschten Kanäle
        '''if len(dmx_data) == num_channels:
            for channel_number in channel_numbers:
                channel_value = dmx_data[channel_number - 1]
                print(f"DMX Kanal {channel_number} Wert: {channel_value}")'''

# Beispiel: Auslesen der Kanäle 1, 3 und 221
receive_specific_dmx_channels(channel_numbers=[1, 3])

