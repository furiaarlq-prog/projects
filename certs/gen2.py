import subprocess
import sys
import hashlib

def get_cert_hash(cert_path):
    """SHA256 hash of certificate in DER format"""
    # Convert PEM -> DER and calculate hash
    result = subprocess.run(
        ['openssl', 'x509', '-in', cert_path, '-outform', 'DER'],
        capture_output=True
    )
    if result.returncode != 0:
        print(f"Error converting cert: {result.stderr.decode()}")
        return None
    
    der_data = result.stdout
    hash_obj = hashlib.sha256(der_data)
    return hash_obj.digest()

def get_pubkey_hash(cert_path):
    """SHA256 hash of public key (SPKI)"""
    # Extract public key from certificate
    pubkey_result = subprocess.run(
        ['openssl', 'x509', '-in', cert_path, '-pubkey', '-noout'],
        capture_output=True
    )
    if pubkey_result.returncode != 0:
        print(f"Error extracting pubkey: {pubkey_result.stderr.decode()}")
        return None
    
    # PEM public key -> DER
    der_result = subprocess.run(
        ['openssl', 'pkey', '-pubin', '-outform', 'DER'],
        input=pubkey_result.stdout,
        capture_output=True
    )
    if der_result.returncode != 0:
        print(f"Error converting pubkey: {der_result.stderr.decode()}")
        return None
    
    hash_obj = hashlib.sha256(der_result.stdout)
    return hash_obj.digest()

def format_hash_cpp(hash_bytes, name):
    """Convert hash to C++ array format"""
    lines = []
    lines.append(f"constexpr unsigned char {name}[32] = {{")
    
    for i in range(0, 32, 8):
        chunk = hash_bytes[i:i+8]
        hex_values = ', '.join(f'0x{b:02X}' for b in chunk)
        if i + 8 < 32:
            lines.append(f"    {hex_values},")
        else:
            lines.append(f"    {hex_values}")
    
    lines.append("};")
    return '\n'.join(lines)

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_pin_hashes.py <certificate.crt>")
        print("\nExample:")
        print("  python generate_pin_hashes.py server.crt")
        sys.exit(1)
    
    cert_path = sys.argv[1]
    
    print("=" * 60)
    print("SSL PINNING HASH GENERATOR")
    print("=" * 60)
    print()
    
    # Certificate hash
    cert_hash = get_cert_hash(cert_path)
    if cert_hash:
        print("// Certificate Hash (Full cert DER -> SHA256)")
        print(format_hash_cpp(cert_hash, "PINNED_CERT_HASH"))
        print()
        print(f"// Hex: {cert_hash.hex()}")
        print()
    
    # Public key hash
    pubkey_hash = get_pubkey_hash(cert_path)
    if pubkey_hash:
        print("// Public Key Hash (SPKI DER -> SHA256)")
        print(format_hash_cpp(pubkey_hash, "PINNED_PUBKEY_HASH"))
        print()
        print(f"// Hex: {pubkey_hash.hex()}")
        print()
    
    print("=" * 60)
    print("Copy these values to the SSLPin namespace in ssl_pinning.hpp file.")
    print("=" * 60)

if __name__ == "__main__":
    main()