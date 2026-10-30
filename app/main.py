from fastapi import FastAPI
app = FastAPI(title="AutoRent — лабораторные работы 1 и 2")

@app.get("/")
def root():
    return {"status": "ok", "project": "AutoRent"}
