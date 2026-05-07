# SV - Secure HTTPS Server

An Express-based HTTPS server with mutual TLS (mTLS) authentication and request forwarding.

## Installation

```bash
bun install
```

## Setup

### 1. Generate SSL Certificates

Run the certificate generation script from the root directory:

```bash
bash gen.sh
```

This will generate all required SSL certificates in the `certs/` directory:
- CA certificate and key (`ca.crt`, `ca.key`)
- Server certificate and key (`server.crt`, `server.key`)
- Client certificate and key (`client.crt`, `client.key`)
- DER format files for C++ embedding (`client.der`, `client_key.der`)

### 2. Configure Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
TARGET_SV=http://0.0.0.0:3000
TARGET_HEADER=your-target-auth-key
CLIENT_AUTH_HEADER=your-client-auth-key
```

- `TARGET_SV`: The target backend server URL where requests will be forwarded
- `TARGET_HEADER`: Authorization header key for the target server
- `CLIENT_AUTH_HEADER`: Authorization header key that clients must provide

## Usage

### Development

```bash
bun index.ts
```

The server will start on port 443 (HTTPS) with mutual TLS authentication enabled.

### Production

To allow the server to bind to port 443 without root privileges:

```bash
npm run permission
npm start
```

## How It Works

1. Server listens on HTTPS port 443 with mutual TLS enabled
2. Client must provide the `CLIENT_AUTH_HEADER` in their request
3. Valid requests are forwarded to `TARGET_SV` with the `TARGET_HEADER` added
4. Invalid requests are redirected to a default URL

## TLS Configuration

- Minimum TLS version: 1.2
- Supported ciphers:
  - ECDHE-RSA-AES256-GCM-SHA384
  - ECDHE-RSA-AES128-GCM-SHA256
- Client certificate verification: Required
