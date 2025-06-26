# App Service

This service provides the user interface and API gateway for the sentiment prediction application. It renders an HTML form, forwards review inputs to the model-service for analysis, and exposes application metadata and monitoring metrics. The API is documented using Swagger (OpenAPI), accessible through a web interface.

---

## Features

- **HTML form** for submitting reviews (`/`)
- **Sentiment prediction API** (`/predict`) that proxies to the model-service
- **Application and model version info endpoints** (`/version`, `/model-version`)
- **Prometheus-compatible monitoring metrics** (`/metrics`)
- **Interactive Swagger documentation** (`/apidocs/`)

---

## 🔍 API Docs (Swagger UI)

After starting the service, visit:

```
http://localhost:5001/apidocs/
```

Here you can explore and test all available endpoints interactively.

---

## API Key Authentication

To communicate with the model-service securely, this app includes an `X-API-Key` header in all outbound requests. The key is loaded from a secret file, depending on the environment:

- **Docker Compose:** `/run/secrets/model_credentials`
- **Kubernetes:** `/app/secrets/model_credentials`

If no valid secret is found, requests to the model-service may fail with a 401 error.

---

## Configuration

The app uses a `.env` file for environment-based configuration. Key variables include:

```env
MODEL_SERVICE_URL=http://localhost:5003
PORT=5001
APP_VERSION=0.1.0
```

- `MODEL_SERVICE_URL`: Location of the model-service API  
- `PORT`: Port to run the app-service on  
- `APP_VERSION`: Version string displayed in the UI and `/version` endpoint

---

## Running Locally (Standalone)

You can run this service without Docker for local development:

1. Make sure **Python 3.11+** is installed.
2. Create and activate a virtual environment (optional but recommended).
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the app:

   ```bash
   python run.py
   ```

Visit:

```
http://localhost:5001/apidocs/
```

to access the Swagger UI and interact with the endpoints.

---

## Monitoring

Expose Prometheus metrics at:

```
http://localhost:5001/metrics
```

Metrics include:

- Total request count
- Length of the most recent review
- Histogram of response time


