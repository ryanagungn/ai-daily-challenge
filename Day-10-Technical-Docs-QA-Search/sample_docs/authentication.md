# Authentication & Security Protocol

## 1. JWT Token Specifications
Sistem menggunakan pola **Dual-Token Authentication** (Access Token + Refresh Token) dengan enkripsi asimetris RS256:
- **Access Token:**
  - Masa berlaku (TTL): 15 Menit.
  - Disimpan oleh klien di Memory (bukan LocalStorage untuk mencegah serangan XSS).
  - Berisi claims: `user_id`, `email`, `role`, dan `permissions`.
- **Refresh Token:**
  - Masa berlaku (TTL): 7 Hari.
  - Disimpan dalam **HTTP-Only, Secure, SameSite=Strict Cookie**.
  - Menerapkan **Refresh Token Rotation (RTR)**: Setiap kali refresh token digunakan, token lama langsung di-revoke dan diganti dengan token baru.

## 2. Role-Based Access Control (RBAC)
Terdapat 3 level hak akses dalam sistem:
1. `SUPER_ADMIN`: Akses penuh ke seluruh resource, tenant management, dan audit logs.
2. `ORGANIZATION_ADMIN`: Mengelola anggota tim, konfigurasi billing, dan webhook integration.
3. `MEMBER`: Akses baca-tulis standar terhadap project dan dokumen miliknya sendiri.
4. `VIEWER`: Akses hanya baca (read-only) tanpa izin modifikasi atau penghapusan data.

## 3. Password Hashing & Security Policies
- Semua kata sandi di-hash menggunakan algoritma **Argon2id** (memory cost: 64MB, time cost: 3 iterations).
- Proteksi Brute Force: Akun akan terkunci sementara selama 30 menit jika gagal login 5 kali berturut-turut.
