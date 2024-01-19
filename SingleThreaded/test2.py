import utime

import uasyncio

async def loop1():
    while True:
        pass

async def loop2():
    while True:
        await uasyncio.sleep(1000)
        print("Hello")


loop = uasyncio.get_event_loop()
loop.create_task(loop1())
loop.run_forever()