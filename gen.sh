#!/bin/bash

CERT_DIR="certs"
DAYS=365
COUNTRY="USA"
ORG="Random"
SERVER_CN="65.109.13.211" #random

mkdir -p $CERT_DIR
cd $CERT_DIR

echo ""
echo "[1/4] Creating CA..."

openssl genrsa -out ca.key 4096

openssl req -new -x509 -days $DAYS -key ca.key -out ca.crt \
    -subj "/C=$COUNTRY/O=$ORG/CN=$ORG CA"

echo "      ✓ ca.key and ca.crt created"

echo ""
echo "[2/4] Creating server cert..."

openssl genrsa -out server.key 4096

openssl req -new -key server.key -out server.csr \
    -subj "/C=$COUNTRY/O=$ORG/CN=$SERVER_CN"

openssl x509 -req -days $DAYS -in server.csr -CA ca.crt -CAkey ca.key \
    -CAcreateserial -out server.crt

rm server.csr
echo "      ✓ server.key and server.crt created"

echo ""
echo "[3/4] Creating client cert..."

openssl genrsa -out client.key 4096

openssl req -new -key client.key -out client.csr \
    -subj "/C=$COUNTRY/O=$ORG/CN=ProxyClient"

openssl x509 -req -days $DAYS -in client.csr -CA ca.crt -CAkey ca.key \
    -CAcreateserial -out client.crt

rm client.csr
echo "      ✓ client.key and client.crt created"


echo ""
echo "[4/4] Creating c++ headers for cert..."

SERVER_HASH=$(openssl x509 -in server.crt -outform DER | openssl sha256 -binary | xxd -p | tr -d '\n')
echo "      Server Cert Hash: $SERVER_HASH"

openssl x509 -in client.crt -outform DER -out client.der
openssl rsa -in client.key -outform DER -out client_key.der 2>/dev/null

echo "      ✓ client.der and client_key.der created"

# ============================================================
# Summary
# ============================================================
echo ""
echo "============================================================"
echo "Done!"
echo "============================================================"
echo ""
echo "Files:"
echo "  $CERT_DIR/ca.crt         - CA cert (leave it in server)"
echo "  $CERT_DIR/server.key     - Server private key"  
echo "  $CERT_DIR/server.crt     - Server cert"
echo "  $CERT_DIR/client.key     - Client private key (Embed to C++)"
echo "  $CERT_DIR/client.crt     - Client cert (Embed to C++)"
echo "  $CERT_DIR/client.der     - Client cert (DER format)"
echo "  $CERT_DIR/client_key.der - Client key (DER format)"
echo ""
echo "Next Steps:"
echo "  1. run index.ts"
echo "  2. embed the client.crt and client.key to C++"
echo ""

cd ..