"""
Script para inserir notas de teste com informações detalhadas
"""

import sqlite3
from datetime import datetime

db_file = 'escola.db'

print("\n" + "="*80)
print("INSERINDO NOTAS DE TESTE")
print("="*80 + "\n")

try:
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Verificar alunos existentes
    cursor.execute("SELECT id, nome FROM alunos LIMIT 3")
    alunos = cursor.fetchall()
    print(f"Alunos encontrados: {alunos}\n")
    
    # Verificar professores existentes
    cursor.execute("SELECT id, nome FROM professores LIMIT 3")
    professores = cursor.fetchall()
    print(f"Professores encontrados: {professores}\n")
    
    if alunos and professores:
        # Disciplinas de exemplo
        disciplinas = ['Matemática', 'Português', 'História', 'Ciências', 'Inglês']
        
        # Limpar notas anteriores
        aluno_id = alunos[0][0]
        professor_id = professores[0][0]
        
        cursor.execute("DELETE FROM notas WHERE aluno_id = ?", (aluno_id,))
        print(f"Notas anteriores do aluno {aluno_id} removidas\n")
        
        # Inserir notas para cada disciplina, para cada bimestre
        for bimestre in range(1, 5):
            print(f"Inserindo notas do {bimestre}º bimestre...")
            
            for disciplina in disciplinas:
                # Valores de exemplo realistas
                avm = 7.5 + (bimestre * 0.5)  # Nota mensal
                avb = 8.0 + (bimestre * 0.3)  # Nota bimestral
                rec = 6.5 if bimestre in [2, 3] else None  # Recuperação em alguns bimestres
                mb = (avm + avb) / 2 if not rec else (avm + avb + rec) / 3  # Média
                
                cursor.execute('''INSERT INTO notas 
                    (aluno_id, professor_id, disciplina, nota, bimestre, 
                     avm, avb, rec, mb, data_registro, observacao)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (aluno_id, professor_id, disciplina, mb, bimestre, 
                     avm, avb, rec, mb, datetime.now(), f'Observação de exemplo para {disciplina}'))
                
                print(f"  ✓ {disciplina}: AVM={avm:.1f}, AVB={avb:.1f}, REC={rec}, MB={mb:.1f}")
        
        conn.commit()
        conn.close()
        
        print("\n" + "="*80)
        print("✅ NOTAS DE TESTE INSERIDAS COM SUCESSO!")
        print("="*80 + "\n")
        print(f"Aluno: {alunos[0][1]} (ID: {aluno_id})")
        print(f"Professor: {professores[0][1]} (ID: {professor_id})")
        print("\nNotas inseridas:")
        print("  • 4 Bimestres")
        print("  • 5 Disciplinas por bimestre")
        print("  • Cada nota contém: AVM (mensal), AVB (bimestral), REC (recuperação), MB (média)")
        print()
        
    else:
        print("❌ Não há alunos ou professores na base de dados!")
        
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
