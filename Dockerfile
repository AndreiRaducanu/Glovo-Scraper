FROM python:3.11

WORKDIR /glovo

COPY requirements.txt ./

COPY requirements_dev.txt ./

COPY pyproject.toml ./

COPY setup.cfg ./ 

COPY setup.py ./ 

COPY tox.ini ./

COPY README.md ./

COPY LICENSE.txt ./

COPY src/glovo src/glovo

RUN pip install -e .

CMD ["python", "src/glovo/main.py"]
