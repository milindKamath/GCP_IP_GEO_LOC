FROM python:3.8-slim

WORKDIR Capstone

COPY ["requirements.txt", "ip_to_loc.py", "./"]

COPY ["/templates", "./templates"]

COPY ["/static", "./static"]


RUN python3 -m pip install -r /Capstone/requirements.txt
CMD ["python3", "ip_to_loc.py"]
