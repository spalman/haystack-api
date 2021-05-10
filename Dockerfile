FROM python:3.7.4-stretch

WORKDIR /home/user/rest_api

RUN apt-get update && apt-get install -y curl git pkg-config cmake

# Install PDF converter
RUN wget --no-check-certificate https://dl.xpdfreader.com/xpdf-tools-linux-4.03.tar.gz && \
    tar -xvf xpdf-tools-linux-4.03.tar.gz && cp xpdf-tools-linux-4.03/bin64/pdftotext /usr/local/bin

# copy code
ADD controller /home/user/rest_api/controller
COPY application.py /home/user/rest_api
COPY deploy.py /home/user/rest_api
COPY config.py /home/user/rest_api

# install as a package
RUN pip install git+https://github.com/spalman/haystack.git
RUN pip install gdown loguru


EXPOSE 8000

# cmd for running the API
CMD ["python3","deploy.py"]
