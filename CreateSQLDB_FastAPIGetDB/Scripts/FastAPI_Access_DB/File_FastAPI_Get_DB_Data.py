# fastapi_server.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import pandas as pd
import uvicorn
from pydantic import BaseModel

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Request body schema for update
class UpdatePayload_Queue(BaseModel):
    queue: str

class UpdatePayload_Status(BaseModel):
    status: str

'''@app.get("/fetch-data")
def fetch_data():
    conn = sqlite3.connect("sample_data.db")
    df = pd.read_sql_query("SELECT * FROM cases", conn)
    conn.close()
    print("df = = = ", df)
    return df.to_dict(orient="records")'''

@app.get("/fetch_data")
def fetch_data(queue: str):
    conn = sqlite3.connect("dummy_data.db")
    query = "SELECT * FROM Dummy_Cases"
    params = ()

    if queue:
        query += " WHERE Queue_CaseOwner = ?"
        params = (queue,)

    df = pd.read_sql_query(query, conn, params=params)
    conn.close()

    print("\n -- \n df = = = ", str(df))

    if df.empty:
        return {"Error" : "Couldn't Fetch Data, Might be Issue with Fetching..."}
    
    return df.to_dict(orient="records")

@app.post("/update_queue")
def update_queue(casenum: str, payload: UpdatePayload_Queue):
    conn = sqlite3.connect("dummy_data.db")
    cursor = conn.cursor()
    
    try:
        # Update
        cursor.execute("UPDATE Dummy_Cases SET Queue_CaseOwner = ? WHERE Case_Number = ?", (payload.queue, casenum))
        conn.commit()

        if cursor.rowcount == 0:
            #raise HTTPException(status_code=404, detail="No rows updated")
            return {"Error" : "Couldn't Update Queue Data, Might be Issue with Queue Updating..."}
        
        #return {"Success" : "Queue Data Successfully Updated..."}

        '''# Fetch updated row
        cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
        row = cursor.fetchone()
        columns = [col[0] for col in cursor.description]'''

    except Exception as e:
        conn.close()
        #raise HTTPException(status_code=400, detail=str(e))
        return {"Error" : "Couldn't Update Queue Data, Might be Issue with Queue Updating..."}

    conn.close()

    # Return row as dict inside a list (just like GET)
    #return [dict(zip(columns, row))]
    return {"Success" : "Queue Data Successfully Updated..."}

@app.post("/update_status")
def update_status(casenum: str, payload: UpdatePayload_Status):
    conn = sqlite3.connect("dummy_data.db")
    cursor = conn.cursor()
    
    try:
        # Update
        cursor.execute("UPDATE Dummy_Cases SET Status = ? WHERE Case_Number = ?", (payload.status, casenum))
        conn.commit()

        if cursor.rowcount == 0:
            #raise HTTPException(status_code=404, detail="No rows updated")
            return {"Error" : "Couldn't Update Status Data, Might be Issue with Status Updating..."}
        
        #return {"Success" : "Queue Data Successfully Updated..."}

        '''# Fetch updated row
        cursor.execute("SELECT * FROM users WHERE id = ?", (id,))
        row = cursor.fetchone()
        columns = [col[0] for col in cursor.description]'''

    except Exception as e:
        conn.close()
        #raise HTTPException(status_code=400, detail=str(e))
        return {"Error" : "Couldn't Update Status Data, Might be Issue with Status Updating..."}

    conn.close()

    # Return row as dict inside a list (just like GET)
    #return [dict(zip(columns, row))]
    return {"Success" : "Status Data Successfully Updated..."}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8888)
