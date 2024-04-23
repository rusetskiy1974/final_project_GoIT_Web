import uvicorn
from fastapi import FastAPI, HTTPException, Depends

from src.database.db import get_db

from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.routes import auth, images

app = FastAPI(title="PhotoShare")

app.include_router(auth.router, prefix="/api")
app.include_router(images.router, prefix="/api")


@app.get("/")
def index():
    return {"message": "PhotoShare Application"}


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")

if __name__ == '__main__':
    # uvicorn.run(app, host="localhost", port=8000)
    uvicorn.run("main:app", host="localhost", port=9000, reload=True)
