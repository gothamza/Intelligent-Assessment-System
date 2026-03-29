
from fastapi import APIRouter, Depends
from langchain_tavily import TavilySearch, TavilyExtract
from langgraph.graph import StateGraph, START, END
from langchain.agents import create_react_agent
from models.models import *  # or your LLM
from langgraph.prebuilt import ToolNode, tools_condition



Tavily_react = APIRouter(tags=["🤖 Tavily ReAct Agent"])

tavily_search = TavilySearch(
    max_results=5,
    topic="general",
    tavily_api_key = os.getenv("TAVILY_API_KEY")
)

tavily_extract = TavilyExtract( 
    extract_depth="advanced",
    include_images=True,
    format="markdown"
)

tools = [tavily_search, tavily_extract]


llm_with_tools = groq_model.bind_tools(tools)

def agent_node(state: dict) -> dict:
    msg_list = state.get("messages", [])
    # Optionally prepend a system message
    response = llm_with_tools.invoke([SystemMessage(content="You can use Tavily search if needed.")] + msg_list)
    return {"messages": [response]}

def format_results_node(state: dict) -> dict:
    messages = state.get("messages", [])
    # Example: rewrite the last message with improved formatting
    if messages:
        last_msg = messages[-1]
        # Here you can use your LLM or custom formatting logic
        # For example, ask the LLM to rewrite the answer with links and markdown and add the hight and width like this /200/300 in the end of the url
        formatted_content = groq_model.invoke([
            SystemMessage(content="Rewrite the following answer in a clear, well-formatted markdown with clickable links if any URLs are present or images url i want every image to be with it page.use this fromat to show the images ![Image 1](https://example.com/image.jpg),if it just siimple question just answer it without any links or images."),
            HumanMessage(content=last_msg.content)
        ])
        messages[-1] = formatted_content
    return {"messages": messages}


builder_tavily = StateGraph(dict)
builder_tavily.add_node("agent", agent_node)
builder_tavily.add_node("tools", ToolNode(tools))
builder_tavily.add_node("format", format_results_node) 


builder_tavily.add_edge(START, "agent")
# Conditional: agent → tools or agent → format
builder_tavily.add_conditional_edges(
    "agent",
    tools_condition,  # This function inspects the agent output and decides
    {
        "tools": "tools",    # If tools are needed, go to tools node
        "__end__": "format",     # If not, go directly to format node
    }
)
builder_tavily.add_edge("tools", "format")
builder_tavily.add_edge("format", END)



agent_graph_tavily = builder_tavily.compile()

@Tavily_react.post("/tavily_agent_prime",response_model=QueryResponse)
async def react_groq(query: str, chat_id: str, current_user: dict = Depends(get_current_user)):
    state = {"messages": [HumanMessage(content=query)]}
    result = agent_graph_tavily.invoke(state)
    last = result["messages"][-1]
    return {"answer": last.content, "sources": []}