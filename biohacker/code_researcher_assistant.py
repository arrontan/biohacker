from strands import Agent, tool
from strands_tools.tavily import tavily_search, tavily_extract, tavily_crawl, tavily_map
import json

CODE_RESEARCHER_SYSTEM_PROMPT ='''
                    You are a Researcher Agent that gathers information from code repositories, documentations, and scholarly articles. 
                    1. Use your research tools to find the latest, relevant information
                    2. Include source URLs and keep findings concise, without losing information
                    3. Always prioritise accuracy and reliability in your findings, if there is not enough information, warn the user.
                    '''
@tool
def code_researcher_assistant(user_input):

    try:
            print("Searching code repositories, documentations, and scholarly articles (this may take ~5mins...☕?)")
            researcher_agent = Agent(
                system_prompt=CODE_RESEARCHER_SYSTEM_PROMPT,
                callback_handler=None, ## impt to suppress output
                tools=[tavily_search, tavily_extract,  tavily_crawl, tavily_map],
            )
            researcher_response = researcher_agent(
                f"Research: '{user_input}'. Use your available tools to gather information from reliable sources.",
            )
            research_findings = str(researcher_response)

            if len(research_findings) > 0:
                return research_findings

            return "I apologize, but I couldn't find any relevant information. Maybe try another tool?"
    except Exception as e:
        # Return specific error message for literature queries
        return f"Error processing your query: {str(e)}"
 