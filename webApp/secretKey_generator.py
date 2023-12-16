import os

def generate_secret_key(length=24):
   
    return os.urandom(length).hex()

if __name__ == "__main__":
    key = generate_secret_key()
    print("Generated Secret Key:")
    print(key)
