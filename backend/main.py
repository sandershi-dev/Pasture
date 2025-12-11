# main.py
from fastapi import FastAPI
from controllers.User import router as UserController
from controllers.Tenant import router as TenantController


app = FastAPI(title="MVC User API")

# Register controllers
app.include_router(UserController)
app.include_router(TenantController)



@app.get("/")
def root():
    return {"message": "User API running"}