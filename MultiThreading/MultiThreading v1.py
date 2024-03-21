import uasyncio
import time
import utime
import random
import _thread
from machine import Pin, UART

# Timing
actualTime = 0 # ms
actualValue = 0 # DMX-Value

# Curtain Constants
openTime = 5000 #ms
buffer = 0.1 # -> 10%
bufferedOpenTime = openTime + openTime * buffer

# unused
movingTask = None

# THREAD STUFF
killThread = False
threadRunning = False

# LEDs
lockLED = Pin(17, Pin.OUT)

# BUTTONS
openButton = machine.Pin(19, machine.Pin.IN, machine.Pin.PULL_DOWN)
closeButton = machine.Pin(18, machine.Pin.IN, machine.Pin.PULL_DOWN)

# IF OPENING AND THEN CREATES NEW TASK VOR OPENING SERVO IS RELEASED AND AGAIN PRESSED -> SHUTTERING

lastPercentage = "0%"
def progressBar(prefix = 'Curtain: ', suffix = 'Closed', decimals = 1, length = 20, fill = '#', printEnd = "\r", value = 0):
    global openTime
    """
    Call in a loop to create terminal progress bar
    @params:
        iterable    - Required  : iterable object (Iterable)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """

    total = openTime

    # Progress Bar Printing Function
    def printProgressBar (iteration):
        global lastPercentage
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        if(lastPercentage == percent):
            return False
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix} -> {iteration / total * 255}', end = printEnd)
        lastPercentage = percent
        return True
    
    res = printProgressBar(value)
    if res != False:
    # Print New Line on Complete
        print()

tx_pin = Pin(4, Pin.OUT)
rx_pin = Pin(5, Pin.IN)
uart = UART(1, baudrate=250000, rx=rx_pin)

localOverride = False
lastValue = None
lockButtons = False

async def receiveDMXChannels(channel):
    global lastValue
    global localOverride
    global lockButtons

    pre_dmx_data = uart.read()
    while True:  

        

        while uart.any() == 0:
            pass
        dmx_data = uart.read()
        ### print("PRE", dmx_data[0], len(dmx_data))
        
        dataArray = bytearray(dmx_data)
            
        for i in range(len(dataArray[2:])):
            channelValue = dataArray[2:][i]
            if(i == channel):
                if(lockButtons == False):
                    if openButton.value() == 1:
                        localOverride = True
                        await setCurtainValue(255)
                    
                        continue
                    elif closeButton.value() == 1:
                        localOverride = True
                        await setCurtainValue(0)
                        continue

                if (lastValue == None or lastValue != channelValue):
                    localOverride = False
                    print(channel + 1, ". ->", channelValue)
                    await setCurtainValue(channelValue)
                    lastValue = channelValue
            elif(i == channel + 1):
                if(channelValue > 127):
                    lockButtons = True
                    lockLED.value(1)
                    lastValue = None
                else:
                    lockButtons = False
                    lockLED.value(0)
        uasyncio.sleep_ms(10)

# DMX Loop
async def randomDelayAndValueLoop():
    i = 0
    while True:    
        newValue = int(random.random() * 255)
        delay = int(random.random() * 15000)
        print("-----------------------")
        print("DELAY ", i, ": " + str(delay) + "ms -> ", newValue)
        print("-----------------------")

        await uasyncio.sleep_ms(delay)
        await setCurtainValue(newValue)

        i = i + 1
    
    """ i = 0
    while True:
        # Hier implementieren Sie Ihre DMX-Logik
        print("DMX Loop: ", i, actualTime)
        #val = int(input("DMX-Value: "))

        # Rufen Sie setCurtainValue im Hauptloop auf
        await setCurtainValue(44)

        i = i+1
        print(actualTime)
        await uasyncio.sleep_ms(4000) """

async def openCurtainAsync(deltaTime, newValue):
    global threadRunning

    t1 = utime.ticks_ms()
    await stopThread()
    threadRunning = True
    t2 = utime.ticks_ms()
    print("STAR NEW OPENING THREAD -> THREAD KILL TIME ", t2-t1, "ms")
    openCurtainWrapper(deltaTime, newValue)

def openCurtainWrapper(deltaTime, newValue):
    print("OPEN WRAPPER")
    _thread.start_new_thread(openCurtainThread, (deltaTime, newValue,))

def testThread(deltaTime, newValue):
    global killThread
    while True:
        if killThread == True:
            killThread = False
            print("Opening Thread killed at ", deltaTime)
            _thread.exit()
        print("RUNNING")

def openCurtainThread(deltaTime, newValue):
    global actualTime
    global buffer
    global openTime
    global killThread
    global threadRunning
    print("PRE", actualTime)
    
    last_time = utime.ticks_ms()
    interval = 1

    print("openCurtain", actualTime, min(actualTime + deltaTime, openTime), (min(actualTime + deltaTime, openTime) - actualTime) / 1000, "s")
    print("PRESS OPEN")

    openLED = Pin(20, Pin.OUT)
    openLED.value(1)
    
    while True:

        if killThread == True:
            killThread = False
            print("Opening Thread killed at ", deltaTime)
            _thread.exit()

        current_time = utime.ticks_ms()
    
        if utime.ticks_diff(current_time, last_time) >= interval:
            # Führe deine Aktionen hier aus
            last_time = utime.ticks_add(last_time, interval)
            #actualTime = max(actualTime + interval, openTime)
            actualTime = actualTime + 1
            deltaTime = deltaTime - interval
            #print(actualTime, deltaTime)
            if deltaTime <= 0:
                break
            #print(last_time)

        progressBar(prefix="Opening Curtain", value=actualTime)
    
    # no buffering
    print("RELEASE OPEN: Calculated DMX Value:", actualTime / openTime * 255)
    threadRunning = False
    openLED.value(0)

async def closeCurtainAsync(deltaTime, newValue):
    global threadRunning

    t1 = utime.ticks_ms()
    await stopThread()
    threadRunning = True
    t2 = utime.ticks_ms()
    print("START NEW CLOSING THREAD -> THREAD KILL TIME ", t2-t1, "ms")
    closeCurtainWrapper(deltaTime, newValue)

def closeCurtainWrapper(deltaTime, newValue):
    _thread.start_new_thread(closeCurtainThread, (deltaTime, newValue,))

def closeCurtainThread(deltaTime, newValue):
    global actualTime
    global buffer
    global openTime
    global killThread
    global threadRunning
    
    last_time = utime.ticks_ms()
    interval = 1

    print("closeCurtain", actualTime, max(actualTime - deltaTime, 0), (max(actualTime - deltaTime, 0) + actualTime), "s")
    print("PRESS CLOSE")

    closeLED = Pin(10, Pin.OUT)
    closeLED.value(1)

    while True:

        if killThread == True:
            killThread = False
            print("Closing Thread killed at ", deltaTime)
            _thread.exit()

        current_time = utime.ticks_ms()
    
        if utime.ticks_diff(current_time, last_time) >= interval:
            last_time = utime.ticks_add(last_time, interval)
            #actualTime = max(actualTime - interval, 0)
            actualTime = actualTime - 1
            deltaTime = deltaTime - interval
            #print(actualTime, deltaTime)
            if deltaTime <= 0:
                break

        progressBar(prefix="Closing Curtain", value=actualTime)

    # no buffering
    print("RELEASE CLOSE: Calculated DMX Value:", actualTime / openTime * 255)
    threadRunning = False
    closeLED.value(0)

async def stopThread():
    global killThread
    global threadRunning
    if threadRunning == False:
        print("THREAD NOT RUNNING")
        return
    
    openLED = Pin(20, Pin.OUT)
    openLED.value(0)
    closeLED = Pin(10, Pin.OUT)
    closeLED.value(0)
    
    print("STOP THREAD")
    
    killThread = True
    while killThread == True:
        #asyncio.sleep(0.1)
        pass
    await uasyncio.sleep_ms(1)
    return

nullCount = 0

async def setCurtainValue(newValue):
    print("----- setCurtainValue ------")
    global movingTask
    global actualValue
    global openTime
    global nullCount

    # REMOVE 0 BUG
    if(newValue == 0 and nullCount < 3):
        nullCount = nullCount + 1
        return
    else:
        if actualValue != 0:
            nullCount = 0
    

    if(actualValue == newValue):
        print("SMAME VALUE RETURN")
        return
    
    newTime = (newValue / 255) * openTime

    if(actualTime == newTime):
        # stop
        print("- STOP")
        #stopMovingTask()
        uasyncio.create_task(stopThread())
    elif(actualTime < newTime):
        # open
        print("- OPEN")
        deltaTime = newTime - actualTime
        print(deltaTime)

        #stopMovingTask()
        #movingTask = uasyncio.create_task(openCurtainTask(deltaTime, newValue))
        #uasyncio.create_task(openCurtainAsync(deltaTime, newValue))
        await openCurtainAsync(deltaTime, newValue)
    else:
        # close 
        print("- CLOSE")
        deltaTime = actualTime - newTime

        #stopMovingTask()
        #movingTask = uasyncio.create_task(closeCurtainTask(deltaTime, newValue))
        #uasyncio.create_task(closeCurtainAsync(deltaTime, newValue))
        await closeCurtainAsync(deltaTime, newValue)
   
    actualValue = newValue

def stopMovingTask():
    global movingTask

    if(movingTask != None):
        movingTask.cancel()
    print("RELEASE ALL BTNs")

# Starten Sie die Aufgaben
loop = uasyncio.get_event_loop()
loop.create_task(receiveDMXChannels(0))

# Führen Sie die Schleifen aus
loop.run_forever()

# todo:
# - veränderung von actualTime mit exaktem verändertem faktor
#   threadKillTime
# - stopThread remove sleep
#
# if openening and get new value to open less or more but in opening position
# -> reset deltaTime instead of killingThread
# -> Performance