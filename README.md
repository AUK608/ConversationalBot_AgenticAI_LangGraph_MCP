# ConversationalBot_AgenticAI_LangGraph_MCP
- Sample data is created in sqlite(data can be viewed using sqlite-web - https://github.com/coleifer/sqlite-web), to acces the data, FastAPI is used(scripts and requirements.txt is kept in CreateSQLDB_FastAPIGetDB.zip)
- Streamlit based Conversational Bot to access the above data using MCP Client(using langchain_mcp_adapters) with LangGraph's Prebuilt Supervisor Agents & Sequential flow-MCP Server connection with SSE, and JWT(scripts are in MCPClient_MCPServer_LangGraph_Scripts.zip)
- Instead of SSE connection, streamable-http can be used as well
