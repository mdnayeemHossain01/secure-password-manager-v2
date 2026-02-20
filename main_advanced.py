import os
from getpass import getpass
from vault import Vault
from crypto import encrypt_password, decrypt_password
from main import derive_key # Importing the key derivation from teammate's main
from generator import generate_secure_password

# Initialize the exact same vault your teammate built
vault = Vault()

print("\n--- Advanced Password Manager v2 ---")
master_password = getpass('Enter your Master Password: ')

# Authentication Logic (Kept exactly the same)
if not vault.salt_exists():
    print("\nCreating new vault...")
    salt = os.urandom(16)
    vault.save_salt(salt)
    key = derive_key(master_password, salt)
    canary = encrypt_password("vault_is_verified!", key)
    vault.save_canary(canary)
    print('\nNew vault created.')
else:
    print("\nFetching your vault...")
    salt = vault.load_salt()
    key = derive_key(master_password, salt)
    canary = vault.get_canary()
    verification = decrypt_password(canary, key)
    
    if verification != 'vault_is_verified!':
        print("Access Denied: Incorrect password.")
        exit()
    print("Authentication Successful. Vault Loaded.")

# The Upgraded Application Loop
while True:
    print("\n--- Menu ---")
    print("1. Add existing password")
    print("2. Generate & save NEW password") # Our new feature!
    print("3. Get password")
    print("4. List services")
    print("5. Delete Service")
    print("6. Exit")

    choice = input("\nChoose an option: ")

    if choice == '1':
        service = input("Enter service name: ")
        password = getpass("Enter password: ")
        encrypted = encrypt_password(password, key)
        vault.save_password(service, encrypted)

    elif choice == '2':
        service = input("Enter service name for the new password: ")
        # Call our new generator
        new_password = generate_secure_password()
        print(f"\nGenerated Password: {new_password}")
        print("Encrypting and saving to vault...")
        
        encrypted = encrypt_password(new_password, key)
        vault.save_password(service, encrypted)

    elif choice == '3':
        service = input("Service: ")
        encrypted = vault.get_password(service)
        if encrypted:
            decrypted = decrypt_password(encrypted, key)
            if decrypted:
                print(f"Password for {service}: {decrypted}")
        else:
            print(f"No password found for {service}.")

    elif choice == '4':
        services = vault.list_services()
        if services:
            print("\nStored services:")
            for s in services:
                print(f" - {s}")
        else:
            print("No services stored.")

    elif choice == '5':
        service = input("Service to delete: ")
        if vault.delete_service(service):
            print(f"{service} was removed.")
        else:
            print(f"Service '{service}' not found.")

    elif choice == '6':
        print("Exiting Advanced Vault. Goodbye!")
        break
    else:
        print("Invalid option. Please try again.")
