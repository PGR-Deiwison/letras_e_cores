"""
Script de Inicialização Rápida - Sistema de Gestão Escolar
Execute este arquivo para configurar e testar o sistema completo
"""

import subprocess
import sys
import os
from banco_dados import BancoDados
import time

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_cabecalho(titulo):
    print("\n" + "=" * 70)
    print(f"  {titulo}")
    print("=" * 70)

def verificar_dependencias():
    """Verifica se as dependências estão instaladas"""
    print_cabecalho("1. VERIFICANDO DEPENDÊNCIAS")
    
    try:
        import flask
        print("✓ Flask instalado")
    except ImportError:
        print("✗ Flask não encontrado")
        print("  Instalando Flask...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    try:
        import flask_cors
        print("✓ Flask-CORS instalado")
    except ImportError:
        print("✗ Flask-CORS não encontrado")
        print("  Instalando Flask-CORS...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def criar_banco_dados():
    """Cria o banco de dados com dados de exemplo"""
    print_cabecalho("2. CRIANDO BANCO DE DADOS")
    
    db = BancoDados('escola.db')
    
    # Verificar se já existem dados
    stats = db.obter_estatisticas()
    
    if stats['total_professores'] > 0:
        print("✓ Banco de dados já contém dados!")
        print(f"  • Professores: {stats['total_professores']}")
        print(f"  • Séries: {stats['total_series']}")
        print(f"  • Alunos: {stats['total_alunos']}")
        return db
    
    print("Criando dados de exemplo...")
    
    # Adicionar disciplinas padrão (Educação Infantil e Ensino Fundamental 1)
    print("\nAdicionando disciplinas...")
    disciplinas = [
        ('Português', 'Linguagem e comunicação'),
        ('Matemática', 'Lógica e operações numéricas'),
        ('Ciências', 'Conhecimento do mundo natural'),
        ('História', 'Conhecimento histórico e cultural'),
        ('Geografia', 'Espaço geográfico e sustentabilidade'),
        ('Educação Física', 'Movimento e saúde'),
        ('Artes', 'Expressão artística'),
        ('Inglês', 'Língua estrangeira'),
    ]
    
    disc_ids = {}
    for nome, descricao in disciplinas:
        disc_id = db.adicionar_disciplina(nome, descricao)
        disc_ids[nome] = disc_id
    
    # Adicionar professores
    print("Adicionando professores...")
    prof1 = db.adicionar_professor('João Silva', 'professor@escola.com', 'Letras2026', '(11) 98765-4321', 'Rua A, 100', '')
    prof2 = db.adicionar_professor('Maria Santos', 'maria@escola.com', 'senha123', '(11) 98765-4322', 'Rua B, 200', '')
    prof3 = db.adicionar_professor('Carlos Oliveira', 'carlos@escola.com', 'senha123', '(11) 98765-4323', 'Rua C, 300', '')
    prof4 = db.adicionar_professor('Ana Costa', 'ana@escola.com', 'Ana123456', '(11) 98765-4324', 'Rua D, 400', '')
    
    # Associar disciplinas aos professores
    if prof1:
        db.adicionar_disciplina_professor(prof1, disc_ids.get('Português', 1))
        db.adicionar_disciplina_professor(prof1, disc_ids.get('Matemática', 2))
    if prof2:
        db.adicionar_disciplina_professor(prof2, disc_ids.get('Ciências', 3))
        db.adicionar_disciplina_professor(prof2, disc_ids.get('História', 4))
    if prof3:
        db.adicionar_disciplina_professor(prof3, disc_ids.get('Educação Física', 6))
        db.adicionar_disciplina_professor(prof3, disc_ids.get('Artes', 7))
    if prof4:
        db.adicionar_disciplina_professor(prof4, disc_ids.get('Inglês', 8))
        db.adicionar_disciplina_professor(prof4, disc_ids.get('Geografia', 5))
    
    # Adicionar séries
    print("Adicionando séries...")
    serie1 = db.adicionar_serie('Pré-Escolar A', 2026, 'Turma da manhã')
    serie2 = db.adicionar_serie('Pré-Escolar B', 2026, 'Turma da tarde')
    serie3 = db.adicionar_serie('1º Ano A', 2026, 'Turma da manhã')
    
    # Associar séries aos professores
    if prof1:
        db.adicionar_serie_professor(prof1, serie1)
        db.adicionar_serie_professor(prof1, serie3)
    if prof2:
        db.adicionar_serie_professor(prof2, serie2)
    if prof3:
        db.adicionar_serie_professor(prof3, serie1)
    if prof4:
        db.adicionar_serie_professor(prof4, serie3)
    
    # Adicionar alunos
    print("Adicionando alunos...")
    alunos_dados = [
        ('Ana Silva', 'ana@email.com', '12345678900', '98765432100', 'Rua A, 100', 'Ana12345', serie1, '2020-03-15', 'João Silva', '(11) 98765-4321'),
        ('Bruno Santos', 'bruno@email.com', '12345678901', '98765432101', 'Rua B, 200', 'Bruno12345', serie1, '2020-05-20', 'Carlos Santos', '(11) 98765-4322'),
        ('Carla Oliveira', 'carla@email.com', '12345678902', '98765432102', 'Rua C, 300', 'Carla12345', serie1, '2020-07-10', 'Pedro Oliveira', '(11) 98765-4323'),
        ('Diego Martins', 'diego@email.com', '12345678903', '98765432103', 'Rua D, 400', 'Diego12345', serie2, '2020-01-05', 'Jorge Martins', '(11) 98765-4324'),
        ('Elisa Ferreira', 'elisa@email.com', '12345678904', '98765432104', 'Rua E, 500', 'Elisa12345', serie2, '2020-09-12', 'Paulo Ferreira', '(11) 98765-4325'),
    ]
    
    alunos_ids = []
    for nome, email, cpf, cpf_resp, endereco, senha, serie_id, data_nasc, resp, tel in alunos_dados:
        aluno_id = db.adicionar_aluno(nome, email, cpf, cpf_resp, endereco, senha, serie_id, data_nasc, resp, tel)
        alunos_ids.append(aluno_id)
    
    # Filtrar apenas alunos que foram adicionados com sucesso
    alunos_ids = [aid for aid in alunos_ids if aid is not None]
    
    print("Adicionando registros de frequência...")
    from datetime import datetime, timedelta
    data_base = datetime(2026, 4, 17)
    
    for i in range(5):
        data = (data_base - timedelta(days=i)).date()
        for aluno_id in alunos_ids:
            presente = aluno_id % 2 == 0 or i < 4  # Alguns alunos com faltas
            db.registrar_frequencia(aluno_id, data, presente)
    
    # Adicionar notas
    print("Adicionando registros de notas...")
    notas_dados = [
        (alunos_ids[0], prof1, 'Português', 8.5, 1),
        (alunos_ids[0], prof1, 'Matemática', 7.5, 1),
        (alunos_ids[0], prof3, 'Educação Física', 9.0, 1),
        (alunos_ids[1], prof1, 'Português', 7.0, 1),
        (alunos_ids[1], prof2, 'Ciências', 8.0, 1),
        (alunos_ids[2], prof1, 'Matemática', 6.5, 1),
        (alunos_ids[2], prof2, 'Ciências', 8.0, 1),
    ]
    
    for aluno_id, prof_id, disciplina, nota, bimestre in notas_dados:
        db.registrar_nota(aluno_id, prof_id, disciplina, nota, bimestre)
    
    print("\n✓ Banco de dados configurado com sucesso!")
    stats = db.obter_estatisticas()
    print(f"\nEstatísticas:")
    print(f"  • Professores: {stats['total_professores']}")
    print(f"  • Séries: {stats['total_series']}")
    print(f"  • Alunos: {stats['total_alunos']}")
    print(f"  • Registros de Frequência: {stats['total_registros_frequencia']}")
    print(f"  • Registros de Notas: {stats['total_registros_notas']}")
    
    return db

def exibir_informacoes(db):
    """Exibe informações do banco de dados"""
    print_cabecalho("3. INFORMAÇÕES DO BANCO DE DADOS")
    
    print("\n📚 DISCIPLINAS:")
    disciplinas = db.listar_disciplinas()
    for disc in disciplinas:
        print(f"  • {disc['nome']}")
    
    print("\n👨‍🏫 PROFESSORES:")
    professores = db.listar_professores()
    for prof in professores:
        print(f"  • {prof['nome']} - Email: {prof['email']}")
    
    print("\n🎓 SÉRIES:")
    series = db.listar_series()
    for ser in series:
        print(f"  • {ser['nome']} (Ano {ser['ano']})")
    
    print("\n👥 ALUNOS:")
    alunos = db.listar_alunos()
    for aluno in alunos:
        print(f"  • {aluno['nome']} (Mat: {aluno['matricula']})")

def exibir_proximos_passos():
    """Exibe os próximos passos"""
    print_cabecalho("4. PRÓXIMOS PASSOS")
    
    print("""
1. INICIAR O SERVIDOR FLASK:
   • Execute: python app.py
   • O servidor será iniciado em http://localhost:5000

2. ACESSAR O PAINEL:
   • Abra um navegador
   • Acesse: http://localhost:5000/painel.html
   
3. FAZER LOGIN (Se tiver uma página de login):
   • Email: joao@escola.com
   • Senha: senha123
   • (Ou qualquer outro professor cadastrado)

4. USAR A API REST:
   • Consulte a documentação em README.md
   • Exemplos em exemplos.py

5. INTEGRAR COM SEU SITE:
   • Use painel.html como referência
   • Adapte para suas necessidades
   • Consulte os exemplos de requisições em exemplos.py

ENDPOINTS PRINCIPAIS:
   • GET  /api/estatisticas              - Obter estatísticas
   • POST /api/login                      - Fazer login
   • GET  /api/professores                - Listar professores
   • GET  /api/series                     - Listar séries
   • GET  /api/alunos                     - Listar alunos
   • POST /api/frequencia                 - Registrar frequência
   • POST /api/notas                      - Registrar nota
   • GET  /api/relatorio/frequencia/<id>  - Relatório de frequência
   • GET  /api/relatorio/notas/<id>       - Relatório de notas
    """)

def main():
    limpar_tela()
    
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║         SISTEMA DE GESTÃO ESCOLAR - INICIALIZAÇÃO RÁPIDA        ║
    ║                                                                  ║
    ║  Banco de Dados SQLite | API REST Flask | Painel Web             ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # Executar passos
    verificar_dependencias()
    db = criar_banco_dados()
    exibir_informacoes(db)
    exibir_proximos_passos()
    
    print_cabecalho("CONFIGURAÇÃO CONCLUÍDA!")
    print("\n✓ Sistema pronto para usar!")
    print("\nPróximo comando a executar:")
    print("  python app.py\n")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Erro durante a inicialização: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
