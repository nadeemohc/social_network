# Social Network API

Welcome to the **Social Network API** project! This repository contains the backend API for a social networking application built using Django and Django REST Framework. It includes various features like user authentication, friend request management, and user search functionality.

## Table of Contents

- [Project Description](#project-description)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Docker Setup](#docker-setup)
- [Design Choices](#design-choices)

## Project Description

The **Social Network API** is designed to handle common social networking operations, such as:
- User signup and login with JWT authentication.
- Sending, accepting, and rejecting friend requests.
- Blocking and unblocking users.
- Searching for users by name or email.
  
This API is optimized for performance and scalability, with rate limiting, caching, and efficient database queries.

## Features

- **User Authentication**: JWT-based authentication for secure login, token refresh, and user management.
- **Friend Request Management**: Send, accept, reject, and block users with friend request functionalities.
- **Rate Limiting**: Protects against abuse by limiting the number of friend requests and other actions within a time frame.
- **User Search**: Efficient search of users by email or name, with PostgreSQL full-text search.
- **Redis Caching**: Improves performance by caching frequently accessed data.
- **Pagination**: Handle large datasets with paginated responses for friend lists and search results.

## Installation

### Prerequisites

- Python 3.x
- PostgreSQL installed and running
- Redis installed and running
- Docker and Docker Compose
- Virtual environment (optional but recommended)

### Setup

1. Clone the repository:

    ```sh
    git clone https://github.com/yourusername/social-network-api.git
    cd social-network-api
    ```

2. If not using Docker, create and activate a virtual environment:

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required dependencies:

    ```sh
    pip install -r requirements.txt
    ```

4. Set up PostgreSQL and Redis, then configure them in `settings.py`.

5. Run database migrations:

    ```sh
    python manage.py migrate
    ```

6. Create a superuser for the admin panel:

    ```sh
    python manage.py createsuperuser
    ```

7. Run the development server:

    ```sh
    python manage.py runserver
    ```

## Docker Setup

### Prerequisites

Make sure you have Docker and Docker Compose installed on your machine.

### Running with Docker

To run the entire application, including PostgreSQL and Redis, with Docker, follow these steps:

1. Ensure that your `.env` file is correctly configured. Here's an example:

    ```env
    DJANGO_SECRET_KEY='django project's secret key'
    DATABASE_URL=postgres://db_user:db_password@db_host:db_port/db_name
    ```

2. Build the Docker containers:

    ```sh
    docker-compose build
    ```

3. Run the Docker containers:

    ```sh
    docker-compose up
    ```

    This will:
    - Build the Django app (`web` service) based on the `Dockerfile`.
    - Set up a PostgreSQL database (`db` service) on port `5433`.
    - Set up Redis (`redis` service) on port `6380`.

4. Once the containers are up, the application will be available at `http://localhost:8000`.

5. To apply database migrations, run:

    ```sh
    docker-compose exec web python manage.py migrate
    ```

6. To create a superuser for accessing the admin panel, run:

    ```sh
    docker-compose exec web python manage.py createsuperuser
    ```

7. To stop the application, press `Ctrl+C` or run:

    ```sh
    docker-compose down
    ```

### Key Docker Services

- **web**: The Django web application, served on port `8000`.
- **db**: The PostgreSQL database, accessible via port `5433`.
- **redis**: Redis cache, served on port `6380`.

## Usage

<!-- ### Postman Collection

A Postman collection is provided to facilitate testing of API endpoints. You can find the collection in the repository at:
[Postman Collection](./postman-collection.json). -->

To use it:

1. Open Postman.
2. Click on `Import`.
3. Select the `postman-collection.json` file.
4. All available API requests will be imported into Postman for quick evaluation.

### Key Endpoints

- **POST** `/login/`: Login using email or username.
- **POST** `/refresh/`: Refresh the access token using the refresh token.
- **POST** `/friend-request/send/`: Send a friend request.
- **POST** `/friend-request/accept/`: Accept a friend request.
- **POST** `/friend-request/reject/`: Reject a friend request.
- **GET** `/users/search/`: Search for users by name or email.

## API Documentation

For detailed API documentation including request and response structures, please refer to the online [API Documentation](https://documenter.getpostman.com/view/38401207/2sAXqv4L4M).

## Design Choices

1. **JWT Authentication**: Chosen for secure, stateless authentication, simplifying the scalability of the API.
2. **PostgreSQL Full-Text Search**: Efficient search capability that improves speed and accuracy, especially with large datasets.
3. **Redis for Caching**: Helps reduce load on the database by caching frequently queried data, like user search results or friend lists.
4. **Rate Limiting**: Implemented to prevent abuse of the system, especially for friend request spamming.
5. **Role-Based Access Control (RBAC)**: Allows differentiated access to certain functionalities depending on user roles.

## Requirements

Ensure all dependencies are installed by running:

```sh
pip install -r requirements.txt
