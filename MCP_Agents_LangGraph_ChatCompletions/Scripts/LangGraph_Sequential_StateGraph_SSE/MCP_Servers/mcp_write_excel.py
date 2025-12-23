import logging
import pandas as pd
from mcp.server.fastmcp import FastMCP
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MCP_Write_Excel")

mcp = FastMCP("WriteExcel_Server", host="127.0.0.1", port=8012)

@mcp.tool()
def write_excel(data: list):
    logger.info(f"Writing to Excel file: {data}")
    df = pd.DataFrame(data)
    now = datetime.datetime.now()
    filename_datetime = now.strftime("%Y%m%d_%H%M%S")
    df.to_excel("output_excel" + str(filename_datetime) + ".xlsx", index=False)
    logger.info("Excel write operation completed.")

if __name__ == "__main__":
    mcp.run(transport="sse")
