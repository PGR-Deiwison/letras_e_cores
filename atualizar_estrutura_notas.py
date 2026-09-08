"""
Script para expandir a estrutura da tabela de notas
DEPRECATED - NÃO USE ESTE SCRIPT!

Este script está obsoleto. A migração correta das colunas de notas (avm, avb, rec, mb)
é feita automaticamente através de aplicar_migracoes() em banco_dados.py

As colunas adicionadas por este script estão INCORRETAS:
  - INCORRETO: nota_mensal_1, nota_mensal_2, nota_mensal_3, nota_bimestral, nota_recuperacao
  - CORRETO: avm, avb, rec, mb

NÃO EXECUTE ESTE SCRIPT!
"""

import sys

print("\n" + "="*80)
print("❌ ERRO: SCRIPT DEPRECATED")
print("="*80)
print("\nEste script não pode ser executado. A migração de notas já é feita")
print("automaticamente pelo sistema na inicialização do banco de dados.")
print("\nPara adicionar as colunas de notas corretamente, simplesmente:")
print("  1. Abra o python interativo")
print("  2. Execute: from banco_dados import BancoDados")
print("  3. Execute: db = BancoDados('escola.db')")
print("\nO sistema aplicará as migrações automaticamente.")
print("="*80 + "\n")

sys.exit(1)

# CÓDIGO ORIGINAL (NÃO EXECUTARÁ)
# ============================================

"""
ORIGINAL SCRIPT (NÃO EXECUTÁVEL):

import sqlite3

db_file = 'escola.db'

print("\n" + "="*80)
print("ATUALIZANDO ESTRUTURA DE NOTAS")
print("="*80 + "\n")

try:
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Verificar estrutura atual
    cursor.execute("PRAGMA table_info(notas)")
    colunas = {col[1] for col in cursor.fetchall()}
    
    print(f"Colunas existentes: {colunas}\n")
    
    # Adicionar colunas se não existirem
    novas_colunas = {
        'nota_mensal_1': 'REAL',
        'nota_mensal_2': 'REAL', 
        'nota_mensal_3': 'REAL',
        'nota_bimestral': 'REAL',
        'nota_recuperacao': 'REAL',
        'tipo_nota': "TEXT DEFAULT 'bimestral'"
    }
    
    for coluna, tipo in novas_colunas.items():
        if coluna not in colunas:
            try:
                cursor.execute(f"ALTER TABLE notas ADD COLUMN {coluna} {tipo}")
                print(f"✓ Coluna '{coluna}' adicionada")
            except Exception as e:
                print(f"⚠️  Erro ao adicionar '{coluna}': {e}")
        else:
            print(f"✓ Coluna '{coluna}' já existe")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*80)
    print("✅ ESTRUTURA ATUALIZADA COM SUCESSO!")
    print("="*80 + "\n")
"""
    print("Estrutura das notas agora suporta:")
    print("  • nota_mensal_1, nota_mensal_2, nota_mensal_3 (avaliações mensais)")
    print("  • nota_bimestral (nota final do bimestre)")
    print("  • nota_recuperacao (recuperação paralela)")
    print("  • tipo_nota (identifica o tipo de nota)")
    print()
    
except Exception as e:
    print(f"❌ Erro: {e}")
    sys.exit(1)
