import hashlib
import os
from getpass import getpass
from vault import Vault
from crypto import encrypt_password, decrypt_password

def derive_key(master_password, salt):
    """Derive encryption key from master password and salt"""
    #using scrypt KDF derive keyBi
    return hashlib.scrypt(
        password=master_password.encode(),
        salt=salt,
        n=2**14,
        r=8,
        p=1,
        dklen=32
    )

#initalize vault
vault = Vault()

#get Master Password
master_password = getpass('Enter your password...')

#check for vault
if not vault.salt_exists():
    print("\nCreating new vault...")
    #if no vault, generate salt
    salt = os.urandom(16) #16 bytes
    vault.save_salt(salt)
    
    key = derive_key(master_password, salt)
    
    #create canary value
    canary = encrypt_password("vault_is_verified!", key)
    vault.save_canary(canary)

    print('\nNew vault created')
else:
    print("\nFetching your vault...")
    salt = vault.load_salt()
    key = derive_key(master_password, salt)

    #Check key validity
    canary = vault.get_canary()
    verification = decrypt_password(canary, key)
    if (verification != 'vault_is_verified!'):
        print("Incorrect password")
        exit()
    
    print("\nVault Loaded")

while True:
    print("\n--- Password Manager ---")
    print("1. Add password")
    print("2. Get password")
    print("3. List services")
    print("4. Delete Service")
    print("5. Exit")

    choice = input("\nChoose an option: ")

    if choice == '1': #add password
        service = input("Enter service name: ")
        password = getpass("Enter password: ")

        encrypted = encrypt_password(password, key)
        vault.save_password(service, encrypted)

    elif choice == '2': #get password
        service = input("Service: ")
        encrypted = vault.get_password(service)
        
        if encrypted:
            decrypted = decrypt_password(encrypted, key)
            if decrypted:
                print(f"{service} password: {decrypted}")
        else:
            print(f"No password found for {service}")
    
    elif choice == '3': #List servieces
        services = vault.list_services()
        if services:
            print("\nStored services")
            for s in services:
                print(f" - {s}")
        else:
            print("No services stored")
    
    elif choice == '5': #exit
        print("BYE")
        break
    elif choice == '4': #delete service
        service = input("Service: ")
        vault.delete_service(service)
        print(f"{service} was removed")

    else:
        print(f"{choice} is an invalid option")
        
