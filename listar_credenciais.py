"""
Script para listar credenciais de alunos, professores e administradores
"""

from banco_dados import BancoDados
import json

db = BancoDados('escola.db')

print("\n" + "="*80)
print("CREDENCIAIS CADASTRADAS NO SISTEMA")
print("="*80 + "\n")

# Listar Professores
print("👨‍🏫 PROFESSORES:")
print("-" * 80)
try:
    professores = db.listar_professores()
    if professores:
        for prof in professores:
            print(f"  Nome: {prof[1]}")
            print(f"  Email: {prof[2]}")
            print(f"  Telefone: {prof[4]}")
            print(f"  Endereço: {prof[5]}")
            print()
    else:
        print("  ❌ Nenhum professor cadastrado")
except Exception as e:
    print(f"  ❌ Erro ao listar professores: {e}")

print("\n")

# Listar Alunos
print("👨‍🎓 ALUNOS:")
print("-" * 80)
try:
    alunos = db.listar_alunos()
    if alunos:
        for aluno in alunos:
            print(f"  Nome: {aluno[1]}")
            print(f"  Email: {aluno[2]}")
            print(f"  CPF: {aluno[3]}")
            print(f"  Matrícula: {aluno[4]}")
            print(f"  Responsável: {aluno[7]}")
            print(f"  Telefone Responsável: {aluno[8]}")
            print()
    else:
        print("  ❌ Nenhum aluno cadastrado")
except Exception as e:
    print(f"  ❌ Erro ao listar alunos: {e}")

print("\n")

# Listar Administradores
print("🔐 ADMINISTRADORES:")
print("-" * 80)
print("  Email: admin@escola.com")
print("  Senha: Admin2026")
print()

print("\n" + "="*80)
print("OBSERVAÇÃO: Senhas são armazenadas com hash bcrypt (não visíveis para alunos/professores)")
print("="*80 + "\n")
