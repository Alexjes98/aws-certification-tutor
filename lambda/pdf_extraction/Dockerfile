FROM --platform=linux/amd64 public.ecr.aws/lambda/python:3.10

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy function code
COPY index.py ${LAMBDA_TASK_ROOT}

# Set the CMD to your handler
CMD [ "index.lambda_handler" ] 