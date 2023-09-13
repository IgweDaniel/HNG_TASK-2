from pydantic import BaseModel, ConfigDict


class PersonBase(BaseModel):
    name: str


class PersonCreate(PersonBase):
    age: int | None = None


class PersonUpdate(BaseModel):
    name: str | None = None
    age: int | None = None
    married: bool = False


class Person(PersonBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    age: int
    married: bool
