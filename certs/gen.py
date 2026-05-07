

import sys
import subprocess
import os

def convert_to_der(input_file, output_file, file_type):
    """Converts PEM file to DER format"""
    if file_type == "cert":
        cmd = ['openssl', 'x509', '-in', input_file, '-outform', 'DER', '-out', output_file]
    else:  # key
        cmd = ['openssl', 'rsa', '-in', input_file, '-outform', 'DER', '-out', output_file]
    
    result = subprocess.run(cmd, capture_output=True)
    return result.returncode == 0

def to_cpp_array(data, varname):
    """Converts binary data to C++ array format"""
    lines = [f'constexpr unsigned char {varname}[] = {{']
    
    for i in range(0, len(data), 16):
        chunk = data[i:i+16]
        hex_vals = ', '.join(f'0x{b:02X}' for b in chunk)
        if i + 16 < len(data):
            lines.append(f'    {hex_vals},')
        else:
            lines.append(f'    {hex_vals}')
    
    lines.append('};')
    lines.append(f'constexpr size_t {varname}_SIZE = {len(data)};')
    return '\n'.join(lines)

def main():
    if len(sys.argv) < 3:
        print("Usage: python generate_client_cert_header.py <client.crt> <client.key>")
        print("")
        print("Example:")
        print("  python generate_client_cert_header.py certs/client.crt certs/client.key")
        print("")
        print("Output: client_cert_embedded.h")
        sys.exit(1)
    
    cert_file = sys.argv[1]
    key_file = sys.argv[2]
    output_file = "client_cert_embedded.h"
    
    # Check if files exist
    if not os.path.exists(cert_file):
        print(f"ERROR: {cert_file} not found!")
        sys.exit(1)
    
    if not os.path.exists(key_file):
        print(f"ERROR: {key_file} not found!")
        sys.exit(1)
    
    print("=" * 60)
    print("CLIENT CERTIFICATE HEADER GENERATOR")
    print("=" * 60)
    print()
    
    # Temporary DER files
    cert_der = "temp_client.der"
    key_der = "temp_client_key.der"
    
    try:
        # PEM -> DER conversion
        print("[1/4] Converting certificate to DER...")
        if not convert_to_der(cert_file, cert_der, "cert"):
            print("ERROR: Certificate conversion failed!")
            sys.exit(1)
        print("      ✓ Certificate ready")
        
        print("[2/4] Converting private key to DER...")
        if not convert_to_der(key_file, key_der, "key"):
            print("ERROR: Private key conversion failed!")
            sys.exit(1)
        print("      ✓ Private key ready")
        
        # Read DER files
        print("[3/4] Reading binary data...")
        with open(cert_der, 'rb') as f:
            cert_data = f.read()
        
        with open(key_der, 'rb') as f:
            key_data = f.read()
        print(f"      ✓ Cert: {len(cert_data)} bytes, Key: {len(key_data)} bytes")
        
        # Create header file
        print(f"[4/4] Creating {output_file}...")
        
        header_content = f'''// client_cert_embedded.h
#pragma once

{to_cpp_array(cert_data, 'CLIENT_CERT')}

{to_cpp_array(key_data, 'CLIENT_KEY')}
'''
        
        with open(output_file, 'w') as f:
            f.write(header_content)
        
        print(f"      ✓ {output_file} created")
        
    finally:
        # Clean up temporary files
        if os.path.exists(cert_der):
            os.remove(cert_der)
        if os.path.exists(key_der):
            os.remove(key_der)
    
    print()
    print("=" * 60)
    print("COMPLETED!")
    print("=" * 60)
    print()
    print(f"Çıktı dosyası: {output_file}")
    print()
    print()

if __name__ == "__main__":
    main()