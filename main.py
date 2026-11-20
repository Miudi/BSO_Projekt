from datetime import datetime
from scripts.files_generator import TestDataGenerator
from scripts.create_database import DatabaseManager
from scripts.file_crypto import FileCrypto

# 1. Generowanie danych testowych
generator = TestDataGenerator(num_files=300, max_total_mb=150, output_dir="test_data")
generator.generate()

# 2. Pakowanie z użyciem drzewa Merkle (nazwa z timestampem w DB_DIR)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
db_filename = f"database_{timestamp}.zip"
key_filename = f"{timestamp}.key"

db = DatabaseManager()
db_path = db.pack("test_data", db_filename)

# 3. Szyfrowanie archiwum bazy -> utworzy databases/database_<timestamp>.zip.enc
crypto = FileCrypto()
crypto = FileCrypto(key_path=key_filename)
crypto.encrypt_file(db_path.name)