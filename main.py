from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Field, Session, SQLModel, create_engine, select

# ==========================================
# 1. DEFINICIÓN DE MODELOS (SQLModel)
# ==========================================

class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    email: str
    activo: bool = Field(default=True)

class Libro(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    titulo: str
    autor: str
    # Llave foránea para relacionar el libro con un usuario
    usuario_id: Optional[int] = Field(default=None, foreign_key="usuario.id")

# ==========================================
# 2. CONFIGURACIÓN DE BASE DE DATOS
# ==========================================

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# engine es el motor de conexión a la base de datos
engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Dependencia para obtener la sesión de la base de datos en cada petición
def get_session():
    with Session(engine) as session:
        yield session

# ==========================================
# 3. INICIALIZACIÓN DE FASTAPI
# ==========================================

app = FastAPI(
    title="API de Usuarios y Libros", 
    description="API RESTful con FastAPI y SQLModel"
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# ==========================================
# 4. RUTAS CRUD: USUARIOS
# ==========================================

@app.post("/usuarios/", response_model=Usuario, tags=["Usuarios"])
def crear_usuario(usuario: Usuario, session: Session = Depends(get_session)):
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario

@app.get("/usuarios/", response_model=List[Usuario], tags=["Usuarios"])
def leer_usuarios(session: Session = Depends(get_session)):
    usuarios = session.exec(select(Usuario)).all()
    return usuarios

@app.get("/usuarios/{usuario_id}", response_model=Usuario, tags=["Usuarios"])
def leer_usuario(usuario_id: int, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

@app.put("/usuarios/{usuario_id}", response_model=Usuario, tags=["Usuarios"])
def actualizar_usuario(usuario_id: int, usuario_data: Usuario, session: Session = Depends(get_session)):
    usuario_db = session.get(Usuario, usuario_id)
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    usuario_db.nombre = usuario_data.nombre
    usuario_db.email = usuario_data.email
    usuario_db.activo = usuario_data.activo
    
    session.add(usuario_db)
    session.commit()
    session.refresh(usuario_db)
    return usuario_db

@app.delete("/usuarios/{usuario_id}", tags=["Usuarios"])
def eliminar_usuario(usuario_id: int, session: Session = Depends(get_session)):
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    session.delete(usuario)
    session.commit()
    return {"mensaje": "Usuario eliminado exitosamente"}

# ==========================================
# 5. RUTAS CRUD: LIBROS
# ==========================================

@app.post("/libros/", response_model=Libro, tags=["Libros"])
def crear_libro(libro: Libro, session: Session = Depends(get_session)):
    session.add(libro)
    session.commit()
    session.refresh(libro)
    return libro

@app.get("/libros/", response_model=List[Libro], tags=["Libros"])
def leer_libros(session: Session = Depends(get_session)):
    libros = session.exec(select(Libro)).all()
    return libros

@app.get("/libros/{libro_id}", response_model=Libro, tags=["Libros"])
def leer_libro(libro_id: int, session: Session = Depends(get_session)):
    libro = session.get(Libro, libro_id)
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return libro

@app.put("/libros/{libro_id}", response_model=Libro, tags=["Libros"])
def actualizar_libro(libro_id: int, libro_data: Libro, session: Session = Depends(get_session)):
    libro_db = session.get(Libro, libro_id)
    if not libro_db:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    
    libro_db.titulo = libro_data.titulo
    libro_db.autor = libro_data.autor
    libro_db.usuario_id = libro_data.usuario_id
    
    session.add(libro_db)
    session.commit()
    session.refresh(libro_db)
    return libro_db

@app.delete("/libros/{libro_id}", tags=["Libros"])
def eliminar_libro(libro_id: int, session: Session = Depends(get_session)):
    libro = session.get(Libro, libro_id)
    if not libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    session.delete(libro)
    session.commit()
    return {"mensaje": "Libro eliminado exitosamente"}