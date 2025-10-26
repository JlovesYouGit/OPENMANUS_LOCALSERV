import asyncio
from app.agent.manus import Manus

async def test():
    print("Creating Manus agent...")
    agent = await Manus.create()
    print('Agent created successfully')
    return agent

if __name__ == "__main__":
    asyncio.run(test())