import os
import subprocess
from django.conf import settings

def restore_database(backup_file):
    db_user = settings.DATABASES['default']['USER']
    db_password = settings.DATABASES['default']['PASSWORD']
    db_host = settings.DATABASES['default']['HOST']
    db_port = settings.DATABASES['default']['PORT']
    # db_name = settings.DATABASES['default']['NAME']
    db_name = 'test'
    env = os.environ.copy()
    env['PGPASSWORD'] = db_password

    restore_command = [
        "psql",
        f"postgresql://{db_user}@{db_host}:{db_port}/{db_name}",
        "-f",
        backup_file
    ]

    result = subprocess.run(restore_command, env=env, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"Veritabanı başarıyla geri yüklendi: {backup_file}")
        return True
    else:
        print(f"Geri yükleme sırasında bir hata oluştu: {result.stderr}")
        return False
