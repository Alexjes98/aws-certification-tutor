FROM public.ecr.aws/lambda/python:3.10

# Install system dependencies required for PyMuPDF
RUN yum install -y \
    gcc \
    gcc-c++ \
    make \
    zlib-devel \
    freetype-devel \
    python3-devel \
    mupdf-devel

COPY requirements.txt ./

RUN python3.10 -m pip install -r requirements.txt -t .

COPY index.py ./

# Command can be overwritten by providing a different command in the template directly.
CMD ["index.lambda_handler"]