import os
import psycopg

from fastapi import FastAPI, HTTPException

# This will grab the URL we defined in the .env file!
DB_URL = os.getenv("DATABASE_URL")


app = FastAPI()


@app.get("/healthz")
async def root():
    return {"status": "ok"}

@app.get("/db-healthz")
async def db_health():
    try:
        with psycopg.connect(DB_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()
                if result and result[0] == 1:
                    return {"status": "ok", "database": "connected"}
                else:
                    # If we get weird data, it's an internal error
                    raise HTTPException(status_code=500, detail="Unexpected query result")
                    
    except Exception as e:
        # THE SRE WAY: Return a 503 status code so monitoring tools know we are broken
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")