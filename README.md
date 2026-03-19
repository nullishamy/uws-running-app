# RunCalc Pro 🏃

A FastAPI-powered running analytics app with pace calculator, race predictor, HR training zones, split planner, and VO₂ max estimator.

---

## Run Locally

**Requirements:** Python 3.10+

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn main:app --host 0.0.0.0 --port 80
```

Open your browser at [http://localhost](http://localhost)

> **Note:** Port 80 may require elevated privileges on Linux/macOS. Either run with `sudo`, or use a higher port like `--port 8000` and visit `http://localhost:8000`.

---

## Run with Docker

**Requirements:** Docker

```bash
# Build the image
docker build -t runcalc-pro .

# Run the container on port 80
docker run -p 80:80 runcalc-pro
```

Open your browser at [http://localhost](http://localhost)

To run in the background (detached):

```bash
docker run -d -p 80:80 --name runcalc runcalc-pro
```

To stop it:

```bash
docker stop runcalc
```

---

## Project Structure

```
running-app/
├── main.py            # FastAPI app & API routes
├── requirements.txt   # Python dependencies
├── Dockerfile         # Container definition
└── templates/
    └── index.html     # Frontend UI
```
