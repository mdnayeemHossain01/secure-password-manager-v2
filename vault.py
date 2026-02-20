
import json
import os
from pathlib import Path

class Vault:
    def __init__(self, vault_file='vault.json'):
        self.vault_file = vault_file

    def _read_data(self):
        '''helper to read data from file'''
        if not Path(self.vault_file).exists():
            return {}
        with open(self.vault_file, 'r') as f:
            return json.load(f)
    
    def _write_data(self, data):
        '''helper to write data to file'''
        with open(self.vault_file, 'w') as f:
            json.dump(data, f, indent=2)

    def salt_exists(self):
        '''Check if Salt Exists'''
        data = self._read_data()
        return data.get('salt') is not None
        
    def save_salt(self, salt):
        '''Save salt to Vault'''
        data = self._read_data()
        data['salt'] = salt.hex()
        self._write_data(data)
    
    def load_salt(self):
        '''Load salt from vault'''
        data = self._read_data()
        return bytes.fromhex(data['salt'])
    
    def save_password(self, service, encrypted_data):
        '''Save encrypted password'''
        data = self._read_data()

        if 'passwords' not in data:
            data['passwords'] = {}
        
        data['passwords'][service] = encrypted_data.hex()
        self._write_data(data)

        print(f"Password for {service} was saved successfully")

    def get_password(self, service):
        '''Retreive encrypted password'''
        data = self._read_data()
        if 'passwords' not in data or service not in data['passwords']:
            return None
        return bytes.fromhex(data['passwords'][service])
    
    def list_services(self):
        ''''get all services'''
        data = self._read_data()
        return list(data.get('passwords', {}).keys())
    
    def save_canary(self, encrypted_canary):
        data = self._read_data()
        data['canary'] = encrypted_canary.hex()
        self._write_data(data)
    
    def get_canary(self):
        data = self._read_data()
        canary_hex = data.get('canary')
        return bytes.fromhex(canary_hex) if canary_hex else None

    def delete_service(self, service):
        """delete a service"""
        data = self._read_data()
        if 'passwords' not in data or service not in data['passwords']:
            return False
        
        del data['passwords'][service]
        self._write_data(data)
        return True
