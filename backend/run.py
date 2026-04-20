"""run.py — Start the EmailGuard API server."""
import os
import uvicorn

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print("=" * 50)
    print("  EmailGuard API — Email Detection System")
    print("=" * 50)
    print(f"  Swagger UI: http://0.0.0.0:{port}/docs")
    print(f"  ReDoc:      http://0.0.0.0:{port}/redoc")
    print(f"  Health:     http://0.0.0.0:{port}/health")
    print("=" * 50)
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
