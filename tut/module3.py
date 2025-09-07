'''
Store KB ID and Open search host name in env first, values found in AWS OpenSearch service
export STRANDS_KNOWLEDGE_BASE_ID=$(aws bedrock-agent list-knowledge-bases --region $AWS_REGION --query 'knowledgeBaseSummaries[].knowledgeBaseId' --output text)
export OPENSEARCH_COLLECTION_ID=$(aws opensearchserverless list-collections --query "collectionSummaries[].id" --output text)
export OPENSEARCH_ENDPOINT=$(aws opensearchserverless batch-get-collection --ids $OPENSEARCH_COLLECTION_ID --query 'collectionDetails[].collectionEndpoint' --output text)
export OPENSEARCH_HOST="${OPENSEARCH_ENDPOINT#https://*}"
echo "export STRANDS_KNOWLEDGE_BASE_ID=\"${STRANDS_KNOWLEDGE_BASE_ID}\"" >> ~/.bashrc
echo "export OPENSEARCH_HOST=\"$OPENSEARCH_HOST\"" >> ~/.bashrc
tail -2 ~/.bashrc

'''
from strands import Agent


# Define user intent, solely between storage and retrieval
def determine_action(agent, query):
    """Determine if the query is a store or retrieve action."""
    result = agent.tool.use_llm(
        prompt=f"Query: {query}",
        system_prompt=ACTION_SYSTEM_PROMPT
    )
    
    # Clean and extract the action
    action_text = str(result).lower().strip()
    
    # Default to retrieve if response isn't clear
    if "store" in action_text:
        return "store"
    else:
        return "retrieve"
   


def run_kb_agent(query):
    ...

    # Determine the action - store or retrieve
    action = determine_action(agent, query)

    if action == "store":
        # Store path
        agent.tool.memory(action="store", content=query)
        print("\nI've stored this information.")
    else:
        # Retrieve path
        result = agent.tool.memory(action="retrieve", query=query, min_score=0.4, max_results=9)
        # Generate response from retrieved information
        answer = agent.use_llm(prompt=f"User question: \"{query}\"\n\nInformation from knowledge base:\n{result_str}...",
                               system_prompt=ANSWER_SYSTEM_PROMPT)

response = run_kb_agent("I am in Singapore")
response = run_kb_agent("Will it rain tomorrow?")

'''
Can also directly call tools

# Optimized retrieval parameters
result = agent.tool.memory(
    action="retrieve", 
    query=query,
    min_score=0.1,  # Set minimum relevance threshold
    max_results=9   # Limit number of results
)
'''
