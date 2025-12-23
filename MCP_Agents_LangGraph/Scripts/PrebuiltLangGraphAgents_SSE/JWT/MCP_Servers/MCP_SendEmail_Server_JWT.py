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

secret_key=os.getenv('SEMCP_SECRET_KEY')
algo=os.getenv('ALGORITHM')
client_id=os.getenv('CLIENT_SEMCP_ID')
client_secret=os.getenv('CLIENT_SEMCP_SECRET')
common_url=os.getenv('COMMON_URL')
sendemail_port=int(os.getenv('SENDEMAIL_PORT'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MCP_SendEmail_Data")

mcp = FastMCP("SendEmail_Server")#, host="127.0.0.1", port="8032")
app = FastAPI(title="SendEmail_FastAPI")

transport = SseServerTransport("/messages/")

class SendEmailInput(BaseModel):
    Recepient_ID: str
    Subject: str
    Message_Body: str

@mcp.tool()
def send_email(mail_val: SendEmailInput):
    """
    Gets the Recepient Mail ID as string, Subject for the mail as string, Message Body for the mail as string
   
    Args:
        mail_val.Recepient_ID (str): Recepient Mail ID as string
        mail_val.Subject (str): Subject Content of the Mail as string
        mail_val.Message_Body (str): Message in the Body of the Mail as string

    Returns:
        json_mail_data (JSON-Formatted): Mail response value in JSON format or else exception
    """
    logger.info("Sending Mail Server")

    try:
        logger.info("\n----\nMail To : ")
        logger.info(mail_val.Recepient_ID)
        logger.info("\n----\nMail Subject : ")
        logger.info(mail_val.Subject)
        logger.info("\n----\nMail MSG : ")
        logger.info(mail_val.Message_Body)
        now_dt = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        text_name = f"SendEmail_{mail_val.Recepient_ID}_{now_dt}.txt"
        with open(os.path.join(r"C:\Tasks\MCP_Multimodal_MultiAgentic_RAG\LangChain_LangGraph_ComplianceCheck\Scripts\Similar_POC_Test\Output\SendEmail_Server",text_name), "w") as f:
            f.write("Sending Email To : " + str(mail_val.Recepient_ID) + "\nSubject : " + str(mail_val.Subject) + "\nMessage Body Content : " + str(mail_val.Message_Body))
       
        json_mail_data = [{"Success": mail_val}]
        logger.info("\n---\njson_mail_data = = ")
        logger.info(json_mail_data)
        return json_mail_data

    except Exception as e:
        logger.info("\n---\nSend Email Error = = = ")
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
            raise HTTPException(status_code=401, detail="Send Email Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Send Email Invalid token")
            
    raise HTTPException(status_code=401, detail="Send Email Unauthorized")

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
        raise HTTPException(status_code=401, detail="Send Email Invalid credentials")


@app.get("/health")
def read_root():
    return {"message": "Send Email MCP SSE Server is running..."}

app.mount("/", sse_app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=common_url, port=sendemail_port)
