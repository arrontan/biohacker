def software_assistant_cli():
    """Run the software assistant in an interactive CLI loop.

    This keeps the @tool `software_assistant` function single-shot for the main agent
    while providing a convenient local REPL for human-driven sessions.
    """
    conversation_manager = SummarizingConversationManager(
        summarization_system_prompt=CUSTOM_SUMMARY_PROMPT
    )

    software_agent = Agent(
        system_prompt=SOFTWARE_ASSISTANT_SYSTEM_PROMPT,
        callback_handler=None,
        tools=[code_researcher_assistant, python_repl, shell, file_read, file_write, editor, handoff_to_user, http_request],
        conversation_manager=conversation_manager,
    )

    print("\nSoftware Assistant interactive mode. Type 'exit' to quit.\n")
    while True:
        try:
            user_input_software = input("> ")
            if user_input_software is None:
                continue
            if user_input_software.lower().strip() == "exit":
                print("Exiting interactive mode.")
                break

            # Run the agent on the provided input and print the result
            try:
                response = software_agent(user_input_software)
            except Exception:
                response = software_agent(str(user_input_software))

            print(str(response))

        except KeyboardInterrupt:
            print("\nInterrupted. Exiting interactive mode.")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    software_assistant_cli()


'''
from strands import tool

@tool
def software_assistant(query: str) -> str:
    return "Software assistant placeholder response."
'''

'''
This tool assists with software-related queries, including programming, algorithms, and data structures.

Tools in Swarm (enables autonomous coordination with shared context and working memory)
Metatooling: make new tools at runtime, for IO
Exa: fetch relevant code and documentation
File ops
Agent workflow has example showing http_request processing information
A2A protocol lets agent communicate and collaborate with each other
Explainer agent

Workflow:

1. User sends a query to the software assistant, software assistant makes sure that there is only 1 software being queried and stored as context at any given time
2. Prompt user to ask for verbosity of response, and if user wants to prioritse customisability by setting parameters in the code or just getting a quick runtime to see preliminary results
2. With Exa, Assistant fetches relevant code and documentation specific to the software being queried
    - Tavily for fast relevant search for RAG
    - Exa for comprehensive code and documentation retrieval
3. Assistant prompts user to ask if it wants to download and run the software locally, or create a virtual runtime for the software, 
    - Keep it simple
    - WARN user that downloading files from untrusted sources can be dangerous, and to verify the source
4. Run the swarm to execute the user's chosen option
    - Fetch code, download dependencies, and set up the environment
    - Write code if needed, and execute it in the virtual runtime, capture logs and handle errors
    - At every step, prompt the user with the parameters chosen, give a short simple explanation, and ask for confirmation before proceeding.
    - If the user wants to make changes, update the context and repeat the process.
    - If errors occur, provide clear feedback and options for resolution.
    - Clean up, prompt user to ask if they still need the files used in runtime
'''

# Workflow, to run agents sequentially
from strands import Agent

# Researcher Agent with web capabilities
researcher_agent = Agent(
    system_prompt=(
        "You are a Researcher Agent that gathers information from the web. "
        "1. Determine if the input is a research query or factual claim "
        "2. Use your research tools (http_request, retrieve) to find relevant information "
        "3. Include source URLs and keep findings under 500 words"
    ),
    callback_handler=None, ## impt to suppress output
    tools=[http_request]
)

# Analyst Agent for verification and insight extraction
analyst_agent = Agent(
    callback_handler=None,
    system_prompt=(
        "You are an Analyst Agent that verifies information. "
        "1. For factual claims: Rate accuracy from 1-5 and correct if needed "
        "2. For research queries: Identify 3-5 key insights "
        "3. Evaluate source reliability and keep analysis under 400 words"
    ),
)

# Writer Agent for final report creation
writer_agent = Agent(
    system_prompt=(
        "You are a Writer Agent that creates clear reports. "
        "1. For fact-checks: State whether claims are true or false "
        "2. For research: Present key insights in a logical structure "
        "3. Keep reports under 500 words with brief source mentions"
    )
)

def run_research_workflow(user_input):
    # Step 1: Researcher Agent gathers web information
    researcher_response = researcher_agent(
        f"Research: '{user_input}'. Use your available tools to gather information from reliable sources.",
    )
    research_findings = str(researcher_response)
    
    # Step 2: Analyst Agent verifies facts
    analyst_response = analyst_agent(
        f"Analyze these findings about '{user_input}':\n\n{research_findings}",
    )
    analysis = str(analyst_response)
    
    # Step 3: Writer Agent creates report
    final_report = writer_agent(
        f"Create a report on '{user_input}' based on this analysis:\n\n{analysis}"
    )
    
    return final_report



# Workflow TOOL, focusing more on tasks within a single agent that can be executed in parallel
from strands import Agent
from strands_tools import workflow

# Create an agent with workflow capability
agent = Agent(tools=[workflow])

# Create a multi-agent workflow
agent.tool.workflow(
    action="create",
    workflow_id="data_analysis",
    tasks=[
        {
            "task_id": "data_extraction",
            "description": "Extract key financial data from the quarterly report",
            "system_prompt": "You extract and structure financial data from reports.",
            "priority": 5
        },
        {
            "task_id": "trend_analysis",
            "description": "Analyze trends in the data compared to previous quarters",
            "dependencies": ["data_extraction"],
            "system_prompt": "You identify trends in financial time series.",
            "priority": 3
        },
        {
            "task_id": "report_generation",
            "description": "Generate a comprehensive analysis report",
            "dependencies": ["trend_analysis"],
            "system_prompt": "You create clear financial analysis reports.",
            "priority": 2
        }
    ]
)

# Execute workflow (parallel processing where possible)
agent.tool.workflow(action="start", workflow_id="data_analysis")

# Check results
status = agent.tool.workflow(action="status", workflow_id="data_analysis")

# Context passing
def build_task_context(task_id, tasks, results):
    """Build context from dependent tasks"""
    context = []
    for dep_id in tasks[task_id].get("dependencies", []):
        if dep_id in results:
            context.append(f"Results from {dep_id}: {results[dep_id]}")

    prompt = tasks[task_id]["description"]
    if context:
        prompt = "Previous task results:\n" + "\n\n".join(context) + "\n\nTask:\n" + prompt

    return prompt


# Swarm
import logging
from strands import Agent
from strands.multiagent import Swarm

# Enable debug logs and print them to stderr
logging.getLogger("strands.multiagent").setLevel(logging.DEBUG)
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()]
)

# Create specialized agents
researcher = Agent(name="researcher", system_prompt="You are a research specialist...")
coder = Agent(name="coder", system_prompt="You are a coding specialist...")
reviewer = Agent(name="reviewer", system_prompt="You are a code review specialist...")
architect = Agent(name="architect", system_prompt="You are a system architecture specialist...")

# Create a swarm with these agents
swarm = Swarm(
    [researcher, coder, reviewer, architect],
    max_handoffs=20,
    max_iterations=20,
    execution_timeout=900.0,  # 15 minutes
    node_timeout=300.0,       # 5 minutes per agent
    repetitive_handoff_detection_window=8,  # There must be >= 3 unique agents in the last 8 handoffs
    repetitive_handoff_min_unique_agents=3
)

# Execute the swarm on a task
result = swarm("Design and implement a simple REST API for a todo app")

# Access the final result
print(f"Status: {result.status}")
print(f"Node history: {[node.node_id for node in result.node_history]}")

@tool
def code_researcher(query: str) -> str:
    """
    Finds information from code repositories.

    Args:
        query: The user's choice of software

    Returns:
        A helpful response addressing biological concepts

    
    """
    # Format the query with specific guidance for the literature assistant
    formatted_query = f"Search the literature for: {query}"

    try:
        print("Searching literature database...")


        agent_response = researcher_agent(formatted_query)
        text_response = str(agent_response)

        if len(text_response) > 0:
            return text_response
        
        return "I apologize, but I couldn't properly analyze your research question. Could you please rephrase or provide more context?"
    except Exception as e:
        # Return specific error message for literature queries
        return f"Error processing your query: {str(e)}"


