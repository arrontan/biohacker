# Includes Tavily tool to extract real time data

from strands import Agent, tool
from strands_tools import file_read, file_write, editor, shell
import json

DATA_SYSTEM_PROMPT = """
You are a file sorter that helps organises the users files, stored in ./uploads
"""


@tool
def data_cleaning_assistant(query: str) -> str:
    try:
        print("Searching data files...")

        data_agent = Agent(
            system_prompt=DATA_SYSTEM_PROMPT,
            tools=[editor, file_read, file_write, shell],
        )
        agent_response = data_agent(query)
        text_response = str(agent_response)

        if len(text_response) > 0:
            return text_response
        
        return "I apologize, but I couldn't properly analyze your files. Could you please rephrase or provide more context?"
    except Exception as e:
        # Return specific error message for data queries
        return f"Error processing your query: {str(e)}"