from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.database import engine
from app.utils.db_utils import sync_postgres_serial_sequences

from app.routers import auth
from app.routers import course
from app.routers import topic

from app.routers import enrollment
from app.routers import teaching

from app.routers import content

from app.routers import analytics

from app.routers import admin
from app.routers import moderation

app = FastAPI()


@app.on_event("startup")
def on_startup():
	# Attempt to sync Postgres serial sequences to avoid duplicate PK errors
	try:
		sync_postgres_serial_sequences(engine)
	except Exception:
		# swallow errors to avoid preventing app startup
		pass

app.include_router(auth.router)
app.include_router(course.router)
app.include_router(topic.router)
app.include_router(enrollment.router)
app.include_router(teaching.router)
app.include_router(content.router)
app.include_router(analytics.router)
app.include_router(admin.router)
app.include_router(moderation.router)

@app.get("/")
def root():
	return RedirectResponse(url="/docs")