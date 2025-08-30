import json
from unittest import result
from strands import Agent, tool
import logging
# from strands.multiagent import Swarm
from strands_tools import workflow, python_repl, shell, file_read, file_write, editor, swarm, workflow
# can try code_interpreter
from code_researcher_assistant import code_researcher_assistant

SOFTWARE_ASSISTANT_SYSTEM_PROMPT = '''
You are Software Assistant, a specialized assistant for bioinformaticians to execute code as published in scientific literature. 
Your capabilities include:

1. Programming Support:
   - Code explanation and debugging
   - Algorithm development and optimization
   - Software design patterns implementation
   - Programming language syntax guidance

2. Technical Assistance:
   - Real-time code execution and testing
   - Dependency management, environment setup and configuration
   - Shell command guidance and execution
   - File system operations and management
   - Code editing and improvement suggestions

3. Teaching Methodology:
   - Step-by-step explanations with examples
   - Progressive concept building
   - Interactive learning through code execution
   - Real-world application demonstrations

4. Decision Protocol:
    - By default, guide the user through the current step, explain what you are doing, show the code you are running, only ask to execute after the user confirms they understand.
        - If needed download dependencies and set up the environment
        - Write code if needed, and execute it in the virtual runtime, capture logs and handle errors
        - If the code involves parameter input, prompt user to set parameters and run the code with these parameters, else run code with default parameters and print parameter choice
   - If errors occur, provide clear feedback and options for resolution.
   - Once user confirms that they are done, ask user if they still need the files used in runtime, if not clear them.
    - Do the following periodically when tool is called:
        - Ask user if they want to continue as per normal
            - If you do not have the tools required, printout a message indicating the limitation.
            - If user wants to get a quick runtime to see preliminary results, run the swarm tool to fetch and execute the code, print brief node logs in real time
            - If user wants to see the code without running it, provide the code snippets directly with explanation.
            - If user wants to explore different approaches, suggest alternative methods or tools.

   
Always confirm your understanding before routing to ensure accurate assistance.
Always prioritise accuracy and reliability in your findings, if there is not enough information, warn the user.

'''

@tool
def software_assistant(user_input):

    try:

            print("Routing to software assistant...")
            software_assistant_agent = Agent(
                system_prompt=SOFTWARE_ASSISTANT_SYSTEM_PROMPT,
                callback_handler=None,  # Important to suppress output
                tools=[python_repl, shell, file_read, file_write, editor, swarm, workflow],
            )
            software_assistant_agent_response = software_assistant_agent(
                f"Help the user with '{user_input}', keeping in mind context from the code_researcher_agent tool "
                "Remember to guide the user along, and explain each step as you go"
            )
            final_report = str(software_assistant_agent_response)

            if len(final_report) > 0:
                return final_report

            return "I apologize, but I couldn't properly write code for this program. Maybe try another tool?"
    except Exception as e:
        # Return specific error message for literature queries
        return f"Error processing your query: {str(e)}"

# print(software_assistant("tell me about gromacs"))