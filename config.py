import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
UDEMY_CLIENT_ID = os.getenv('UDEMY_CLIENT_ID')
UDEMY_CLIENT_SECRET = os.getenv('UDEMY_CLIENT_SECRET')

# API Configuration
UDEMY_API_CONFIG = {
    'client_id': UDEMY_CLIENT_ID,
    'client_secret': UDEMY_CLIENT_SECRET,
    'base_url': 'https://www.udemy.com/api-2.0',
    'auth_url': 'https://www.udemy.com/api-2.0/oauth2/token/'
}

# Other API configurations can be added here
COURSERA_API_CONFIG = {
    'base_url': 'https://api.coursera.org/api/courses.v1'
}

EDX_API_CONFIG = {
    'base_url': 'https://api.edx.org/catalog/v1/catalogs/'
}

KHAN_ACADEMY_API_CONFIG = {
    'base_url': 'https://www.khanacademy.org/api/v1'
} 