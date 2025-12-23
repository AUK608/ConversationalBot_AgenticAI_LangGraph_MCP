import logging
from mcp.server.fastmcp import FastMCP
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MCP_Get_Data")
print("Available......")

mcp = FastMCP("GetAllData_Server", host="127.0.0.1", port=8010)

@mcp.tool()
def get_alldata():
    print("Inside......")
    logger.info("Fetching data from the database.")
    # Simulate data retrieval
    '''data = {
        {"column1": "not okay", "column2": "value2", "column3": "email1@example.com"},
        {"column1": "okay", "column2": "value4", "column3": "email2@example.com"}
    }'''

    data = requests.get("http://127.0.0.1:8888/fetch-data").text

    logger.info(f"Data retrieved: {data}")
    return data

if __name__ == "__main__":
    print("Entered......")
    mcp.run(transport="sse")
