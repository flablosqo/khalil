import asyncio
import time


async def foo():
    before = time.time()
    print('inside foo')
    await asyncio.sleep(1)
    print('foo done ')
    print('time in foo:', time.time() - before)


async def bar():
    before = time.time()
    print('inside bar')
    await asyncio.sleep(6)
    print('bar done ')
    print('time in foo:', time.time() - before)


async def main():
    await asyncio.gather(foo(), bar())
    # await foo()
    # await bar()


if __name__ == '__main__':
    before = time.time()
    asyncio.run(main())
    print('time:', time.time() - before)
