FROM python:3.10-slim

# working directory
WORKDIR /app

# install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# copy only requirements first for caching
COPY requirements.txt .

# install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# copy the whole code
COPY . .

# expose streamlit port
EXPOSE 8501

# run the app
CMD ["streamlit", "run", "app/main.py"]
