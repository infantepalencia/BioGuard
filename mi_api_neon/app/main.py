from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  
from .routers import usuarios, especies, incidentes, tickets

app = FastAPI(
    title="API Fauna Universitaria con NeonDB",
    description="Backend en FastAPI conectado a NeonDB y consumido por Angular."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://127.0.0.1:4200"],
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"], )

app.include_router(usuarios.router, prefix="/api/v1")
app.include_router(especies.router, prefix="/api/v1")
app.include_router(incidentes.router, prefix="/api/v1")
app.include_router(tickets.router, prefix="/api/v1")

@app.get("/")
def root():
    return {
        "status": "API Funcionando Correctamente",
        "documentation": "Ingresa a /docs para ver los endpoints interactivos"
    }