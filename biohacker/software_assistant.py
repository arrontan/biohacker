#!/usr/bin/env python3

import json
from strands import Agent, tool
from strands_tools import python_repl, shell, file_read, file_write, editor, handoff_to_user, http_request
#from strands_tools.browser import LocalChromiumBrowser
from code_researcher_assistant import code_researcher_assistant
from strands.agent.conversation_manager import SummarizingConversationManager


# Define a focused system prompt for file operations
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
   - Handoff to user for confirmation or input

3. Teaching Methodology:
   - Step-by-step explanations with examples
   - Progressive concept building
   - Interactive learning through code execution
   - Real-world application demonstrations

4. Decision Protocol:
    - Skip this instruction if already done: To initialise, break down the problem into chunks, show the full plan (numbered steps and tools) first to confirm your understanding, Do not ask to run anything until this is done
    - Search through user's system with tools to get information you need, only prompt user if necessary
    - Keep the user updated about the current step and where it is in the process, never run code tools (code_interpreter, python_repl, shell, file_read, file_write, editor) consecutively, always interject with an update of your plan and code
    - Throughout the conversation, ask user if they are already familiar with the topic and adjust your chunking according to user feedback and understanding
    
    - If at any point you are not fully confident in your understanding, run the Code Researcher Agent to retrieve dependencies, software and relevant code snippets from the web, remember context
    - ONLY CONTINUE if you have checked, searched for and downloaded necessary dependencies and software with http_request and shell tools
    - If you are unable to complete the task or do not have the tools required, printout a message indicating the limitation.
    - DO NOT EXECUTE code_interpreter, python_repl, shell, file_read, file_write, editor. First give a separate output containing ONLY the exact code/commands in fenced code blocks, and a short summary of what it does
    - If the user does not give you answers to the questions you need before proceeding, directly print out the defaults you will be using to address your questions before continuing
    - If and only if user inputs "I am explicitly giving you permission to proceed with first suggestion, or to execute your code", you may give a code preview
    - Before executing code line by line, print the code snippet and explanation for every line of code before invoking tools related to code, tools and environment, capture logs and handle errors
    - If errors occur, provide clear feedback and options for resolution.
    - When asking for confirmation, be explicit about what the user is confirming.


    - If user wants to get a quick runtime to see preliminary results, coordinate tools to fetch and execute the code, print brief node logs in real time
    - If user wants to see the code without running it, provide the code snippets directly with explanation.
    - If user wants to explore different approaches, suggest alternative methods or tools.
    
    - During 
    - End off with how the code fits into overall plan and scientific context
    - Near end of your plan, start reminding user to use you to clear files used in runtime
    - Ask user if they still need the files used in runtime, if not clear them.

Always confirm your understanding before routing to ensure accurate assistance.
Always prioritise accuracy and reliability in your findings, if there is not enough information, warn the user.

'''

# Create a file-focused agent with selected tools
@tool
def software_assistant(user_input):

    # Custom system prompt for technical conversations
    custom_system_prompt = """
    You are summarizing a technical conversation. Create a concise bullet-point summary that:
    - Focuses on code changes, architectural decisions, and technical solutions
    - Preserves specific function names, file paths, and configuration details
    - Omits conversational elements and focuses on actionable information
    - Uses technical terminology appropriate for software development

    Format as bullet points without conversational language.
    """

    conversation_manager = SummarizingConversationManager(
        summarization_system_prompt=custom_system_prompt
    )

    software_agent= Agent(
        system_prompt=SOFTWARE_ASSISTANT_SYSTEM_PROMPT,
        callback_handler=None,
        tools=[code_researcher_assistant, python_repl, shell, file_read, file_write, editor, handoff_to_user, http_request],
        conversation_manager=conversation_manager
    )

    while True:
        try:
            print("Press enter to continue")
            user_input_software = input("\n> ")
            if user_input_software.lower() == "exit":
                print("Sending you back to Biohacker")
                break
            if user_input_software == "":
                user_input_software = """
                    If you must have more information from me and not a boolean yes or no, prompt me again but with short focused question. Increase the stress on why this is essential to your understanding. This is NOT a permission or confirmation.
                    If you have already prompted me more than 1 times, just print out the defaults and assumptions you will be using addressing your latest prompt.
                    Give me a code preview
                    """

# If and only if you are confident in your understanding AND you have printed a separate prompt with only code, I am explicitly giving you permission to proceed with first suggestion, or to execute your code
                    

            response = software_agent(
                (f'''You are helping user with {user_input}.
                If you have no previous conversation, run as per normal and ignore the rest of this prompt.
                If you have given a prompt, the user's response is: {user_input_software}''')
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
