import logging
from mcp.server.fastmcp import FastMCP
import requests
from pydantic import BaseModel
import os
import traceback
import json
import datetime
import pandas as pd

from fastapi import  FastAPI, HTTPException, Request
from starlette.applications import Starlette
from starlette.routing import Route, Mount
import jwt
from mcp.server.sse import SseServerTransport

from dotenv import load_dotenv

load_dotenv()

secret_key=os.getenv('LUMCP_SECRET_KEY')
algo=os.getenv('ALGORITHM')
client_id=os.getenv('CLIENT_LUMCP_ID')
client_secret=os.getenv('CLIENT_LUMCP_SECRET')
common_url=os.getenv('COMMON_URL')
lookup_port=int(os.getenv('LOOKUP_PORT'))


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MCP_LookUp_Data")

mcp = FastMCP("LookUp_Queue_Server")#, host="127.0.0.1", port="8030")
app = FastAPI(title="Look_Up_FastAPI")

transport = SseServerTransport("/messages/")

class QueueInput(BaseModel):
    QueueValue: str

@mcp.tool()
def look_up_queue(queue_val: QueueInput):
    """
    Gets the Queue value as string and fetches the data through api call
   
    Args:
        queue_val (str): Queue value as string

    Returns:
        json_lookup_data (JSON-Formatted): API fetched data in JSON format or else exception
    """
    logger.info("Fetching data from Queue Search API")

    try:
       
       #code for authentication with token url, client and client secret to generate token as headers to access the below url
        
        params = {"queue" : str(queue_val.QueueValue)}
        url = "http://127.0.0.1:8888/fetch_data"

        response = requests.get(url, json=None, params=params)
        logger.info("\n---\nSearch Response = = ")
        logger.info(response.text)

        if "Error" in response.text:
            logging.info("\n---\nLook Up Response Error...")
            logging.info(response.text)
            return json.dumps({"Error" : str(response.text)})

        res = response.json()
        json_lookup_data = res
       
        now_dt = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        #excel_name = f"LookUpServerExcel_{queue_val.QueueValue}_{now_dt}.xlsx"
        results_df = pd.DataFrame(json_lookup_data)
        #results_df.to_excel(os.path.join(lookup_path, excel_name), index=False)
        excel_name = f"LookUpServerExcel_{queue_val.QueueValue}_{now_dt}.txt"
        with open(os.path.join(r"C:\Tasks\MCP_Multimodal_MultiAgentic_RAG\LangChain_LangGraph_ComplianceCheck\Scripts\Similar_POC_Test\Output\LookUp_Server", excel_name), "w") as f:
            f.write(str(results_df))
        logger.info("\n---\njson_lookup_data = = ")
        logger.info(json_lookup_data)
           
        return json.dumps(json_lookup_data)

    except Exception as e:
        logger.info("\n---\nLook Up Error = = = ")
        logger.info(json.dumps({"Error" : str(traceback.format_exc())}))
        return json.dumps({"Error" : str(traceback.format_exc())})

'''if __name__ == "__main__":
    mcp.run(transport="sse")'''

def check_auth(request: Request):
    auth = request.headers.get("authorization", "")        
    if auth.startswith("Bearer "):
        token = auth.split(" ", 1)[1]
        try:
            payload = jwt.decode(token, secret_key, algorithms=[algo])
            return True
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Look Up Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Look Up Invalid token")
            
    raise HTTPException(status_code=401, detail="Look Up Unauthorized")

async def handle_sse(request):
    check_auth(request=request)
    # Prepare bidirectional streams over SSE
    async with transport.connect_sse(
        request.scope,
        request.receive,
        request._send
    ) as (in_stream, out_stream):
        # Run the MCP server: read JSON-RPC from in_stream, write replies to out_stream
        await mcp._mcp_server.run(
            in_stream,
            out_stream,
            mcp._mcp_server.create_initialization_options()
        )


#Build a small Starlette app for the two MCP endpoints
sse_app = Starlette(
    routes=[
        Route("/sse", handle_sse, methods=["GET"]),
        # Note the trailing slash to avoid 307 redirects
        Mount("/messages/", app=transport.handle_post_message)
    ]
)

CLIENTS = {
    client_id: client_secret
}

class TokenRequest(BaseModel):
    client_id: str
    client_secret: str

@app.post("/token")
def generate_token(request: TokenRequest):
    if request.client_id in CLIENTS and CLIENTS[request.client_id] == request.client_secret:
        payload = {
            "sub": request.client_id,
            "exp": datetime.datetime.now() + datetime.timedelta(minutes=60)
        }
        token = jwt.encode(payload, secret_key, algorithm=algo)
        return {"access_token": token}
    else:
        raise HTTPException(status_code=401, detail="Look Up Invalid credentials")


@app.get("/health")
def read_root():
    return {"message": "Look UP MCP SSE Server is running..."}

app.mount("/", sse_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=common_url, port=lookup_port)
