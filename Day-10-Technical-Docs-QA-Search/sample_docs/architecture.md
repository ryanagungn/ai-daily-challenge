# System Architecture & Technical Design

## 1. High-Level Architecture Overview
Sistem backend dirancang menggunakan arsitektur microservices modular berbasis FastAPI dan Go.
Seluruh permintaan dari klien (Web SPA dan Mobile App) diarahkan melalui **Kong API Gateway** sebelum mencapai layanan internal.

Komponen Utama:
- **API Gateway (Kong):** Bertanggung jawab atas SSL termination, rate limiting (maksimal 100 req/min per IP), dan central routing.
- **Auth Service:** Menangani otentikasi OAuth2, issuance token JWT, dan verifikasi Role-Based Access Control (RBAC).
- **Order & Payment Service:** Mengelola transaksi, integrasi payment gateway (Midtrans & Stripe), dan webhook rekonsiliasi.
- **Notification Worker:** Background worker asynchronous yang memproses email, push notification, dan SMS via RabbitMQ message broker.

## 2. Caching & Message Queue
- **Redis Cluster:** Digunakan untuk distributed session storage, token blacklist cache, dan caching kueri baca dengan TTL 15 menit.
- **RabbitMQ:** Digunakan untuk event-driven messaging antar service dengan retry policy exponential backoff (maksimal 5 kali percobaan).

## 3. Observability & Monitoring
- **Prometheus & Grafana:** Mengumpulkan metrik sistem (CPU, RAM, HTTP request latency, error rate 5xx).
- **OpenTelemetry & Jaeger:** Distributed tracing untuk melacak alur request antar microservice dengan trace ID terpadu.
- **Sentry:** Error tracking real-time untuk menangkap unhandled exception di level aplikasi.
