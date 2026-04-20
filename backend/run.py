"""run.py — Start the EmailGuard API server."""
import uvicorn

if __name__ == "__main__":
    print("=" * 50)
    print("  EmailGuard API — Email Detection System")
    print("=" * 50)
    print("  Swagger UI: http://localhost:8000/docs")
    print("  ReDoc:      http://localhost:8000/redoc")
    print("  Health:     http://localhost:8000/health")
    print("=" * 50)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
