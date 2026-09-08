# API Reference & Endpoints

## Base URL
Production: `https://api.inovasitech.id/v1`
Staging: `https://api-staging.inovasitech.id/v1`

Semua request wajib menyertakan header:
`Content-Type: application/json`
`Authorization: Bearer <access_token>`

## 1. POST /auth/login
Melakukan otentikasi pengguna dan mengembalikan JWT Access Token.

### Request Body
```json
{
  "email": "user@example.com",
  "password": "SecretPassword123!"
}
```

### Response (200 OK)
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900,
    "user": {
      "id": "usr_99812",
      "name": "Ryan Agung",
      "role": "ORGANIZATION_ADMIN"
    }
  }
}
```

## 2. GET /users/me
Mengambil profil pengguna yang sedang login berdasarkan Bearer Token.

### Response (200 OK)
```json
{
  "status": "success",
  "data": {
    "id": "usr_99812",
    "email": "ryan@example.com",
    "is_active": true,
    "created_at": "2024-01-15T08:00:00Z"
  }
}
```

## 3. POST /payments/checkout
Membuat tagihan pembayaran baru.
Rate Limit: 20 request/menit per user.
