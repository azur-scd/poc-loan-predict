
# syntax=docker/dockerfile:1
FROM python:3.10.1-slim-buster
WORKDIR /app
RUN pip install --upgrade pip
RUN pip install pandas plotly streamlit
COPY . .
EXPOSE 8051
CMD streamlit run app.py --server.port 8051