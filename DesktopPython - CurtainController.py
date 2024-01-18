import asyncio
import time

# Timing
actualTime = 0 # ms
actualValue = 0 # DMX-Value

# Curtain Constants
openTime = 15000 #ms
buffer = 0.1 # -> 10%
bufferedOpenTime = openTime + openTime * buffer

movingTask = None

# IF OPENING AND THEN CREATES NEW TASK VOR OPENING SERVO IS RELEASED AND AGAIN PRESSED -> SHUTTERING

async def main_loop():
    await asyncio.gather(main())

async def get_user_input():
    loop = asyncio.get_event_loop()
    print("--- DMX-Value: ---")
    return await loop.run_in_executor(None, input)

async def main():
    #while True:
    dmxValue = input("DMX-Value:")
    setCurtainValue(int(dmxValue))
    #await asyncio.sleep(3000)
    setCurtainValue(30)

    """ while True:
        
        dmxValue = await get_user_input()
        print(f"Received DMX-Value: {dmxValue}")
        setCurtainValue(int(dmxValue))
        dmxValue = await get_user_input()
        print(f"Received DMX-Value: {dmxValue}")
        setCurtainValue(int(dmxValue)) """
    
    # duration 15s
    """ asyncio.create_task(setCurtainValue(255))
    print("AFTER START")
    await asyncio.sleep(1)
    print("AFTER DELAY")
    asyncio.create_task(setCurtainValue(100))
    await asyncio.sleep(1000)
    print("AFTER 2nd run") """

async def openCurtainTask(deltaTime, newValue):
    global actualTime
    global buffer
    global openTime

    start_time = time.time() * 1000
    startActualTime = actualTime
    last_loop_time = start_time

    print("openCurtain", startActualTime, min(startActualTime + deltaTime, openTime), (min(startActualTime + deltaTime, openTime) - startActualTime) / 1000, "s")
    print("PRESS OPEN")
    # no buffering
    while actualTime < min(startActualTime + deltaTime, openTime):
        end_time = time.time() * 1000
        loop_duration = end_time - last_loop_time
        # aT cant buffer
        actualTime = min(actualTime + loop_duration, openTime)
        last_loop_time = end_time
        #print(loop_duration)
        print(actualTime)

    # buffering
    if(newValue == 255):
        bufferDuration = openTime * buffer
        start_time = time.time() * 1000
        last_loop_time = start_time
        print("BUFFERING")
        while(bufferDuration > 0):
            end_time = time.time() * 1000
            loop_duration = end_time - last_loop_time
            bufferDuration = bufferDuration - loop_duration
            last_loop_time = end_time
            #print(loop_duration, bufferDuration)
        print("BUFFERING STOPPED")

    print("RELEASE OPEN: Calculated DMX Value:", actualTime / openTime * 255)

async def closeCurtainTask(deltaTime, newValue):
    global actualTime
    global buffer
    global openTime

    start_time = time.time() * 1000
    startActualTime = actualTime
    last_loop_time = start_time

    print("closeCurtain", startActualTime, max(startActualTime - deltaTime, 0), (max(startActualTime - deltaTime, 0) + startActualTime) / 1000, "s")
    print("PRESS CLOSE")

    # no buffering
    while actualTime > max(startActualTime - deltaTime, 0):
        end_time = time.time() * 1000
        loop_duration = end_time - last_loop_time
        # aT cant buffer
        actualTime = max(actualTime - loop_duration, 0)
        last_loop_time = end_time
        #print(loop_duration, actualTime)
        #print(actualTime)

    # buffering
    if(newValue == 0):
        bufferDuration = openTime * buffer
        start_time = time.time() * 1000
        last_loop_time = start_time
        print("BUFFERING")
        while(bufferDuration > 0):
            end_time = time.time() * 1000
            loop_duration = end_time - last_loop_time
            bufferDuration = bufferDuration - loop_duration
            last_loop_time = end_time
            #print(loop_duration, bufferDuration)
        print("BUFFERING STOPPED")

    print("RELEASE CLOSE: Calculated DMX Value:", actualTime / openTime * 255)

def setCurtainValue(newValue):
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
        movingTask = asyncio.create_task(openCurtainTask(deltaTime, newValue))
    else:
        # close 
        print("CLOSE")
        deltaTime = actualTime - newTime

        stopMovingTask()
        movingTask = asyncio.create_task(closeCurtainTask(deltaTime, newValue))

    actualValue = newValue

def stopMovingTask():
    global movingTask

    if(movingTask != None):
        movingTask.cancel()
    print("RELEASE ALL BTNs")

if __name__ == "__main__":
    asyncio.run(main())


