# import the required methods
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from typing import List, Literal
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage, AIMessage

import os
from dotenv import load_dotenv

load_dotenv()

azure_token = os.getenv('AZURE_OPENAI_API_KEY')
api_version = str(os.getenv('AZURE_OPENAI_API_VERSION'))
azure_endpoint_url=os.getenv('AZURE_ENDPOINT_URL')
azure_deploy_url=os.getenv('AZURE_DEPLOYMENT_URL')

#model = ChatGroq(model="llama-3.3-70b-versatile",temperature=0.1)
#model = ChatOllama(model="llama3.2:1b",temperature=0.0,max_new_tokens=500)
model = AzureChatOpenAI(
    azure_deployment="gpt4o",
    max_tokens=1024,
    temperature=0.1,
    api_version=api_version,
    azure_endpoint=azure_endpoint_url,
    api_key=os.getenv('AZURE_OPENAI_API_KEY'),
    )

async def initialize_supervisor(query):
    async with MultiServerMCPClient({
        "GetAllData_Server": {"url": "http://localhost:8010/sse", "transport": "sse"},
        "WriteText_Server": {"url": "http://localhost:8011/sse", "transport": "sse"},
        "WriteExcel_Server": {"url": "http://localhost:8012/sse", "transport": "sse"},
        "UpdateDB_Server": {"url": "http://localhost:8013/sse", "transport": "sse"},
        "SendEmail_Server": {"url": "http://localhost:8014/sse", "transport": "sse"}
    }) as client:

        tools = client.get_tools()

        # define a tool_node with the available tools

        '''def call_model(state: MessagesState):
            response = model.bind_tools(tools).invoke(state["messages"])
            return {"messages": response}'''
        def call_model(state: MessagesState):
            messages = state["messages"]
            tool_messages = [msg for msg in messages if isinstance(msg, ToolMessage)]
            print("\n--\ntool_messages = = = ", tool_messages)
            if tool_messages:
                tool_summary = "\n".join(
                    f"[Tool: {msg.tool_name}] {msg.content}" for msg in tool_messages
                )
                messages.append(
                    HumanMessage(content=f"The tools results:\n{tool_summary}")
                )
            response = model.invoke(messages)
            return {"messages": [response]}

        builder = StateGraph(MessagesState)
        builder.add_node(call_model)
        builder.add_node(ToolNode(tools))
        builder.add_edge(START, "call_model")
        builder.add_conditional_edges(
            "call_model",
            tools_condition,
        )
        builder.add_edge("tools", "call_model")
        agent = builder.compile()

        # display(Image(agent.get_graph().draw_mermaid_png()))

        '''for chunk in agent.stream(
            {"messages": [("user", "Will it rain in Trivandrum today?")]},
            stream_mode="values",):
            chunk["messages"][-1].pretty_print()'''
        
        
        res1 = await agent.ainvoke({"messages":"Show me available data"})
        print("\n res1 = = = = ", res1)
        print("\nresult first = = = ",res1["messages"][-1].content)

        
        res = await agent.ainvoke({"messages":query})
        #print("\n res = = = = ", res)
        #print("\nresult final = = = ",res["messages"][-1].content)
        return res["messages"][-1].content

# For testing purposes
if __name__ == "__main__":
    import asyncio
    query =(
                """
                Retrieve the available data.
                If 'case_status' is 'Completed' then write information to a text file and excel file.
                If 'case_status' is 'Not Completed' then send a email to the address mentioned in 'notify' and also update the db.
                """
            )
    res = asyncio.run(initialize_supervisor(query))
    print(res)