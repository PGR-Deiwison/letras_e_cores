"""
Configurações do Sistema de Gestão Escolar
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# ===== CONFIGURAÇÕES DO BANCO DE DADOS =====
DATABASE_NAME = os.getenv('DATABASE_NAME', 'escola.db')
DATABASE_PATH = os.path.join(os.path.dirname(__file__), DATABASE_NAME)

# ===== CONFIGURAÇÕES DO FLASK =====
DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))

# ===== CONFIGURAÇÕES DE SEGURANÇA =====
SECRET_KEY = os.getenv('SECRET_KEY', 'CHANGE_THIS_IN_PRODUCTION_KEY_2026')

# Criptografia de senhas
PASSWORD_ALGORITHM = 'bcrypt'  # ✅ Mudado para bcrypt (seguro)

# CORS - Restrito a domínios específicos
CORS_ENABLED = True
CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5000').split(',')
CORS_ALLOW_CREDENTIALS = os.getenv('CORS_ALLOW_CREDENTIALS', 'true').lower() == 'true'

# ===== CONFIGURAÇÕES DE SESSÃO (JWT) =====
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'CHANGE_THIS_JWT_KEY_IN_PRODUCTION_2026')
JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 86400))  # 24 horas
SESSION_TIMEOUT = timedelta(hours=24)
SESSION_COOKIE_SECURE = os.getenv('FLASK_ENV', 'development') == 'production'  # True apenas em HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

# ===== CONFIGURAÇÕES DE ADMINISTRADOR =====
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@escola.com')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'Admin2026')

# ===== CONFIGURAÇÕES DE LOGGING =====
LOG_LEVEL = 'INFO'
LOG_FORMAT = '[%(asctime)s] %(levelname)s: %(message)s'
LOG_FILE = 'app.log'

# ===== CONFIGURAÇÕES DE VALIDAÇÃO =====
SENHA_MIN_LENGTH = 6
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

# ===== CONFIGURAÇÕES DE NEGÓCIO =====
BIMESTRES = [1, 2, 3, 4]
NOTA_MINIMA = 0
NOTA_MAXIMA = 10
FREQUENCIA_MINIMA_APROVACAO = 75  # Percentual

# ===== CONFIGURAÇÕES DE API =====
JSON_SORT_KEYS = False
JSONIFY_PRETTYPRINT_REGULAR = True
API_TIMEOUT = 30  # segundos

# ===== CONFIGURAÇÕES DE PERFORMANCE =====
DATABASE_CONNECTION_TIMEOUT = 5.0
CACHE_ENABLED = False
CACHE_TIMEOUT = 300  # segundos

# ===== MODO PRODUÇÃO =====
PRODUCTION = False  # Mude para True ao fazer deploy

if PRODUCTION:
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    CORS_ORIGINS = ['https://seu-dominio.com']  # Configure seu domínio
    # Outras configurações de produção

# ===== IMPRESSÃO DE CONFIGURAÇÕES =====
if __name__ == '__main__':
    print("Configurações do Sistema:")
    print(f"  Database: {DATABASE_PATH}")
    print(f"  Server: {HOST}:{PORT}")
    print(f"  Debug: {DEBUG}")
    print(f"  Production: {PRODUCTION}")
