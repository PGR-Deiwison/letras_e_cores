"""
Script para limpar todos os dados cadastrados (alunos, professores e admin)
"""

import sqlite3
import os

db_file = 'escola.db'

if os.path.exists(db_file):
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        print("\n🔍 Limpando banco de dados...\n")
        
        # Deletar dados das tabelas (mantém a estrutura)
        tabelas_a_limpar = [
            'professor_disciplina_serie',
            'professor_disciplina',
            'professor_serie',
            'notas',
            'frequencia',
            'alunos',
            'professores',
            'series',
            'disciplinas'
        ]
        
        for tabela in tabelas_a_limpar:
            try:
                cursor.execute(f"DELETE FROM {tabela}")
                print(f"  ✓ Tabela '{tabela}' limpa")
            except Exception as e:
                print(f"  ⚠️  Erro ao limpar '{tabela}': {e}")
        
        conn.commit()
        conn.close()
        
        print("\n✅ Banco de dados limpo com sucesso!")
        print("\nAgora o sistema está vazio. Você pode:")
        print("  1. Fazer login com admin@escola.com / Admin2026")
        print("  2. Cadastrar novos alunos e professores\n")
        
    except Exception as e:
        print(f"❌ Erro ao limpar banco de dados: {e}")
else:
    print(f"❌ Arquivo {db_file} não encontrado")
