from fastapi import FastAPI

from app.routers import gym, auth, sessions, routes, attempts

app = FastAPI(
    title="Bouldy API",
    version="1.0.0",
)

app.include_router(gym.router)
app.include_router(auth.router)
app.include_router(sessions.router)
app.include_router(routes.router)
app.include_router(attempts.router)


@app.get("/")
def root():
    return {
        "message": "Welcome to Bouldy API!"
    }