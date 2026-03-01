from pydantic import BaseModel

class MetricPayload(BaseModel):
    user_id: int
    metric_name: str
    metric_value: float