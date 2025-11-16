# The base image for python. There are countless official images.
# Alpine just sounded cool.
#
FROM python:3.11-alpine

# The directory in the container where the app will run.
#
WORKDIR /app

# Copy the requirements.txt file from the project directory into the working
# directory and install the requirements.
#
COPY ./requirements.txt /app
RUN pip install -r requirements.txt

# Copy over the files.
#
COPY . .

EXPOSE 8080

# Cloud SQL (YHL for test)
# ENV DATABASE_URL=mysql+pymysql://root:yl5763@35.188.28.63:3306/donor_registry

# Run the app.
CMD ["python", "main.py"]