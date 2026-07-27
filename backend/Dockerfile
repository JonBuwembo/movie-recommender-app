FROM python:3.13

WORKDIR /app

# Copy dependencies file
COPY backend/requirements.txt .

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy source files
COPY backend /app/backend

ENV FLASK_APP=backend.app

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
