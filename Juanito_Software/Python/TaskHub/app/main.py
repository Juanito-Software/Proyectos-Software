from fastapi import FastAPI
from .database import Base, engine
from .routers import auth, tasks


Base.metadata.create_all(bind=engine)

app = FastAPI(title="TaskHub", version="0.1.0")

app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/", tags=["root"])
def root():
    return {"message": "TaskHub API — visita /docs para la documentación interactiva"}
