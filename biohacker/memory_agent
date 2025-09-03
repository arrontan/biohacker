# importing 
import boto3
import os
import json
import logging
import numpy as np

import os
os.environ["TAVILY_API_KEY"] = "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"


# Create a logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


from strands import Agent, tool
from strands.models import BedrockModel

from botocore.exceptions import ClientError

# second cell
region = os.environ.get("AWS_REGION")
bedrock_client = boto3.client(
    service_name='bedrock-runtime',
    region_name="us-east-1"
)

#String constants: Label each model you want to use
#Need to think if we want to use other models
claude3 = 'claude3'
llama2 = 'llama2'
llama3='llama3'
mistral='mistral'
titan='titan'
cohere = 'cohere'

# Map model nicknames to the actual Bedrock model ID's 
models_dict = {
    claude3 : 'anthropic.claude-3-haiku-20240307-v1:0',
    llama2: 'meta.llama2-13b-chat-v1',
    llama3: 'meta.llama3-8b-instruct-v1:0',
    mistral: 'mistral.mistral-7b-instruct-v0:2',
    titan : 'amazon.titan-embed-text-v2:0',
}

##Inference parameters

# max length of the response of the agent
max_tokens_val = 200 

#Temp sets randomness in generation (lower = more deterministic, high = more creative and random)
temperature_val = 0.1

# Setting special parameters for each model 
# Might have to experiment with this
# Model looks at all possible next tokens(words/pieces of words)
# Keeps only top k most likely tokens that model might pick from the model vocabulary while generating its response
dict_add_params = {
    llama3: {}, #"max_gen_len":max_tokens_val, "temperature":temperature_val} , 
    claude3: {"top_k": 200, },# "temperature": temperature_val, "max_tokens": max_tokens_val},
    mistral: {}, #{"max_tokens":max_tokens_val, "temperature": temperature_val} , 
    titan:  {"topK": 200, },# "maxTokenCount": max_tokens_val},
}

# Shared configuration passed to all models
# topP limits the probability mass
# topk limits the number of candidate tokens
inference_config={
    "temperature": temperature_val,
    "maxTokens": max_tokens_val,
    "topP": 0.9
}

#Sending a request; Wraps user input into Bedrock's message format
#Adds system prompt except for Mistral and Titan which dosent support system prompts
def generate_conversation(bedrock_client,model_id,system_text,input_text):
    """
    Sends a message to a model.
    Args:
        bedrock_client: The Boto3 Bedrock runtime client.
        model_id (str): The model ID to use.
        system_text (JSON) : The system prompt.
        input text : The input message.

    Returns:
        response (JSON): The conversation that the model generated.

    """

    logger.info("Generating message with model %s", model_id)

    # Message to send.
    message = {
        "role": "user",
        "content": [{"text": input_text}]
    }
    messages = [message]
    system_prompts = [{"text" : system_text}]

    if model_id in [models_dict.get(mistral), models_dict.get(titan)]:
        system_prompts = [] # not supported

# Inference parameters to use.


#Base inference parameters to use.
#inference_config 


    # Send the message.
    response = bedrock_client.converse(
        modelId=model_id,
        messages=messages,
        system=system_prompts,
        inferenceConfig=inference_config,
        additionalModelRequestFields=get_additional_model_fields(model_id)
    )

    return response

#Example Usage
system_text = """You are a memory-enabled research assistant for biologists.
You have access to prior context and a memory store containing information from GitHub, CRAN, bioRxiv, PubMed, software manuals, and publications.

Your tasks are:
1. Remember and recall important facts from previous conversations or memory.
2. When answering, combine the user’s latest question with relevant stored knowledge.
3. If memory is too long, summarize key points instead of repeating everything verbatim.
4. Guide the user on practical next steps for biological workflows (BLAST, GROMACS, AutoDock Vina, ChimeraX, etc.), including data transformation or preparation when necessary.
5. If no relevant memory is found, say so honestly and ask clarifying questions.
6. Maintain consistency: once a fact has been given and stored, do not contradict it later unless the user provides an update.
7. Present responses clearly, in steps or options, so that a biologist can decide the best next action.

Always act as a reliable memory agent that helps researchers make sense of their data and choose the right tools.
"""

input_text = "How should I prepare my FASTA file for BLAST?"

#Helper function: get extra parameters
def get_additional_model_fields(modelId):

    return dict_add_params.get(modelId)
    #{"top_k": top_k, "max_tokens": max_tokens}}

#Extract the output
def get_converse_output(response_obj):
    ret_messages=[]
    output_message = response_obj['output']['message']
    role_out = output_message['role']

    for content in output_message['content']:
        ret_messages.append(content['text'])
        
    return ret_messages, role_out

response = generate_conversation(bedrock_client, models_dict[claude3], system_text, input_text)

messages, role = get_converse_output(response)
print(messages)

#Semantic Similarity with Amazon Titan Embeddings
#Calls Bedrock's invoke_model() API
#Sends the text in JSON as {"inputText:"}
#Gets back an embedding (a list of numbers)
#Returns embedding as a NumPy array
def embed_text_input(bedrock_client, prompt_data, modelId="amazon.titan-embed-text-v1"):
    accept = "application/json"
    contentType = "application/json"
    body = json.dumps({"inputText": prompt_data})
    response = bedrock_client.invoke_model(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )
    response_body = json.loads(response.get("body").read())
    embedding = response_body.get("embedding")
    return np.array(embedding)

#Langchain components we need 
from langchain.docstore.document import Document
from langchain.document_loaders import TextLoader
from langchain.embeddings import BedrockEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS

from langchain.document_loaders import PyPDFLoader
from langchain.tools.retriever import create_retriever_tool
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import CharacterTextSplitter


#Titan embeddings via Langchain
br_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0", client=bedrock_client)

#Creating the web scraper
from langchain.docstore.document import Document
from strands import Agent, tool
from strands_tools.tavily import tavily_search, tavily_extract, tavily_crawl, tavily_map
import json

WEB_SCRAPER_SYSTEM_PROMPT = """
You are a web scraper that scrapes biological scholarly articles from the web.
1. Use your research tools to find the most recent and relevant articles based on the keywords in the user input.
2. Always include structured metadata (title, authors, journal, date, source_url).
3. Keep abstracts concise but informative.
4. If you cannot find relevant articles, say so.
"""

@tool
def web_scraper_assistant(user_input: str):
    try:
        print("Searching scholarly articles (this may take ~5mins...☕)")
        
        researcher_agent = Agent(
            system_prompt=WEB_SCRAPER_SYSTEM_PROMPT,
            callback_handler=None,
            tools=[tavily_search, tavily_extract, tavily_crawl, tavily_map],
        )

        researcher_response = researcher_agent(
            f"Research: '{user_input}'. "
            "Return results as JSON with fields: title, authors, journal, pub_date, url, abstract."
        )

        # Try parsing JSON output
        try:
            results = json.loads(str(researcher_response))
        except Exception:
            # If not valid JSON, fall back to raw string
            return [
                Document(
                    page_content=str(researcher_response),
                    metadata={"title": "Untitled", "source": "web_scraper"}
                )
            ]

        docs = []
        for item in results:
            docs.append(
                Document(
                    page_content=item.get("abstract", ""),
                    metadata={
                        "title": item.get("title", "Untitled"),
                        "authors": item.get("authors", "N/A"),
                        "journal": item.get("journal", "N/A"),
                        "pub_date": item.get("pub_date", "N/A"),
                        "source": item.get("url", "web_scraper"),
                    },
                )
            )

        if len(docs) == 0:
            return [
                Document(
                    page_content="No relevant articles found.",
                    metadata={"title": "None", "source": "web_scraper"}
                )
            ]

        return docs

    except Exception as e:
        return [
            Document(
                page_content=f"Error processing your query: {str(e)}",
                metadata={"title": "Error", "source": "web_scraper"}
            )
        ]

# Run the scraper to get structured Documents
docs = web_scraper_assistant("NF1 pathogenicity recent research")

# Safety check
print(f"Number of docs retrieved: {len(docs)}")
print(docs[0].metadata)

#Semantic Similarity with Amazon Titan Embeddings
def embed_text_input(bedrock_client, prompt_data, modelId="amazon.titan-embed-text-v2:0"):
    accept = "application/json"
    contentType = "application/json"
    body = json.dumps({"inputText": prompt_data})
    response = bedrock_client.invoke_model(
        body=body, modelId=modelId, accept=accept, contentType=contentType
    )
    response_body = json.loads(response.get("body").read())
    embedding = response_body.get("embedding")
    return np.array(embedding)

#JUST TESTING
user_input = 'Things to do that are productive'
document_1 = 'swimming, site seeing, sky diving'
document_2 = 'cleaning, note taking, studying'

user_input_vector = embed_text_input(bedrock_client, user_input)
document_1_vector = embed_text_input(bedrock_client, document_1)
document_2_vector = embed_text_input(bedrock_client, document_2)

doc_1_match_score = np.dot(user_input_vector, document_1_vector)
doc_2_match_score = np.dot(user_input_vector, document_2_vector)

print(f'"{user_input}" matches "{document_1}" with a score of {doc_1_match_score:.1f}')
print(f'"{user_input}" matches "{document_2}" with a score of {doc_2_match_score:.1f}')

#Simplifying search with Langchain and FAISS
from langchain.docstore.document import Document
from langchain.document_loaders import TextLoader
from langchain.embeddings import BedrockEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS

from langchain.document_loaders import PyPDFLoader
from langchain.tools.retriever import create_retriever_tool
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import CharacterTextSplitter

br_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0", client=bedrock_client)

# Embed PubMed docs into FAISS index
vectorstore = FAISS.from_documents(docs, br_embeddings)

# Create retriever for semantic search
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

query = "How can NF1 missense variants be identified?"
results = retriever.get_relevant_documents(query)

for i, r in enumerate(results, 1):
    print(f"\nResult {i}")
    print("Title:", r.metadata.get("title"))
    print("Authors:", r.metadata.get("authors"))
    print("Journal:", r.metadata.get("journal"))
    print("Date:", r.metadata.get("pub_date"))
    print("Source:", r.metadata.get("source"))
    print("Abstract snippet:", r.page_content[:300], "...")

query = "Explain how NF1 pathogenicity is predicted"
retrieved_docs = retriever.get_relevant_documents(query)

# Concatenate retrieved content into system prompt
context = "\n\n".join([f"Title: {d.metadata['title']}\nAbstract: {d.page_content}" for d in retrieved_docs])

system_text_with_context = system_text + f"\n\nRelevant PubMed articles:\n{context}"

response = generate_conversation(
    bedrock_client,
    models_dict[claude3],
    system_text_with_context,
    query
)

messages, role = get_converse_output(response)
print(messages)


#Split into chunkc: LLM's cant handle super long text directly
split_docs = CharacterTextSplitter(
    chunk_size=2000,
    chunk_overlap=400,
    separator="\n"
).split_documents(docs)

print(f"Number of documents after split and chunking={len(docs)}")


# Comvert to embeddings and store in FAISS
vs = FAISS.from_documents(split_docs, br_embeddings)

#Check index size
print(f"vectorstore_faiss_aws: number of elements in the index={vs.index.ntotal}::")

docs[0]

#Search FAISS vector store
search_results = vs.similarity_search(
    "Explain how NF1 pathogenicity is predicted", k=3
)
print(search_results[0])

#Combining search results with text generation
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import ChatPromptTemplate
from langchain_community.chat_models import BedrockChat
from langchain_core.messages import HumanMessage
from langchain.chains import ConversationChain
from langchain_core.output_parsers import StrOutputParser


SYSTEM_MESSAGE = """
System: Here is some important context which can help inform the questions the Human asks.
Make sure to not make anything up to answer the question if it is not provided in the context.

Context: {context}
"""
HUMAN_MESSAGE = "{text}"

messages = [
    ("system", SYSTEM_MESSAGE),
    ("human", HUMAN_MESSAGE)
]

prompt_data = ChatPromptTemplate.from_messages(messages)

human_input =  "Explain how NF1 pathogenicity is predicted"
search_results = vs.similarity_search(human_input, k=3)
context_string = '\n\n'.join([f'Document {ind+1}: ' + i.page_content for ind, i in enumerate(search_results)])
len(context_string)

human_query =  "Explain how NF1 pathogenicity is predicted"

from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferMemory 
from langchain_aws import ChatBedrock


# turn verbose to true to see the full logs and documents
modelId = models_dict.get(claude3)
cl_llm = ChatBedrock(
    model_id=modelId,
    client=bedrock_client,
    model_kwargs={"temperature": 0.1, 'max_tokens': 100},
)

br_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0", client=bedrock_client)

chain = prompt_data | cl_llm | StrOutputParser()
chain_input = {
        "context": context_string, #"This is a sample context doc", #context_doc,
        "text": human_query,
    }


for chunk in chain.stream(chain_input):
    print(chunk, end="", flush=True)

print(chain.invoke(chain_input))


@tool
def similarity_search(query: str) -> str:
    """
    Search the knowledge base based on the provided query. 

    Args:
        query (str): the query to retrieve relevant knowledge.

    Returns:
        str: The search results

    """
    search_results = vs.similarity_search(query, k=3)
    context_string = '\n\n'.join([f'Document {ind+1}: ' + i.page_content for ind, i in enumerate(search_results)])
    return(context_string)

# System prompt for generating answers from retrieved information
ANSWER_SYSTEM_PROMPT = """
You are a helpful knowledge assistant that provides clear, concise answers based on information retrieved from a knowledge base.

The information from the knowledge base contains document IDs and content preview. Focus on the actual content and 
ignore the metadata.

For any question, use only the content from knowledge base to answer. Use the knowledge base tool only once. 

Your responses should:
1. Be direct and to the point
2. Not mention the source of information (like document IDs or scores)
3. Not include any metadata or technical details
4. Be conversational but brief
5. Acknowledge when information is conflicting or missing
6. Begin the response with \n

When analyzing the knowledge base results:
- Higher scores (closer to 1.0) indicate more relevant results
- Look for patterns across multiple results
- Prioritize information from results with higher scores
- Ignore any JSON formatting or technical elements in the content
- If there is no relevant results from the knowledge base, respond by saying that you could not find any information from the knowledge base.
- Do not provide anything apart from what is available from the knowledge base.

Example response for conflicting information:
"Based on my records, I have both July 4 and August 8 listed as your birthday. Could you clarify which date is correct?"

Example response for clear information:
"Your birthday is on July 4."

Example response for missing information:
"I don't have any information about your birthday stored."
"""

kb_agent = Agent(system_prompt=ANSWER_SYSTEM_PROMPT, model = "us.anthropic.claude-3-7-sonnet-20250219-v1:0", tools=[similarity_search])

response = kb_agent("Could you tell me the most recent research talked about in PubMed")

response = kb_agent("Could you give me the metadata for the most recent research you found")