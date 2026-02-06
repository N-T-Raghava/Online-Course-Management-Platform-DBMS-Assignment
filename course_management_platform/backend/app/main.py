from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.routers import auth
from app.routers import course
from app.routers import topic

from app.routers import enrollment
from app.routers import teaching

from app.routers import content

from app.routers import analytics

app = FastAPI()

app.include_router(auth.router)
app.include_router(course.router)
app.include_router(topic.router)
app.include_router(enrollment.router)
app.include_router(teaching.router)
app.include_router(content.router)
app.include_router(analytics.router)

@app.get("/")
def root():
	return RedirectResponse(url="/docs")