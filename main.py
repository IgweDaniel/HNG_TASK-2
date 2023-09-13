from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse

from sqlalchemy.orm import Session

import models, schemas

from database import SessionLocal, engine


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/api/", response_model=schemas.Person)
def create_person(person: schemas.PersonCreate, db: Session = Depends(get_db)):
    db_person = (
        db.query(models.Person).filter(models.Person.name == person.name).first()
    )
    if db_person:
        raise HTTPException(status_code=400, detail="name already registered")

    db_person = models.Person(name=person.name, age=person.age)
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person


@app.get("/api/{name}", response_model=schemas.Person)
def read_person(name: str, db: Session = Depends(get_db)):
    db_user = db.query(models.Person).filter(models.Person.name == name).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.put("/api/{name}", response_model=schemas.Person)
def update_person(
    name: str,
    updates: schemas.PersonUpdate,
    db: Session = Depends(get_db),
):
    db_person = db.query(models.Person).filter(models.Person.name == name).first()
    if db_person is None:
        raise HTTPException(status_code=404, detail="User not found")

    for attr, value in updates.model_dump(exclude_none=True).items():
        setattr(db_person, attr, value)
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person


@app.delete("/api/{name}")
def delete_person(
    name: str,
    db: Session = Depends(get_db),
):
    db_person = db.query(models.Person).filter(models.Person.name == name).first()
    if not db_person:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_person)
    db.commit()
    return {"message": "user successfully deleted"}


@app.get("/api/", response_model=list[schemas.Person])
def get_users(db: Session = Depends(get_db)):
    return db.query(models.Person).all()


@app.get("/", response_model=list[schemas.Person])
def read_root():
    return RedirectResponse(url="/docs")
