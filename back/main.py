
from fastapi import FastAPI
from routers import fight, quest, shop, start, profile

app = FastAPI(title="RPG Bot API")

app.include_router(start.router, prefix="/start", tags=["Start"])
app.include_router(fight.router, prefix="/fight", tags=["Fight"])
app.include_router(shop.router, prefix="/shop", tags=["Shop"])
app.include_router(quest.router, prefix="/quest", tags=["Quest"])
app.include_router(profile.router, prefix="/profile", tags=["Profile"])
