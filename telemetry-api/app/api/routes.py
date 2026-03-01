import psycopg
from fastapi import APIRouter, HTTPException
from app.core.config import DATABASE_URL
from app.schemas.telemetry import MetricPayload

router = APIRouter()


@router.get("/healthz")
async def root():
    return {"status": "ok"}

@router.get("/db-healthz")
async def db_health():
    try:
        with psycopg.connect(DATABASE_URL) as conn:
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

@router.post("/metrics", status_code=201)
async def record_metric(payload: MetricPayload):
    try:
        with psycopg.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                # 1. The SQL Command with safe placeholders
                sql = """
                    INSERT INTO metrics (user_id, metric_name, metric_value)
                    VALUES (%s, %s, %s);
                """
                
                # 2. Execute the command and pass the Pydantic data as a tuple
                cur.execute(
                    sql, 
                    (payload.user_id, payload.metric_name, payload.metric_value)
                )
                
                # 3. CRITICAL: Save the transaction!
                conn.commit()
                
                return {"status": "success", "message": "Metric recorded successfully"}
                
    except Exception as e:
        # If the user_id doesn't exist, Postgres will throw a Foreign Key error here
        raise HTTPException(status_code=500, detail=f"Failed to insert metric: {str(e)}")