#!/bin/bash


set SQLALCHEMY_DATABASE_URI=sqlite:///./test.db


echo "Starting the tests..."

pytest