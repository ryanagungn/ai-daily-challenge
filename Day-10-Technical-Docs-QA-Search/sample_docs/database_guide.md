# Database Architecture & Migration Guide

## 1. Primary Database: PostgreSQL 16
Sistem menggunakan PostgreSQL 16 terkelola (Managed Database) dengan konfigurasi High Availability (HA) dan read-replicas.

### Connection Pooling
Aplikasi menggunakan **PgBouncer** di depan PostgreSQL dengan mode pooling `transaction`:
- `max_client_conn`: 1000 koneksi
- `default_pool_size`: 25 koneksi per service
- `pool_mode`: transaction
- Timeout idle connection: 60 detik

### Indexing Strategy
- Gunakan **B-Tree Index** untuk foreign keys dan kolom yang sering digunakan pada filter `WHERE id = ...` atau range `WHERE created_at >= ...`.
- Gunakan **GIN Index** dengan ekstensi `pg_trgm` untuk pencarian teks (full-text search) pada nama produk dan deskripsi pengguna.
- Gunakan **Partial Index** untuk kueri status tertentu, contoh:
  ```sql
  CREATE INDEX idx_orders_unprocessed ON orders (created_at) WHERE status = 'pending';
  ```

## 2. Database Migrations with Alembic
Seluruh perubahan skema tabel HARUS didokumentasikan melalui migrasi Alembic:
1. Buat revisi migrasi baru:
   ```bash
   alembic revision --autogenerate -m "add_phone_number_to_users"
   ```
2. Tinjau file migrasi yang dihasilkan di folder `migrations/versions/`.
3. Jalankan migrasi ke database:
   ```bash
   alembic upgrade head
   ```
4. Rollback satu langkah jika terjadi kegagalan:
   ```bash
   alembic downgrade -1
   ```
