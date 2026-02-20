import psycopg2

class Vault:
    def __init__(self, vault_file='vault.json'):
        # We ignore vault_file now, but keep it in the __init__ so main.py doesn't break!
        
        # ⚠️ IMPORTANT: Change 'YOUR_PASSWORD_HERE' to your actual PostgreSQL password 
        self.conn = psycopg2.connect(
            dbname="advanced_vault",
            user="postgres",
            password="YOUR_PASSWORD_HERE", 
            host="localhost"
        )
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """Automatically create the SQL tables if they don't exist yet."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS vault_config (
                id INTEGER PRIMARY KEY,
                salt TEXT,
                canary TEXT
            );
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS passwords (
                service TEXT PRIMARY KEY,
                encrypted_password TEXT
            );
        """)
        self.conn.commit()

    def salt_exists(self):
        self.cursor.execute("SELECT salt FROM vault_config WHERE id = 1;")
        result = self.cursor.fetchone()
        return result is not None and result[0] is not None

    def save_salt(self, salt):
        # ON CONFLICT allows us to update the salt if it already exists
        self.cursor.execute("""
            INSERT INTO vault_config (id, salt) VALUES (1, %s)
            ON CONFLICT (id) DO UPDATE SET salt = EXCLUDED.salt;
        """, (salt.hex(),))
        self.conn.commit()

    def load_salt(self):
        self.cursor.execute("SELECT salt FROM vault_config WHERE id = 1;")
        result = self.cursor.fetchone()
        return bytes.fromhex(result[0]) if result else None

    def save_password(self, service, encrypted_data):
        self.cursor.execute("""
            INSERT INTO passwords (service, encrypted_password) 
            VALUES (%s, %s)
            ON CONFLICT (service) DO UPDATE SET encrypted_password = EXCLUDED.encrypted_password;
        """, (service, encrypted_data.hex()))
        self.conn.commit()
        print(f"Password for {service} was saved successfully to the database")

    def get_password(self, service):
        self.cursor.execute("SELECT encrypted_password FROM passwords WHERE service = %s;", (service,))
        result = self.cursor.fetchone()
        return bytes.fromhex(result[0]) if result else None

    def list_services(self):
        self.cursor.execute("SELECT service FROM passwords;")
        results = self.cursor.fetchall()
        return [row[0] for row in results]

    def save_canary(self, encrypted_canary):
        self.cursor.execute("UPDATE vault_config SET canary = %s WHERE id = 1;", (encrypted_canary.hex(),))
        self.conn.commit()

    def get_canary(self):
        self.cursor.execute("SELECT canary FROM vault_config WHERE id = 1;")
        result = self.cursor.fetchone()
        return bytes.fromhex(result[0]) if result and result[0] else None

    def delete_service(self, service):
        self.cursor.execute("DELETE FROM passwords WHERE service = %s RETURNING service;", (service,))
        deleted = self.cursor.fetchone()
        self.conn.commit()
        return deleted is not None