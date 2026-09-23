from fastapi import FastAPI,HTTPException,requests
import uvicorn

app = FastAPI(
    title="Multi Linguinal application",
    version= "0.0.1",
    summary="API DOC for the backend application which hold the Translation APP"
)


@app.get('/health',tags=['APP Services'], summary="Check API, postgres DB and Redis up and running")
def main():
    return {"status" :"Ok"}


if __name__ == "__main__":
    uvicorn.run("main:app",host="0.0.0.0",port=8080, reload = True)
