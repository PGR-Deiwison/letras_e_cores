#!/usr/bin/env python
"""
Script de inicialização do banco de dados para Render/Supabase
Execute este script após o deploy para criar as tabelas
"""

import os
import sys
from banco_dados import inicializar_banco

def main():
    print("=" * 60)
    print("🔧 INICIALIZADOR DE BANCO DE DADOS")
    print("=" * 60)
    print()
    
    # Verificar se existe DATABASE_URL
    database_url = os.environ.get("DATABASE_URL")
    
    if database_url:
        print("✓ DATABASE_URL detectada (Produção com PostgreSQL)")
        print(f"  Host: {database_url.split('@')[1].split(':')[0] if '@' in database_url else 'N/A'}")
    else:
        print("✓ DATABASE_URL não encontrada (Desenvolvimento com SQLite)")
    
    print()
    print("Inicializando banco de dados...")
    print()
    
    try:
        db = inicializar_banco()
        print()
        print("=" * 60)
        print("✅ BANCO DE DADOS INICIALIZADO COM SUCESSO!")
        print("=" * 60)
        print()
        
        # Mostrar tipo de banco de dados
        if db.usar_postgresql:
            print("📊 Base de dados: PostgreSQL (Supabase/Render)")
        else:
            print("📊 Base de dados: SQLite (Local)")
        
        print()
        print("Próximos passos:")
        print("1. Verificar se as tabelas foram criadas no Supabase Studio")
        print("2. Iniciar o aplicativo Flask: python app.py")
        print("3. Acessar http://localhost:5000 (local) ou seu domínio Render (produção)")
        
        return 0
        
    except Exception as e:
        print()
        print("=" * 60)
        print("❌ ERRO AO INICIALIZAR BANCO DE DADOS")
        print("=" * 60)
        print()
        print(f"Erro: {str(e)}")
        print()
        print("Possíveis causas:")
        print("1. DATABASE_URL inválida ou incorreta")
        print("2. Servidor PostgreSQL/Supabase indisponível")
        print("3. Permissões insuficientes")
        print()
        print("Para resolver:")
        print("- Verifique a DATABASE_URL no arquivo .env ou variáveis Render")
        print("- Verifique a conectividade com o servidor PostgreSQL")
        print("- Consulte DEPLOY_SUPABASE_RENDER.md para instruções")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())
