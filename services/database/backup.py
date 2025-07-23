import os
import datetime
from django.conf import settings
from config.connection.send_developer import send_private_message_developer
from config.settings.base import SITE_NAME

def backup_database():
    # Yedek dosyasının adını oluştur
    backup_dir = "db_backup"  # Yedeklerin saklanacağı klasör
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)  # Klasör yoksa oluşturulur
    backup_file = f"{backup_dir}/backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    os.system(
        f"pg_dump --dbname=postgresql://{settings.DATABASES['default']['USER']}:{settings.DATABASES['default']['PASSWORD']}@{settings.DATABASES['default']['HOST']}:{settings.DATABASES['default']['PORT']}/{settings.DATABASES['default']['NAME']} > {backup_file}")
    send_private_message_developer(f'{SITE_NAME} db backup - {datetime.datetime.now()}')