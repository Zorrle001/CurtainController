import uasyncio

async def main():
    task = uasyncio.create_task(loop1())
    uasyncio.create_task(loop2())
    uasyncio.run_until_complete(task)

async def loop1():
    while True:
        print("LOOP 1")
        await uasyncio.sleep_ms(5000)
        print("LOOP 1 - RUN")
        loop = uasyncio.get_event_loop()
        loop.create_task(task())
        print("LOOP 1 - RESTART")

async def task():
    print("RUN TASK")
    await uasyncio.sleep_ms(1000)
    i = 0
    while True:
        pass

    print("TASK FINISHED")

async def loop2():
    while True:
        print("LOOP 2")
        await uasyncio.sleep_ms(1000)


if __name__ == "__main__":
    loop = uasyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()