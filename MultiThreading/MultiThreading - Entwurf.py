# from here to MultiThreading v1

import uasyncio as asyncio
import utime as utime
import _thread

actualTime = 0

killThread = False
threadRunning = False

# Ihre Funktion zum Setzen des Vorhangswerts
async def setCurtainValue(value):
    # Hier implementieren Sie die Logik zum Setzen des Vorhangswerts
    print("Setting curtain value to:", value)

    # Starten Sie den 2. Task (Vorhang öffnen) asynchron
    
    asyncio.create_task(openCurtainTaskAsync(5000))
    
    #delaying because of stopThread
    #await openCurtainTaskAsync(5000)

# Ihre blockierende Funktion (ohne asynchrone Unterstützung)
def openCurtainTaskBlocking(deltaTime):
    global killThread
    global actualTime
    global threadRunning
    last_time = utime.ticks_ms()
    interval = 1
    while True:

        if killThread == True:
            killThread = False
            print("Thread killed at ", deltaTime)
            _thread.exit()

        current_time = utime.ticks_ms()
    
        if utime.ticks_diff(current_time, last_time) >= interval:
            last_time = utime.ticks_add(last_time, interval)
            actualTime = actualTime + 1
            deltaTime = deltaTime - interval

            if deltaTime <= 0:
                break

    print("OPENED - Thread finished")
    threadRunning = False

# Funktion zum Wrapper für den blockierenden Task
def openCurtainTaskWrapper(deltaTime):
    _thread.start_new_thread(openCurtainTaskBlocking, (deltaTime,))

# Asynchrone Wrapper-Funktion für den blockierenden Task
async def openCurtainTaskAsync(deltaTime):
    global threadRunning

    t1 = utime.ticks_ms()
    await stopThread()
    threadRunning = True
    t2 = utime.ticks_ms()
    print("STAR NEW THREAD -> CLOSING TIME ", t2-t1, "ms")
    openCurtainTaskWrapper(deltaTime)

async def stopThread():
    global killThread
    global threadRunning
    if threadRunning == False:
        print("THREAD NOT RUNNING")
        return
    
    print("STOP THREAD")
    
    killThread = True
    while killThread == True:
        #asyncio.sleep(0.1)
        pass
    await asyncio.sleep_ms(1)
    return

# Ihr Haupt-Loop (DMX Loop)
async def mainLoop():
    i = 0
    while True:
        # Hier implementieren Sie Ihre DMX-Logik
        print("DMX Loop: ", i, actualTime)
        #val = int(input("DMX-Value: "))

        # Rufen Sie setCurtainValue im Hauptloop auf
        await setCurtainValue(44)

        i = i+1
        print(actualTime)
        await asyncio.sleep_ms(4)  # Beispiel für eine asynchrone Wartezeit

# Starten Sie die Aufgaben
loop = asyncio.get_event_loop()
loop.create_task(mainLoop())

# Führen Sie die Schleifen aus
loop.run_forever()

# todo:
# veränderung von actualTime mit exaktem verändertem faktor
# threadKillTime