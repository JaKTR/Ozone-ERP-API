import uvicorn
from fastapi import FastAPI
from starlette import status
from starlette.responses import RedirectResponse

app = FastAPI()


@app.get("/")
async def root() -> RedirectResponse:
    return RedirectResponse("/docs", status_code=status.HTTP_303_SEE_OTHER)

if __name__ == "__main__":
    uvicorn.run("modules.racs:app", host="127.0.0.1", port=5000, log_level="debug", reload=True)