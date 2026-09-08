# Deployment & Kubernetes Infrastructure

## 1. Containerization (Dockerfile)
Aplikasi dikemas menggunakan multi-stage build untuk menghasilkan image yang ramping dan aman:

```dockerfile
# Build Stage
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final Runtime Stage
FROM python:3.12-slim
WORKDIR /app
RUN useradd -m -u 1001 appuser
COPY --from=builder /root/.local /home/appuser/.local
COPY . .
USER appuser
ENV PATH="/home/appuser/.local/bin:$PATH"
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

## 2. Health Check Probes
Kubernetes Deployment wajib menyertakan Liveness dan Readiness Probes:
- **Liveness Probe:** `GET /healthz` (timeout: 2s, period: 10s) — Me-restart pod jika service hang.
- **Readiness Probe:** `GET /readyz` (timeout: 2s, period: 5s) — Memastikan koneksi database dan Redis aktif sebelum menerima traffic.

## 3. Environment Secrets Management
DILARANG menyimpan secrets di ConfigMap atau Dockerfile.
Semua credentials (DATABASE_URL, GEMINI_API_KEY, JWT_SECRET) harus disuntikkan via **Kubernetes Secret** atau **HashiCorp Vault / External Secrets Operator**.
