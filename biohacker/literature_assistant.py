# Just a basic assistant first, but needs to be a KB assistant that can scrape and retrieve information

from strands import Agent, tool
from strands_tools import file_read, file_write, editor
import json

LITERATURE_ASSISTANT_SYSTEM_PROMPT = """
You are a bioinformatician that is an expert in bioinformatic tools involved in research. Your capabilities include:

1. Analysis Tools:
   - Text summarization
   - Literature review
   - Content evaluation
   - Citation assistance

2. Teaching Methods:
   - Provide clear explanations with examples
   - Offer constructive feedback
   - Suggest improvements
   - Break down complex concepts

3. Decision Protocol:
   - If query is a summary of the user's research → Summarise briefly and suggest relevant literature, tools, and methods, especially bioinformatics tools that can be run by the software assistant agent.
   - If query seeks to clarify information about which program to use → Search specifically the literature relevant to the user's research question, compare the different tools and methods available, and provide a recommendation.

Focus on being clear, encouraging, and educational in all interactions. Always explain the reasoning behind your suggestions to promote learning.

"""


@tool
def literature_assistant(query: str) -> str:
    """
    Process and respond to biological queries.

    Args:
        query: The user's biological question

    Returns:
        A helpful response addressing biological concepts
    """
    # Format the query with specific guidance for the literature assistant
    formatted_query = f"Analyze and respond to this biological query, providing clear explanations with examples with clear citations where appropriate: {query}"
    
    try:
        print("Searching literature database...")

        literature_agent = Agent(
            system_prompt=LITERATURE_ASSISTANT_SYSTEM_PROMPT,
            tools=[editor, file_read, file_write],
        )
        agent_response = literature_agent(formatted_query)
        text_response = str(agent_response)

        if len(text_response) > 0:
            return text_response
        
        return "I apologize, but I couldn't properly analyze your research question. Could you please rephrase or provide more context?"
    except Exception as e:
        # Return specific error message for literature queries
        return f"Error processing your query: {str(e)}"