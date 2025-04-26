FROM python:3.9-slim
LABEL authors="marcello"

WORKDIR /src
COPY requirements.txt requirements.txt

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Create a user without administrative privileges and set the appropriate permissions for the /src directory
RUN useradd -m appuser && chown -R appuser:appuser /src
# Copy the script to the working directory
COPY . .
RUN rm Dockerfile
#RUN apt-get update && apt-get install -y dnsutils libnss3
# Set the user
USER appuser
EXPOSE 32025
# Run the Python script at container startup
CMD [ "python", "app.py" ]
#CMD ["tail", "-f", "/dev/null"]
