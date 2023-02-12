#!/bin/bash

echo "Make sure you are the correct venv..."

set SQLALCHEMY_DATABASE_URI=mysql://hbstudent:hbstudent@localhost/dev-portal

echo "Starting the server..."

uvicorn main:app  --reload --host 0.0.0.0 --port 8000

