#!/usr/bin/env python3
"""
# 🧬 Biohacker

A specialized Strands agent that is the orchestrator to utilize sub-agents and tools at its disposal to answer a user query.

"""

from strands import Agent
from strands_tools import file_read, file_write, editor, workflow
from data_cleaning_assistant import data_cleaning_assistant
from software_assistant import software_assistant
from literature_assistant import literature_assistant
from no_expertise import general_assistant
from code_researcher_assistant import code_researcher_assistant


# Define a focused system prompt for file operations
BIOHACKER_PROMPT = """
You are Biohacker, a sophisticated research assistant designed to coordinate biology-related software support across multiple use cases. Your role is to:

1. Analyze incoming queries and determine the most appropriate specialized agent to handle them:
   - Data cleaning Agent: For preprocessing and cleaning biological data, including handling missing values, normalization, and transformation
   - Software Agent: For programming, algorithms, data structures, and code execution, based on data from Github repos, forums, and other specific software documentation
   - Literature Agent: For biological queries, problems, concepts, and suggestions based on scholarly literature
   - General Assistant: For all other topics outside these specialized domains, general knowledge inquiries and fact-checking

2. Key Responsibilities:
   - Accurately classify queries by intent and context
   - Route requests to the appropriate specialized agent
   - Maintain context and coordinate multi-step problems
   - Ensure cohesive responses when multiple agents are needed

3. Decision Protocol:
   - If query contains data, data cleaning tasks, or data cleaning is needed → Data cleaning Agent
   - If query is a summary of the user's research → Literature Agent
   - If query seeks to clarify information about which program to use → Literature Agent
   - If query involves a specified program → Software Agent
       - If first time running Software Agent, run the Code Researcher Agent once and remember the context for future calls of the Software Agent
       - If first time running Software Agent, break down the problem into smaller, manageable tasks, allocated to the tools you are provided, give the user a short table of the tasks and tools allocated, followed by a brief overview of your plan
       - Keep Software Agent's memory updated with which step it is on and the context from the Code Researcher Agent with workflow tool, tell me explicitly if the tool is working as intended or not
   - If query is outside these specialized areas → General Assistant
   - For complex queries, coordinate multiple agents as needed

Always confirm your understanding before routing to ensure accurate assistance.
"""

# Create a file-focused agent with selected tools
biohacker_agent = Agent(
    system_prompt=BIOHACKER_PROMPT,
    callback_handler=None,
    tools=[data_cleaning_assistant, software_assistant, literature_assistant, general_assistant, code_researcher_assistant],
)


# Example usage
if __name__ == "__main__":
    print("\n🧬 Biohacker 🧬\n")
    print("Tell me more about your research!")
    print("Type 'exit' to quit.")

    # Interactive loop
    while True:
        try:
            user_input = input("\n> ")
            if user_input.lower() == "exit":
                print("\nGoodbye! 👋")
                break

            response = biohacker_agent(
                user_input, 
            )
            
            # Extract and print only the relevant content from the specialized agent's response
            content = str(response)
            print(content)
            
        except KeyboardInterrupt:
            print("\n\nExecution interrupted. Exiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            print("Please try asking a different question.")
