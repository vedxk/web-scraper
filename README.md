# web-scraper
This project is a web scraping tool designed to automate the process of scraping information from a specific webpage. It leverages Scrapy for the scraping process, incorporates middleware for retries, uses FastAPI and Uvicorn to provide an API interface, and utilizes Redis for caching results. The scraped data is stored locally in a JSON file.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)

## Features

- Scrapy: Efficient and flexible web scraping framework.
- Middleware: Custom retry logic to handle request failures.
- FastAPI: Modern web framework for building APIs.
- Uvicorn: Lightning-fast ASGI server for serving the FastAPI application.
- Redis: In-memory data structure store used for caching scraped results.
- Local Storage: Stores scraped data in a JSON file.
- User Inputs: Allows specifying start page, end page, and proxy as inputs.


## Installation

> **Note:**
> Make sure you have Python 3.8+ installed.

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/web-scraper.git
    cd web-scraper
    ```

2. Create a virtual environment:
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the required packages:
    ```sh
    pip3 install -r requirements.txt
    ```

## Configuration

1. Run Redis Server:
   - Make sure you have a Redis server running on localhost:6379.

2. Auth Token Config:
   - Update the Auth Token in the config.ini file.

## Usage

1. To start the server, use the following command:

  ```sh
  uvicorn main:app --host 127.0.0.1 --port 8000
  ```

2. Send a POST request to start the scraping process:

  ```sh
  curl -X POST "http://localhost:8000/scrape" -H "Authorization: your_token" -H "Content-Type: application/json" -d '{"start_page": 1, "end_page": 5, "proxy": "http://yourproxy:port"}'
  ```

3. There is a test script scraping_endpoint_test.py in the repo which can achieve the same.












