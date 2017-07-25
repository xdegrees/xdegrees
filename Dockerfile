FROM python:3.5

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 1792

CMD python -m xdegrees.app --port=1792 --search_url=${SEARCH_URL} --search_timeout_seconds=${SEARCH_TIMEOUT_SECONDS}