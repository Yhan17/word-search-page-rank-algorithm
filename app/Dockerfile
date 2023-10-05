FROM python:latest
WORKDIR /app
COPY ./ .

RUN pip3 install -r requirements.txt
RUN apt-get update

EXPOSE 80
EXPOSE 8080
EXPOSE 8000
EXPOSE 8002

# CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8002","--reload"]
CMD ["uvicorn", "main:app", "--reload", "--workers", "1", "--host", "0.0.0.0", "--port", "8002"]
