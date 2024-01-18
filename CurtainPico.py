import uasyncio
import time
import utime

# Timing
actualTime = 15000 # ms
actualValue = 255 # DMX-Value

# Curtain Constants
openTime = 15000 #ms
buffer = 0.1 # -> 10%
bufferedOpenTime = openTime + openTime * buffer

movingTask = None

# IF OPENING AND THEN CREATES NEW TASK VOR OPENING SERVO IS RELEASED AND AGAIN PRESSED -> SHUTTERING

async def get_user_input():
    loop = uasyncio.get_event_loop()
    print("--- DMX-Value: ---")
    return await loop.run_in_executor(None, input)

async def main():
    #while True:
    dmxValue = input("DMX-Value:")
    #dmxValue2 = input("DMX Val 2:")
    #dmxValue3 = input("DMX Val 3:")
    task = setCurtainValue(int(dmxValue))
    await uasyncio.sleep(5)
    print("AFTER")
    #await uasyncio.sleep(5)
    #uasyncio.create_task(setCurtainValue(255))
    #await uasyncio.sleep(3000)
    #await uasyncio.sleep(500000)
    #setCurtainValue(int(dmxValue2))
    #await uasyncio.sleep(5)
    #setCurtainValue(int(dmxValue3))

    """ while True:
        
        dmxValue = await get_user_input()
        print(f"Received DMX-Value: {dmxValue}")
        setCurtainValue(int(dmxValue))
        dmxValue = await get_user_input()
        print(f"Received DMX-Value: {dmxValue}")
        setCurtainValue(int(dmxValue)) """
    
    # duration 15s
    """ uasyncio.create_task(setCurtainValue(255))
    print("AFTER START")
    await uasyncio.sleep(1)
    print("AFTER DELAY")
    uasyncio.create_task(setCurtainValue(100))
    await uasyncio.sleep(1000)
    print("AFTER 2nd run") """

async def openCurtainTask(deltaTime, newValue):
    global actualTime
    global buffer
    global openTime
    print("PRE", actualTime)

    start_time = utime.ticks_ms()
    startActualTime = actualTime
    last_loop_time = start_time
    
    last_time = utime.ticks_ms()
    interval = 1

    print("openCurtain", startActualTime, min(startActualTime + deltaTime, openTime), (min(startActualTime + deltaTime, openTime) - startActualTime) / 1000, "s")
    print("PRESS OPEN")
    
    while True:
        current_time = utime.ticks_ms()
    
        if utime.ticks_diff(current_time, last_time) >= interval:
            # Führe deine Aktionen hier aus
            last_time = utime.ticks_add(last_time, interval)
            #actualTime = max(actualTime + interval, openTime)
            actualTime = actualTime + 1;
            deltaTime = deltaTime - interval;
            #print(actualTime, deltaTime)
            if deltaTime <= 0:
                break
            #print(last_time)
    
    # no buffering
    '''while actualTime < min(startActualTime + deltaTime, openTime):
        end_time = time.ticks_ms()
        loop_duration = end_time - last_loop_time
        # aT cant buffer
        actualTime = min(actualTime + loop_duration, openTime)
        last_loop_time = end_time
        #print(loop_duration)
        print(actualTime)

    # buffering
    if(newValue == 255):
        bufferDuration = openTime * buffer
        start_time = time.ticks_ms()
        last_loop_time = start_time
        print("BUFFERING")
        while(bufferDuration > 0):
            end_time = time.ticks_ms()
            loop_duration = end_time - last_loop_time
            bufferDuration = bufferDuration - loop_duration
            last_loop_time = end_time
            #print(loop_duration, bufferDuration)
        print("BUFFERING STOPPED")'''

    print("RELEASE OPEN: Calculated DMX Value:", actualTime / openTime * 255)

async def closeCurtainTask(deltaTime, newValue):
    global actualTime
    global buffer
    global openTime

    start_time = utime.ticks_ms()
    startActualTime = actualTime
    last_loop_time = start_time
    
    last_time = utime.ticks_ms()
    interval = 1

    print("closeCurtain", startActualTime, max(startActualTime - deltaTime, 0), (max(startActualTime - deltaTime, 0) + startActualTime), "s")
    print("PRESS CLOSE")

    # no buffering
    '''while actualTime > max(startActualTime - deltaTime, 0):
        end_time = time.ticks_ms()
        loop_duration = end_time - last_loop_time
        # aT cant buffer
        actualTime = max(actualTime - loop_duration, 0)
        last_loop_time = end_time
        #print(loop_duration, actualTime)
        #print(actualTime)'''
    
    while True:
        current_time = utime.ticks_ms()
    
        if utime.ticks_diff(current_time, last_time) >= interval:
            # Führe deine Aktionen hier aus
            last_time = utime.ticks_add(last_time, interval)
            #actualTime = max(actualTime - interval, 0)
            actualTime = actualTime - 1;
            #print(last_time)
            deltaTime = deltaTime - interval;
            #print(actualTime, deltaTime)
            if deltaTime <= 0:
                break

    '''# buffering
    if(newValue == 0):
        bufferDuration = openTime * buffer
        start_time = time.ticks_ms()
        last_loop_time = start_time
        print("BUFFERING")
        while(bufferDuration > 0):
            end_time = time.ticks_ms()
            loop_duration = end_time - last_loop_time
            bufferDuration = bufferDuration - loop_duration
            last_loop_time = end_time
            #print(loop_duration, bufferDuration)
        print("BUFFERING STOPPED")'''

    print("RELEASE CLOSE: Calculated DMX Value:", actualTime / openTime * 255)

def setCurtainValue(newValue):
    print("----- setCurtainValue ------")
    global movingTask
    global actualValue
    global openTime

    if(actualValue == newValue):
        return
    
    newTime = (newValue / 255) * openTime
    if(actualTime == newTime):
        # stop
        print("STOP")
        stopMovingTask()
        pass
    elif(actualTime < newTime):
        # open
        print("OPEN ", openTime)
        deltaTime = newTime - actualTime
        print(deltaTime)

        stopMovingTask()
        movingTask = uasyncio.create_task(openCurtainTask(deltaTime, newValue))
    else:
        # close 
        print("CLOSE")
        deltaTime = actualTime - newTime

        stopMovingTask()
        movingTask = uasyncio.create_task(closeCurtainTask(deltaTime, newValue))

    actualValue = newValue

def stopMovingTask():
    global movingTask

    if(movingTask != None):
        movingTask.cancel()
    print("RELEASE ALL BTNs")

if __name__ == "__main__":
    uasyncio.run(main())


