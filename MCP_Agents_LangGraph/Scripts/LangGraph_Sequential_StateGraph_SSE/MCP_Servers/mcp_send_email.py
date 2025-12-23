import logging
from mcp.server.fastmcp import FastMCP
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MCP_Send_Email")

mcp = FastMCP("SendEmail_Server", host="127.0.0.1", port=8014)

from pydantic import BaseModel

class EmailData(BaseModel):
    to: str
    message: str

class EmailInput(BaseModel):
    email_data: EmailData

@mcp.tool()
#def send_email(email_data: dict):
def send_email(input_email: EmailInput):
    """
    get the values in form of dictionary having keys as 'to' for the email address from a column and key as 'message' for message to be sent to email
    """
    print("email_data= = = = ", input_email)
    email_data = input_email.email_data
    print("email_data = = ==  = ", email_data)
    #logger.info(f"Sending email to {email_data['to']} with message: {email_data['message']}")
    logger.info(f"Sending email to {email_data.to} with message: {email_data.message}")
    now = datetime.datetime.now()
    filename_datetime = now.strftime("%Y%m%d_%H%M%S")
    with open("send_email" + str(filename_datetime) + ".txt", "a") as f:
        f.write(f"Sending email to {email_data.to} with message: {email_data.message}\n")
    # Simulate email sending
    logger.info("Email sent successfully.")

if __name__ == "__main__":
    mcp.run(transport="sse")
