import secrets

# Generate a 32-byte (256-bit) secret key
secret_key = secrets.token_hex(128)

# Print the secret key
print(secret_key)
