ARG PYTHON_IMAGE
ARG PYTHON_IMAGE_VERSION

FROM ${PYTHON_IMAGE}:${PYTHON_IMAGE_VERSION}

WORKDIR /opt/gon

COPY gon gon/
COPY tests/ tests/
COPY README.md .
COPY requirements.txt .
COPY requirements-tests.txt .
COPY setup.py .
COPY setup.cfg .

RUN pip install -r requirements.txt .
RUN pip install -r requirements-tests.txt .
