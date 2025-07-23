import requests
import json

from config.connection.send_developer import send_private_message_developer
from store.models import Product
from user.models import User, Districts, Regions
from django.http import JsonResponse


MyToken = "as2213dA2Dwwww21kwo12oasaaaaa123aaaaaaaaaadWALKSAMD.KA2KSMaslkdalsjdlkasdA123LDKMAaskdalskdasdas12dasdd213lasdlkasmldsadasdas"
HEADER = {'Content-type': 'application/json',
          "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36",
          'Accept': 'application/json', 'MyToken': MyToken}


