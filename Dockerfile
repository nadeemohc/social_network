# Step 1: Use the official Python image
FROM python:3.11-slim

# Step 2: Set the working directory in the container
WORKDIR /app

# Step 3: Copy the requirements file into the container
COPY requirements.txt .

# Step 4: Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5: Copy the current directory contents into the container at /app
COPY . .

# Step 6: Expose the port on which the Django app will run
EXPOSE 8000

# Step 7: Run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
