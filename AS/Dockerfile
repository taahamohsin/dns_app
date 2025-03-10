# Name: Taaha Bin Mohsin

FROM python:3.9-slim
WORKDIR /app
COPY app.py .
COPY dns_records.txt .
RUN chmod +x /app/app.py
ENV PYTHONUNBUFFERED=1
EXPOSE 53533
CMD ["python", "-u", "app.py"]
