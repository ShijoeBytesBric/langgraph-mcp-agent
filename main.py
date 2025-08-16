import asyncio
from dotenv import load_dotenv

load_dotenv()

from src.mcp_agent import Agent, LLMProvider

llm = LLMProvider().model
agent = Agent(llm)

async def main():
    response = await agent.run("What are the latest updates in the Office 365 product")
    with open("response.txt", "a") as f:
        f.write(str(response))


if __name__ == "__main__":  

    asyncio.run(main())
