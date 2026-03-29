from fastapi import APIRouter, Depends
from langchain.agents import create_react_agent, Tool
# from langchain.agents.agent_toolkits.react.base import ReActAgentPrompt  # Optionnel : Prompt personnalisé
from langchain_community.tools import DuckDuckGoSearchRun
from models.models import QueryResponse
from auth.oauth2 import get_current_user
from models.models import groq_model
from langchain_core.prompts import PromptTemplate

router_react = APIRouter(tags=["🤖 ReAct Agent"])

# DuckDuckGo search tool
search_tool = DuckDuckGoSearchRun()

tools = [
    Tool(
        name="DuckDuckGo Search",
        func=search_tool.run,
        description="Search the web using DuckDuckGo for up-to-date information."
    ),
    # Add more tools if needed
]

# 👇 Créez un prompt pour l'agent ReAct
prompt_template = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original question

Begin!

Question: {input}
{agent_scratchpad}"""

prompt = PromptTemplate(
    input_variables=["input", "tools", "tool_names", "agent_scratchpad"],
    template=prompt_template
)

# 👇 Maintenant on peut créer l'agent
agent = create_react_agent(llm=groq_model, tools=tools, prompt=prompt)

@router_react.post("/react_agent", response_model=QueryResponse)
async def react_agent(query: str, chat_id: str, current_user: dict = Depends(get_current_user)):
    result = agent.invoke({"input": query})
    return {"answer": result, "sources": []}


##############################

from langchain_community.tools import DuckDuckGoSearchRun , WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
api_wrapper = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=500)
wiki_tool = WikipediaQueryRun(api_wrapper=api_wrapper)

search_tool = DuckDuckGoSearchRun()
tools = [search_tool, wiki_tool]
llm_with_tools = groq_model.bind_tools(tools)


from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import HumanMessage, SystemMessage, AnyMessage
from typing import TypedDict, Annotated, List
import operator


class State(TypedDict):
    messages: Annotated[List[AnyMessage], operator.add]

sys_msg = SystemMessage(content="You can use DuckDuckGo search if needed.")

def agent_node(state: State) -> dict:
    msg_list = state.get("messages", [])
    response = llm_with_tools.invoke([sys_msg] + msg_list)
    return {"messages": [response]}

builder = StateGraph(State)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")


agent_graph = builder.compile()


@router_react.post("/react_agent2", response_model=QueryResponse)
async def react_groq(query: str, chat_id: str, current_user: dict = Depends(get_current_user)):
    state = {"messages": [HumanMessage(content=query)]}
    while True:
        result = agent_graph.invoke(state)
        state["messages"] = result["messages"]
        last = state["messages"][-1]
        if not last.tool_calls:
            return {"answer": last.content, "sources": []}
        # sinon, continue la boucle
