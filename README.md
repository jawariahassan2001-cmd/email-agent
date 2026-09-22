# Email Agent

An AI agent that takes natural language like "send an email to Jerry at 5pm saying the meeting moved" and turns it into an actual scheduled email, without any manual parsing or fixed command format.

## How it works

You type a plain English request. An LLM reads it and decides which action to take and what arguments it needs (recipient, time, message). That decision gets passed to real Python code, which actually sends the email through Gmail.

The LLM never sends anything itself, it only decides what should happen. The Python code is what actually does it.

## Two versions in this repo

### v1 - agent.py

The first working version. Built by hand to understand tool calling before relying on a framework.

- LLM: Groq, using `openai/gpt-oss-120b` with native function calling
- Tool schema written manually as JSON
- A simple dispatcher checks what the model decided and calls the matching Python function
- Scheduling done with `dateutil` for parsing times like "5pm" and `time.sleep()` to wait
- Sending done with `smtplib` and a Gmail app password

This version works end to end. Tested it multiple times, real emails land in the inbox at the scheduled time.

### v2 - mcp_server.py + langchain_agent.py

Same idea, rebuilt on LangChain and MCP instead of hand-rolled tool calling.

- `mcp_server.py` is a FastMCP server that exposes the email tool. It doesn't know or care what's calling it.
- `langchain_agent.py` connects to that server as an MCP client and uses LangGraph's prebuilt agent loop to decide when to call the tool, instead of the manual dispatcher from v1.

Right now this part is blocked on a dependency conflict. `langchain-mcp-adapters` (0.3.1) was built against the older MCP SDK, and the current `mcp` package (2.x) changed some internals it depends on. There's an open issue on their GitHub about this exact thing. Fix is to pin `mcp==1.28.0` with an older `fastmcp` release, haven't finished testing it yet.

## Stack

Python, Groq API, LangChain, LangGraph, FastMCP, MCP, smtplib, python-dateutil

## Why bother with v1 if v2 exists

Because writing the tool schema and dispatcher by hand first means I actually understand what LangChain and MCP are doing for me. If I'd started with the framework I'd have a working demo but not much to say if someone asked how any of it actually works underneath.

## Next steps

- add a second tool for sending immediately instead of scheduling
- add a read-only tool that checks the inbox, to show the agent isn't just one trick
- swap time.sleep() for something that doesn't block the whole script, so multiple emails can be scheduled at once
- get the v2 dependency conflict sorted and confirm it runs the same test case as v1
