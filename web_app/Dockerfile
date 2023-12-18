FROM python:3.8-slim
WORKDIR /web_app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
EXPOSE 5001
CMD [ "python3", "-m" , "flask", "run"]