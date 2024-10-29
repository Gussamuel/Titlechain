from ecdsa import SigningKey, NIST384p

# Generate a new private key
private_key = SigningKey.generate(curve=NIST384p)

# Convert to hex and verify length
private_key_hex = private_key.to_string().hex()
print(f"Private Key: {private_key_hex}")
print(f"Length: {len(private_key_hex)} (Should be 96 characters)")