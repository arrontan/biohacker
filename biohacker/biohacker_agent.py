#!/usr/bin/env python3
"""
# 🧬 Biohacker

A specialized Strands agent that is the orchestrator to utilize sub-agents and tools at its disposal to answer a user query.

"""

import json
from strands import Agent
from strands_tools import file_read, file_write, editor, workflow, handoff_to_user
from data_cleaning_assistant import data_cleaning_assistant
from software_assistant import software_assistant
from literature_assistant import literature_assistant
from no_expertise import general_assistant
# from code_researcher_assistant import code_researcher_assistant


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
   - If query involves data, file manipulation, data cleaning tasks, or data cleaning is needed → Data cleaning Agent
   - If query is a summary of the user's research → Literature Agent
   - If query seeks to clarify information about which program to use → Literature Agent
   - If query involves a specified program → Software Agent
   - If query is outside these specialized areas → General Assistant
   - For complex queries, coordinate multiple agents as needed

Always confirm your understanding before routing to ensure accurate assistance.
"""

# Create a file-focused agent with selected tools
biohacker_agent = Agent(
    system_prompt=BIOHACKER_PROMPT,
    callback_handler=None,
    tools=[data_cleaning_assistant, software_assistant, literature_assistant, general_assistant, handoff_to_user],
)

''''''
# Example usage
if __name__ == "__main__":
    
    print(
        '''
        \n🧬 Biohacker 🧬\n
        
    Tell me more about your research!
    
    I can help you:
    1. Review the literature, try: 
        - Best tools for simulating molecular dynamics?
        - How can I compare between different homologs of a protein?
        - What visualisation is best used for showing gene expression data?
    2. Guide you through software installation, setup, and execution, try:
        - Molecular dynamics: GROMACS tutorial
        - Sequence analysis: ClustalW tutorial
        - Data visualisation: Volcano plot tutorial in R
    3. Ask me questions about basic biology
    4. Help you with file management, workflow automation and scripting

    Type 'exit' to quit
        '''
    )

    # Interactive loop
    while True:
        try:
            user_input = input("\n> ")
            if user_input.lower() == "exit":
                print("\nGoodbye! 👋")
                break
            
            print("Thinking...")
            # If the biohacker agent routes to the software_assistant, send a JSON shuttle
            # so the software assistant can accept both prompt and followup without interactive input.
            try:
                # build a simple shuttle: main prompt is user_input, no followup yet
                shuttle = json.dumps({"prompt": user_input, "followup": None})
                response = biohacker_agent(shuttle)
            except Exception:
                response = biohacker_agent(user_input)
            
            # Extract and print only the relevant content from the specialized agent's response
            content = str(response)
            print(content)
            
        except KeyboardInterrupt:
            print("\n\nExecution interrupted. Exiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            print("Please try asking a different question.")
