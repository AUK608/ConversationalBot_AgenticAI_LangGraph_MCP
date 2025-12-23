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
logger = logging.getLogger("MCP_LookUp_Data")

mcp = FastMCP("LookUp_Queue_Server", host="127.0.0.1", port="8030")

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

if __name__ == "__main__":
    mcp.run(transport="sse")
