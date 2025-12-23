import logging
from mcp.server.fastmcp import FastMCP
import requests
from pydantic import BaseModel
import os
import traceback
import json
import datetime
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MCP_SendEmail_Data")

mcp = FastMCP("SendEmail_Server", host="127.0.0.1", port="8032")

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

if __name__ == "__main__":
    mcp.run(transport="sse")
