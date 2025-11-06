import os
import datetime
from django.conf import settings
from config.connection.send_developer import send_private_message_developer
from config.settings.base import SITE_NAME

# def backup_database():
#     # Yedek dosyasının adını oluştur
#     backup_dir = "db_backup"  # Yedeklerin saklanacağı klasör
#     if not os.path.exists(backup_dir):
#         os.makedirs(backup_dir)  # Klasör yoksa oluşturulur
#     backup_file = f"{backup_dir}/backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
#     os.system(
#         f"pg_dump --dbname=postgresql://{settings.DATABASES['default']['USER']}:{settings.DATABASES['default']['PASSWORD']}@{settings.DATABASES['default']['HOST']}:{settings.DATABASES['default']['PORT']}/{settings.DATABASES['default']['NAME']} > {backup_file}")
#     send_private_message_developer(f'{SITE_NAME} db backup - {datetime.datetime.now()}')


import datetime
import subprocess
import os
from django.conf import settings

from services.handle_exception import handle_exception


# from myapp.utils import send_private_message_developer  # senin fonksiyonun

def backup_database():
    backup_dir = "db_backup"
    os.makedirs(backup_dir, exist_ok=True)

    backup_file = os.path.join(
        backup_dir,
        f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    )
    db = settings.DATABASES['default']
    command = [
        "/usr/bin/pg_dump",
        f"--dbname=postgresql://{db['USER']}:{db['PASSWORD']}@{db['HOST']}:{db['PORT']}/{db['NAME']}"
    ]
    try:
        # stdout=PIPE ve stderr=PIPE ile hatayı yakalayabiliyoruz
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True  # hata olursa otomatik Exception atar
        )
        # stdout'u (çıktıyı) dosyaya kaydet
        with open(backup_file, "w") as f:
            f.write(result.stdout)

        send_private_message_developer(
            f"✅ {settings.SITE_NAME} - DB backup başarıyla alındı: {backup_file}"
        )

    except subprocess.CalledProcessError as e:
        handle_exception(e)

    except Exception as e:
        handle_exception(e)
