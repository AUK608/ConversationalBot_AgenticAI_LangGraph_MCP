import logging
from mcp.server.fastmcp import FastMCP
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MCP_Write_Text")

mcp = FastMCP("WriteText_Server", host="127.0.0.1", port=8011)

@mcp.tool()
def write_text(info: str):
    logger.info(f"Writing to text file: {info}")
    now = datetime.datetime.now()
    filename_datetime = now.strftime("%Y%m%d_%H%M%S")
    with open("output_text"+str(filename_datetime)+".txt", "a") as f:
        f.write(info + "\n")
    logger.info("Write operation completed.")

if __name__ == "__main__":
    mcp.run(transport="sse")
