"""Datacircle MCP Agent - Read LinkedIn Profiles

Connect an Agno agent to Datacircle's hosted MCP server. Each tool makes one
REST call with your Datacircle API key. This example keeps the agent to two
tools: `get_linkedin_profile` and `get_balance`.

Setup:
1. Install dependencies: `uv pip install "agno[mcp,openai]"`
2. Log in at https://datacircle.dev/login with your work email and copy your API key
3. Set `DATACIRCLE_API_KEY` and `OPENAI_API_KEY` in your environment

Run: `python cookbook/91_tools/mcp/datacircle.py`

Datacircle MCP docs: https://docs.datacircle.dev/mcp-server
"""

import asyncio
from os import getenv
from textwrap import dedent

from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from agno.tools.mcp import MCPTools
from agno.utils.log import log_error

# ---------------------------------------------------------------------------
# Create Agent
# ---------------------------------------------------------------------------

DATACIRCLE_MCP_URL = "https://api.datacircle.dev/mcp"


async def run_agent(task: str) -> None:
    """Connect to Datacircle and run one task."""
    datacircle_api_key = getenv("DATACIRCLE_API_KEY")
    if not datacircle_api_key:
        log_error("DATACIRCLE_API_KEY environment variable not set.")
        return

    async with MCPTools(
        url=DATACIRCLE_MCP_URL,
        transport="streamable-http",
        headers={"Authorization": f"Bearer {datacircle_api_key}"},
        # The server also has add_funds (a checkout link) and file tools;
        # this example only reads profiles and the balance.
        include_tools=["get_linkedin_profile", "get_balance"],
        timeout_seconds=60,
    ) as datacircle_tools:
        agent = Agent(
            name="DatacircleAgent",
            model=OpenAIResponses(id="gpt-5.6-luna"),
            tools=[datacircle_tools],
            instructions=dedent("""\
                You research people for a sales team with Datacircle's tools.

                - Read each LinkedIn profile once with get_linkedin_profile; every call is billed
                - Answer only from the profile the tool returns
                - If a call fails, report the error instead of retrying
            """),
            markdown=True,
        )
        await agent.aprint_response(input=task, stream=True)


# ---------------------------------------------------------------------------
# Run Agent
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(
        run_agent(
            "Look up https://www.linkedin.com/in/williamhgates and summarize his career "
            "in three lines. Then show my Datacircle balance."
        )
    )

# More example prompts:
"""
- "Read https://www.linkedin.com/in/<profile> with the harvestapi provider and list the last three roles."
- "Summarize the education and current company of https://www.linkedin.com/in/<profile>."
"""
