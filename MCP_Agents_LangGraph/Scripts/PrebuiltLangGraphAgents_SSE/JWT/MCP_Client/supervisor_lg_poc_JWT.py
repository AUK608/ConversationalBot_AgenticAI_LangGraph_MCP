import logging
import asyncio
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
import aiohttp

from langchain_openai import AzureChatOpenAI
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Supervisor")

from dotenv import load_dotenv

load_dotenv()

# API Key Configuration 
'''groq_api = os.getenv('GROQ_API_KEY')
hf_token = os.getenv('HF_TOKEN')
mistralai_api = os.getenv('MISTRAL_API_KEY')'''
azure_token = os.getenv('AZURE_OPENAI_API_KEY')
api_version = str(os.getenv('AZURE_OPENAI_API_VERSION'))
azure_endpoint_url=os.getenv('AZURE_ENDPOINT_URL')
azure_deploy_url=os.getenv('AZURE_DEPLOYMENT_URL')
lookup_url=os.getenv('LOOKUP_SERVER_URL')
lookup_token=os.getenv('TOKEN_LUMCP_URL')
lookup_cid=os.getenv('CLIENT_LUMCP_ID')
lookup_csec=os.getenv('CLIENT_LUMCP_SECRET')
updatedb_url=os.getenv('UPDATEDB_SERVER_URL')
updatedb_token=os.getenv('TOKEN_UPMCP_URL')
updatedb_cid=os.getenv('CLIENT_UPMCP_ID')
updatedb_csec=os.getenv('CLIENT_UPMCP_SECRET')
sendemail_url=os.getenv('SENDEMAIL_SERVER_URL')
sendemail_token=os.getenv('TOKEN_SEMCP_URL')
sendemail_cid=os.getenv('CLIENT_SEMCP_ID')
sendemail_csec=os.getenv('CLIENT_SEMCP_SECRET')

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

async def get_token(client_id, client_secret, token_url, server_name):
    payload = {"client_id": client_id, "client_secret": client_secret}
    async with aiohttp.ClientSession() as session:
        async with session.post(token_url, json=payload) as resp:
            if resp.status != 200:
                logger.error(f"Failed to get token: {resp.status}")
                raise Exception("Unable to authenticate. Ensure you are using valid credentials")
            data = await resp.json()
            logger.info("Successfully generated token for : ")
            logger.info(str(server_name))
            logger.info("and the token is ")
            logger.info(data)
            return data["access_token"]

async def initialize_supervisor(user_question):

    lookup_auth_token = await get_token(lookup_cid, lookup_csec, lookup_token, "look_up")
    lookup_headers = {"Authorization": f"Bearer {lookup_auth_token}"}
    updatedb_auth_token = await get_token(updatedb_cid, updatedb_csec, updatedb_token, "update_db")
    updatedb_headers = {"Authorization": f"Bearer {updatedb_auth_token}"}
    sendemail_auth_token = await get_token(sendemail_cid, sendemail_csec, sendemail_token, "send_email")
    sendemail_headers = {"Authorization": f"Bearer {sendemail_auth_token}"}

    async with MultiServerMCPClient({
        "LookUp_Queue_Server": {"url": lookup_url, "transport": "sse", "headers": lookup_headers},
        "UpdateDB_Server": {"url": updatedb_url, "transport": "sse", "headers": updatedb_headers},
        "SendEmail_Server": {"url": sendemail_url, "transport": "sse", "headers": sendemail_headers}
    }) as client:
        
        tools = client.get_tools()
        print("\n---\nAvailable Tools = = = ", str([t.name for t in tools]))
        
        get_tools_look = client.server_name_to_tools["LookUp_Queue_Server"]
        lookup_agent = create_react_agent(model, get_tools_look, name="LookUp_Agent",prompt="Strictly use the tool available and return this tools results based on user request")
        
        get_tools_update = client.server_name_to_tools["UpdateDB_Server"]
        updatedb_agent = create_react_agent(model, get_tools_update, name="UpdateDB_Agent",prompt="Strictly use this tool and return this tools results based on user request")

        get_tools_email = client.server_name_to_tools["SendEmail_Server"]
        print("\n---\nget_tools_email = = = = ", get_tools_email)
        sendemail_agent = create_react_agent(model, get_tools_email, name="SendEmail_Agent",prompt="Strictly use this tool and return this tools results based on user request")

        supervisorall = create_supervisor(
            agents=[lookup_agent, updatedb_agent, sendemail_agent],
            model=model,
            prompt=(
        "You are a supervisor overseeing 3 agents:\n"
        "- `lookup_agent`: responsible for retrieving available case data based on queue parameter.\n"
        "- `updatedb_agent`: responsible for updating values based on case number and queue(1 tool) or case number and status(another tool).\n"
        "- `sendemail_agent`: responsible for sending emails(pass info as dictionary with email required fields of 'recepient id', 'subject' and 'message' to tool) Based on User Prompt Modifications Done, generate the correct subject and message content.\n\n"
        "Your task is to delegate user requests step-by-step to the correct agent. "
        "Strictly call respective tools from respective agents and return results as it is based on user request and what the tool returns, dont mention any other thing apart from tool output."
        )
        ).compile()
        logger.info("Supervisor initialized.")
        
        response_sup = await supervisorall.ainvoke({"messages":user_question})

        #print("In All Response_sup = = = = = = ", response_sup)
        #print("in response_sup = = = = = ", response_sup["messages"][-1].content)

        return response_sup["messages"][-1].content


'''# For testing purposes
if __name__ == "__main__":
    import asyncio

    prompt = (
        """Retrieve available data. 
        If 'column1' is 'not okay', write the information to a text file and an Excel sheet. 
        If 'column1' is 'okay', send an email to the address mentioned in 'column3' and also update the db."""
        )
    
    res = asyncio.run(initialize_supervisor(user_question=prompt))
    print("res sup all = = = = = = = ", res)'''