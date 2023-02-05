FROM python:3.10.9-slim-buster as base

WORKDIR /run

COPY main.py requirements.txt .
