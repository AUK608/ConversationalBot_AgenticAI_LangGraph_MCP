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

secret_key=os.getenv('UPMCP_SECRET_KEY')
algo=os.getenv('ALGORITHM')
client_id=os.getenv('CLIENT_UPMCP_ID')
client_secret=os.getenv('CLIENT_UPMCP_SECRET')
common_url=os.getenv('COMMON_URL')
updatedb_port=int(os.getenv('UPDATEDB_PORT'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MCP_UpdateDB_Data")

mcp = FastMCP("UpdateDB_Server")#, host="127.0.0.1", port="8031")
app = FastAPI(title="UpdateDB_FastAPI")

transport = SseServerTransport("/messages/")

class QueueUpInput(BaseModel):
    QueueUpValue: str
    CaseNumber: str

@mcp.tool()
def update_queue(queueup_val: QueueUpInput):
    """
    Gets the Queue or Case Owner value as string, Case Number as string and updates the DB with this Queue value for given Case Number through api call
   
    Args:
        queueup_val.QueueUpValue (str): Queue or Case Owner value as string
        queueup_val.CaseNumber (str): Case Number value as string

    Returns:
        json_update_data (JSON-Formatted): API response value in JSON format or else exception
    """
    logger.info("Posting data to Queue Update API")

    try:

        #code for authentication with token url, client and client secret to generate token as headers to access the below url
       
        url = "http://127.0.0.1:8888/update_queue"
        params = {"casenum" : str(queueup_val.CaseNumber)}
        data = {"queue" : str(queueup_val.QueueUpValue)}
        response = requests.post(url, json=data, params=params)
        logger.info("\n---\nUpdate Response = = ")
        logger.info(response.text)

        if "Error" in response.text:
            logging.info("\n---\nUpdate Queue Response Error...")
            logging.info(response.text)
            return json.dumps({"Error" : str(response.text)})

        json_update_data = []
        json_update_data.append({
                "Update_Response": str(response.text),
                "Case_Number": str(queueup_val.CaseNumber),
                "Queue_CaseOwner": str(queueup_val.QueueUpValue)
            })

        now_dt = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")    
        #excel_name = f"UpdateDBServerExcel_{queueup_val.CaseNumber}_{queueup_val.QueueUpValue}_{now_dt}.xlsx"
        results_df = pd.DataFrame(json_update_data)
        #results_df.to_excel(os.path.join(updatequeue_path, excel_name), index=False)
        excel_name = f"UpdateDBServerExcel_{queueup_val.CaseNumber}_{queueup_val.QueueUpValue}_{now_dt}.txt"
        with open(os.path.join(r"C:\Tasks\MCP_Multimodal_MultiAgentic_RAG\LangChain_LangGraph_ComplianceCheck\Scripts\Similar_POC_Test\Output\UpdateDB_Server", excel_name), "w") as f:
            f.write(str(results_df))
        logger.info("\n---\njson_lookup_data = = ")
        logger.info(json_update_data)
       
        return json.dumps(json_update_data)

    except Exception as e:
        logger.info("\n---\nUpdate DB Error = = = ")
        logger.info(json.dumps({"Error" : str(traceback.format_exc())}))
        return json.dumps({"Error" : str(traceback.format_exc())})
   
class StatusUpInput(BaseModel):
    StatusUpValue: str
    CaseNumber: str

@mcp.tool()
def update_status(statusup_val: StatusUpInput):
    """
    Gets the Status value as string, Case Number as string and updates the DB with this Status value for given Case Number through api call
   
    Args:
        statusup_val.StatusUpValue (str): Status value as string
        statusup_val.CaseNumber (str): Case Number value as string

    Returns:
        json_update_data (JSON-Formatted): API response value in JSON format or else exception
    """
    logger.info("Posting data to Status Update API")

    try:

        #code for authentication with token url, client and client secret to generate token as headers to access the below url
       
        url = "http://127.0.0.1:8888/update_status"
        params = {"casenum" : str(statusup_val.CaseNumber)}
        data = {"status" : str(statusup_val.StatusUpValue)}
        response = requests.post(url, json=data, params=params)
        logger.info("\n---\nUpdate st Response = = ")
        logger.info(response.text)

        if "Error" in response.text:
            logging.info("\n---\nUpdate Status Response Error...")
            logging.info(response.text)
            return json.dumps({"Error" : str(response.text)})

        json_update_data = []
        json_update_data.append({
                "Update_Response": str(response.text),
                "Case_Number": str(statusup_val.CaseNumber),
                "Status": str(statusup_val.StatusUpValue)
            })

        now_dt = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")    
        #excel_name = f"UpdateDBServerExcel_{statusup_val.CaseNumber}_{statusup_val.StatusUpValue}_{now_dt}.xlsx"
        results_df = pd.DataFrame(json_update_data)
        #results_df.to_excel(os.path.join(updatequeue_path, excel_name), index=False)
        excel_name = f"UpdateDBServerExcel_{statusup_val.CaseNumber}_{statusup_val.StatusUpValue}_{now_dt}.txt"
        with open(os.path.join(r"C:\Tasks\MCP_Multimodal_MultiAgentic_RAG\LangChain_LangGraph_ComplianceCheck\Scripts\Similar_POC_Test\Output\UpdateDB_Server", excel_name), "w") as f:
            f.write(str(results_df))
        logger.info("\n---\njson_lookup_data st = = ")
        logger.info(json_update_data)
       
        return json.dumps(json_update_data)

    except Exception as e:
        logger.info("\n---\nUpdate DB Error = = = ")
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
            raise HTTPException(status_code=401, detail="Update DB Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Update DB Invalid token")
            
    raise HTTPException(status_code=401, detail="Update DB Unauthorized")

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
        raise HTTPException(status_code=401, detail="Update DB Invalid credentials")


@app.get("/health")
def read_root():
    return {"message": "Update DB MCP SSE Server is running..."}

app.mount("/", sse_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=common_url, port=updatedb_port)


