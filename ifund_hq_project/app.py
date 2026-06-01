from fastapi import FastAPI

from ifund_hq_project.router import router

app = FastAPI(
    title="ETF Hq Project",
    description="ETF tab C-end business interface for plate statistics",
    version="1.0.0",
)

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}
