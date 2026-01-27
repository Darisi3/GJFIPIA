# 1️⃣ Use Python 3.11
FROM python:3.11-slim

# 2️⃣ Set working directory
WORKDIR /app

# 3️⃣ Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4️⃣ Copy all project files
COPY . .

# 5️⃣ Expose port (5000 për Flask, ndrysho nëse duhet)
EXPOSE 5000

# 6️⃣ Start the app
CMD ["python", "run.py"]
