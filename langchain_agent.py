import asyncio
import os
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

async def main():
    # Tell LangChain how to launch and talk to your MCP server
    client = MultiServerMCPClient(
        {
            "email_agent": {
                "command": "python",
                "args": ["mcp_server.py"],
                "transport": "stdio",
            }
        }
    )

    # This starts mcp_server.py as a subprocess and asks it
    # "what tools do you have?" — this is where FastMCP's
    # auto-generated schema gets pulled in, no manual JSON needed.
    tools = await client.get_tools()

    llm = ChatGroq(model="openai/gpt-oss-120b")

    agent = create_react_agent(llm, tools)

    user_message = "Schedule an email to jerry21jerry21jerry@gmail.com to be sent now. The message body should say: Testing my LangChain plus MCP agent!"

    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": user_message}]}
    )

    print(result["messages"][-1].content)

if __name__ == "__main__":
    asyncio.run(main())