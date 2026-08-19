from fastapi import FastAPI
from app.api.route.query import router as query_router


app = FastAPI(title="Maritime Knowledge Engine")

app.include_router(query_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
