# FastAPI SQLite CRUD API

This is a simple FastAPI project that provides a RESTful API for performing CRUD (Create, Read, Update, Delete) operations on a "person" resource. The API interacts with an SQLite database and offers dynamic parameter handling.
It was built as a requirement for stage 3 progress at HNG internship 2023 for which I'm a participant.

## Features

- Create a new person record.
- Retrieve details of a person by name.
- Update the details of an existing person.
- Delete a person record.
- Flexible parameter handling - CRUD operations can be performed using the person's name.
- SQLite database backend.
- Documentation outlining request/response formats, setup instructions, and sample API usage.

## Installation

To run this project locally, follow these steps:

1. Clone the GitHub repository:

   ```bash
   git clone https://github.com/IgweDaniel/HNG_TASK-2.git
   ```

2. Change to the project directory:

   ```bash
   cd HNG_TASK-2
   ```

3. Install the required Python dependencies using Poetry:

   ```bash
   poetry install
   ```

4. Start the FastAPI server:

   ```bash
   poetry run uvicorn main:app --reload
   ```

   The API will be accessible at `http://localhost:8000`.

## API Documentation

For detailed information on how to use the API, refer to the [API Documentation](DOCUMENTATION.md).

The documentation covers standard formats for requests and responses, sample usage of the API, known limitations, and setup instructions for both local and server deployment.

## Testing

You can run tests for the API using the following command:

```bash
poetry run pytest
```

This will execute the unit tests to ensure that all CRUD operations and edge cases are handled correctly.




