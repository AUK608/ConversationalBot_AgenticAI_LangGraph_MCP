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
logger = logging.getLogger("MCP_UpdateDB_Data")

mcp = FastMCP("UpdateDB_Server", host="127.0.0.1", port="8031")

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

if __name__ == "__main__":
    mcp.run(transport="sse")

