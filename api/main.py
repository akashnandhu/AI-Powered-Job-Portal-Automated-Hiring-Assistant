from fastapi import FastAPI
from fastapi.responses import JSONResponse
from .routers import resume, jobs

app = FastAPI(
    title="AI ATS Platform API",
    description="REST API for AI-powered resume screening system",
    version="1.0.0"
)

# Exception handler for standard error format
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(exc)
            }
        }
    )

from fastapi.openapi.utils import get_openapi

app.include_router(resume.router, tags=["Resume Processing"])
app.include_router(jobs.router, tags=["Async Job Management"])

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="AI ATS Platform API",
        description="REST API for AI-powered resume screening system",
        version="1.0.0",
        routes=app.routes,
    )
    # Remove 422 Validation Error from Swagger docs
    for path in openapi_schema.get("paths", {}).values():
        for method in path.values():
            if "422" in method.get("responses", {}):
                del method["responses"]["422"]
                
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

@app.get("/")
def health_check():
    return {"status": "healthy"}
