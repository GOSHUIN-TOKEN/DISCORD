import asyncio

async def hello_world(n):
    await asyncio.sleep(1)
    print("{}: Hello World!".format(n))

async def call_hello_world1():
    print("call_hello_world1()")
    await hello_world(1)

async def call_hello_world2():
    print("call_hello_world2()")
    await hello_world(2)

loop = asyncio.get_event_loop()
loop.create_task(call_hello_world1())
loop.run_until_complete(call_hello_world2())