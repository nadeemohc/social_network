# Social Network API

Welcome to the **Social Network API** project! This repository contains the backend API for a social networking application built using Django and Django REST Framework. It includes various features like user authentication, friend request management, and user search functionality.

## Table of Contents

- [Project Description](#project-description)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
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
- Virtual environment (optional but recommended)

### Setup

1. Clone the repository:

    ```sh
    git clone https://github.com/yourusername/social-network-api.git
    cd social-network-api
    ```

2. Create and activate a virtual environment:

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

## Usage

### Postman Collection

A Postman collection is provided to facilitate testing of API endpoints. You can find the collection in the repository at:
[Postman Collection](./postman-collection.json).

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
