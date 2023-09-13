from uu import Error
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from main import app, get_db
import models

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="module")
def test_db():
    test_db = TestingSessionLocal()
    try:
        yield test_db
    finally:
        test_db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="class")
def delete_person_row(test_db):
    # raise Error()
    # session = test_db()
    try:
        # Delete all rows in the Person model
        test_db.query(models.Person).delete()
        test_db.commit()
    finally:
        test_db.close()


class TestPersonCreate:
    def test_create_with_valid_data(self, test_db):
        person = {"name": "daniel", "age": 34}
        response = client.post(
            "/api/",
            json=person,
        )
        assert response.status_code == 200

        db_person = (
            test_db.query(models.Person)
            .filter(models.Person.name == person["name"])
            .first()
        )

        assert db_person is not None

        assert response.json() == {
            "id": db_person.id,
            "name": db_person.name,
            "age": db_person.age,
            "married": db_person.married,
        }

        assert response.json()["name"] == person["name"] == db_person.name
        assert response.json()["age"] == person["age"] == db_person.age

    @pytest.mark.usefixtures("delete_person_row")
    def test_create_with_invalid_data(slef, test_db):
        person = {"name": 1}
        response = client.post(
            "/api/",
            json=person,
        )
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
        assert "name" in str(data["detail"])

        persons_count = test_db.query(models.Person).count()
        assert persons_count == 0


class TestPersonRetrieve:
    def test_retreive_existing_user_by_name(slef, test_db):
        person = {"name": "igwe", "age": 34}
        db_person = models.Person(**person)
        test_db.add(db_person)
        test_db.commit()
        test_db.refresh(db_person)
        response = client.get(f'/api/{person["name"]}')

        assert response.status_code == 200
        assert response.json() == {
            "id": db_person.id,
            "name": db_person.name,
            "age": db_person.age,
            "married": db_person.married,
        }

    def test_return_404_for_noxexistent_user(self):
        nonexistent_name = "nouser"
        response = client.get(f"/api/{nonexistent_name}")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in str(data["detail"])

    def test_return_all_users(self, test_db):
        people = [
            {"name": "Alice", "age": 30, "married": True},
            {"name": "Bob", "age": 25, "married": False},
            {"name": "Charlie", "married": True},
        ]

        for person in people:
            test_db.add(
                models.Person(**person),
            )

        test_db.commit()
        response = client.get(f"/api/")
        assert response.status_code == 200
        data = response.json()
        for person in people:
            assert person["name"] in str(data)


class TestPersonUpdate:
    def test_update_existing_user(self, test_db):
        # Create a user to update
        initial_data = {"name": "John", "age": 30}
        db_person = models.Person(**initial_data)
        test_db.add(db_person)
        test_db.commit()

        # Update the user's data
        updated_data = {"age": 35}
        response = client.put(f'/api/{initial_data["name"]}', json=updated_data)
        assert response.status_code == 200
        updated_person = response.json()

        assert updated_person["name"] == initial_data["name"]
        assert updated_person["age"] == updated_data["age"]

        # Verify the database is updated
        db_person = (
            test_db.query(models.Person)
            .filter(models.Person.name == initial_data["name"])
            .first()
        )
        assert db_person is not None
        assert db_person.age == updated_data["age"]

    def test_update_nonexistent_user(self):
        non_existent_name = "nonexistent_user"
        updated_data = {"age": 35}
        response = client.put(f"/api/{non_existent_name}", json=updated_data)
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "User not found" in str(data["detail"])


class TestPersonDelete:
    @pytest.mark.usefixtures("delete_person_row")
    def test_delete_existing_user(self, test_db):
        # Create a user to delete
        user_to_delete = {"name": "Alice", "age": 25}
        db_person = models.Person(**user_to_delete)
        test_db.add(db_person)
        test_db.commit()

        response = client.delete(f'/api/{user_to_delete["name"]}')
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "user successfully deleted"

        # Verify the user is deleted from the database
        db_person = (
            test_db.query(models.Person)
            .filter(models.Person.name == user_to_delete["name"])
            .first()
        )
        assert db_person is None

    def test_delete_nonexistent_user(self):
        non_existent_name = "nonexistent_user"
        response = client.delete(f"/api/{non_existent_name}")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "User not found" in str(data["detail"])
