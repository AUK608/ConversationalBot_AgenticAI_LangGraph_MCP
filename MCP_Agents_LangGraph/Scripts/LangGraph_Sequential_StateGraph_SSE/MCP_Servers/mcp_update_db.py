import logging
from mcp.server.fastmcp import FastMCP
import pandas as pd
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MCP_Update_DB")

mcp = FastMCP("UpdateDB_Server", host="127.0.0.1", port=8013)

from pydantic import BaseModel

'''class UpDBData(BaseModel):
    queue: str
    case_status: str

class UpDBInput(BaseModel):
    updb_data: UpDBData'''

@mcp.tool()
def update_db(record: list):
#def update_db(input_rec: UpDBInput):
    """
    get the values in form of dictionary to update the db
    """

    logger.info(f"Updating database with record: {input}")
    now = datetime.datetime.now()
    filename_datetime = now.strftime("%Y%m%d_%H%M%S")
    df = pd.DataFrame(record)
    df.to_excel("db_update" + str(filename_datetime) + ".xlsx", index=False)
    # Simulate database update
    logger.info("Database update completed.")

if __name__ == "__main__":
    mcp.run(transport="sse")
