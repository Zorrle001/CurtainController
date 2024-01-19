import uasyncio as asyncio
import utime as utime

actualTime = 0

# Ihr 2. Task (Vorhang öffnen)
async def openCurtainTask(deltaTime):
    global actualTime
    last_time = utime.ticks_ms()
    interval = 1
    while True:
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

    print("OPENED")

# Ihre Funktion zum Setzen des Vorhangwerts
async def setCurtainValue(value):
    # Hier implementieren Sie die Logik zum Setzen des Vorhangswerts
    print("Setting curtain value to:", value)

    # Starten Sie den 2. Task (Vorhang öffnen)
    asyncio.create_task(openCurtainTask(5000))

# Ihr Haupt-Loop (DMX Loop)
async def mainLoop():
    while True:
        # Hier implementieren Sie Ihre DMX-Logik
        print("DMX Loop")

        # Rufen Sie setCurtainValue im Hauptloop auf
        await setCurtainValue(42)

        await asyncio.sleep(0.1)  # Beispiel für eine asynchrone Wartezeit

# Starten Sie die Aufgaben
loop = asyncio.get_event_loop()
loop.create_task(mainLoop())

# Führen Sie die Schleifen aus
loop.run_forever()