"""
Banco de dados para sistema de gestão escolar
Gerenciamento com SQLite
"""

import sqlite3
import bcrypt
from datetime import datetime
import os
import random
import string

class BancoDados:
    def __init__(self, arquivo_db='escola.db'):
        self.arquivo_db = arquivo_db
        self.criar_banco_dados()
    
    def conexao(self):
        """Cria e retorna uma conexão com o banco de dados"""
        conn = sqlite3.connect(self.arquivo_db, timeout=10.0)
        conn.row_factory = sqlite3.Row
        return conn
    
    # ===== FUNÇÕES DE SEGURANÇA (BCRYPT) =====
    
    def hash_senha(self, senha):
        """Gera hash seguro da senha usando bcrypt"""
        return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verificar_senha(self, senha, hash_armazenado):
        """Verifica se a senha corresponde ao hash armazenado"""
        try:
            return bcrypt.checkpw(senha.encode('utf-8'), hash_armazenado.encode('utf-8'))
        except Exception:
            return False
    
    def usuario_eh_admin(self, user_id):
        """Verifica se um usuário é administrador"""
        # Por enquanto, apenas user_id 0 é admin
        # TODO: Implementar tabela de usuários com papéis
        return str(user_id) == '0' or str(user_id) == 'admin'
    
    def criar_banco_dados(self):
        """Cria as tabelas do banco de dados"""
        if not os.path.exists(self.arquivo_db):
            print(f"Criando banco de dados: {self.arquivo_db}")
            conn = self.conexao()
            cursor = conn.cursor()
            
            # Professores (com dados pessoais expandidos)
            cursor.execute('''CREATE TABLE IF NOT EXISTS professores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                cpf TEXT,
                data_nascimento DATE,
                celular TEXT,
                endereco TEXT,
                foto TEXT,
                data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # Séries
            cursor.execute('''CREATE TABLE IF NOT EXISTS series (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                ano INTEGER NOT NULL,
                descricao TEXT,
                data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # Alunos
            cursor.execute('''CREATE TABLE IF NOT EXISTS alunos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT,
                matricula TEXT UNIQUE NOT NULL,
                cpf TEXT UNIQUE,
                cpf_responsavel TEXT,
                endereco TEXT,
                senha TEXT,
                serie_id INTEGER NOT NULL,
                data_nascimento DATE,
                responsavel TEXT,
                telefone TEXT,
                data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (serie_id) REFERENCES series(id)
            )''')
            
            # Frequência
            cursor.execute('''CREATE TABLE IF NOT EXISTS frequencia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aluno_id INTEGER NOT NULL,
                data DATE NOT NULL,
                presente BOOLEAN DEFAULT 1,
                observacao TEXT,
                data_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (aluno_id) REFERENCES alunos(id),
                UNIQUE(aluno_id, data)
            )''')
            
            # Notas
            cursor.execute('''CREATE TABLE IF NOT EXISTS notas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aluno_id INTEGER NOT NULL,
                professor_id INTEGER NOT NULL,
                disciplina TEXT NOT NULL,
                nota REAL NOT NULL,
                bimestre INTEGER NOT NULL,
                data_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                observacao TEXT,
                FOREIGN KEY (aluno_id) REFERENCES alunos(id),
                FOREIGN KEY (professor_id) REFERENCES professores(id)
            )''')
            
            # Disciplinas
            cursor.execute('''CREATE TABLE IF NOT EXISTS disciplinas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                descricao TEXT,
                data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # Relacionamento: Professor - Disciplina
            cursor.execute('''CREATE TABLE IF NOT EXISTS professor_disciplina (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                professor_id INTEGER NOT NULL,
                disciplina_id INTEGER NOT NULL,
                data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (professor_id) REFERENCES professores(id),
                FOREIGN KEY (disciplina_id) REFERENCES disciplinas(id),
                UNIQUE(professor_id, disciplina_id)
            )''')
            
            # Relacionamento: Professor - Turma (Série)
            cursor.execute('''CREATE TABLE IF NOT EXISTS professor_serie (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                professor_id INTEGER NOT NULL,
                serie_id INTEGER NOT NULL,
                data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (professor_id) REFERENCES professores(id),
                FOREIGN KEY (serie_id) REFERENCES series(id),
                UNIQUE(professor_id, serie_id)
            )''')
            
            # Relacionamento: Professor - Disciplina - Turma (Série)
            # Especifica qual professor leciona qual disciplina em qual turma
            cursor.execute('''CREATE TABLE IF NOT EXISTS professor_disciplina_serie (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                professor_id INTEGER NOT NULL,
                disciplina_id INTEGER NOT NULL,
                serie_id INTEGER NOT NULL,
                data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (professor_id) REFERENCES professores(id),
                FOREIGN KEY (disciplina_id) REFERENCES disciplinas(id),
                FOREIGN KEY (serie_id) REFERENCES series(id),
                UNIQUE(professor_id, disciplina_id, serie_id)
            )''')
            
            # ===== TABELAS DE ARQUIVO MORTO (SOFT DELETE) =====
            
            # Professores Deletados (Arquivo Morto)
            cursor.execute('''CREATE TABLE IF NOT EXISTS professores_mortos (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                email TEXT NOT NULL,
                senha TEXT NOT NULL,
                cpf TEXT,
                data_nascimento DATE,
                celular TEXT,
                endereco TEXT,
                foto TEXT,
                data_cadastro DATETIME,
                data_exclusao DATETIME DEFAULT CURRENT_TIMESTAMP,
                motivo_exclusao TEXT
            )''')
            
            # Alunos Deletados (Arquivo Morto)
            cursor.execute('''CREATE TABLE IF NOT EXISTS alunos_mortos (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                email TEXT,
                matricula TEXT NOT NULL,
                cpf TEXT,
                cpf_responsavel TEXT,
                endereco TEXT,
                senha TEXT,
                serie_id INTEGER,
                data_nascimento DATE,
                responsavel TEXT,
                telefone TEXT,
                data_cadastro DATETIME,
                data_exclusao DATETIME DEFAULT CURRENT_TIMESTAMP,
                motivo_exclusao TEXT
            )''')
            
            # Backup de registros relacionados aos arquivos mortos
            cursor.execute('''CREATE TABLE IF NOT EXISTS frequencia_morta (
                id INTEGER PRIMARY KEY,
                aluno_id INTEGER NOT NULL,
                data DATE NOT NULL,
                presente BOOLEAN DEFAULT 1,
                observacao TEXT,
                data_registro DATETIME
            )''')
            
            cursor.execute('''CREATE TABLE IF NOT EXISTS notas_mortas (
                id INTEGER PRIMARY KEY,
                aluno_id INTEGER NOT NULL,
                professor_id INTEGER NOT NULL,
                disciplina TEXT NOT NULL,
                nota REAL NOT NULL,
                bimestre INTEGER NOT NULL,
                data_registro DATETIME,
                observacao TEXT
            )''')
            
            # Atividades (criadas pelo professor para a turma)
            cursor.execute('''CREATE TABLE IF NOT EXISTS atividades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                serie_id INTEGER NOT NULL,
                professor_id INTEGER NOT NULL,
                titulo TEXT NOT NULL,
                descricao TEXT,
                data_criacao DATE,
                data_entrega DATE,
                status TEXT DEFAULT 'ativa',
                data_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (serie_id) REFERENCES series(id),
                FOREIGN KEY (professor_id) REFERENCES professores(id)
            )''')
            
            # Criar índices
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alunos_serie ON alunos(serie_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_frequencia_aluno ON frequencia(aluno_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_notas_aluno ON notas(aluno_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_notas_professor ON notas(professor_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_prof_disciplina ON professor_disciplina(professor_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_prof_serie ON professor_serie(professor_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_professores_mortos ON professores_mortos(data_exclusao)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alunos_mortos ON alunos_mortos(data_exclusao)')
            
            conn.commit()
            conn.close()
            print("Banco de dados criado com sucesso!")
        
        # Executar migrações de segurança
        self.aplicar_migracoes()
    
    def aplicar_migracoes(self):
        """Aplica migrações seguras (adiciona colunas faltantes sem perder dados)"""
        conn = self.conexao()
        cursor = conn.cursor()
        
        try:
            # Verificar e adicionar colunas na tabela notas se não existirem
            cursor.execute("PRAGMA table_info(notas)")
            colunas_existentes = [row[1] for row in cursor.fetchall()]
            
            # Adicionar coluna 'avm' (Avaliação Mensal) se não existir
            if 'avm' not in colunas_existentes:
                cursor.execute("ALTER TABLE notas ADD COLUMN avm REAL DEFAULT NULL")
                print("✓ Coluna 'avm' adicionada à tabela notas")
            
            # Adicionar coluna 'avb' (Avaliação Bimestral) se não existir
            if 'avb' not in colunas_existentes:
                cursor.execute("ALTER TABLE notas ADD COLUMN avb REAL DEFAULT NULL")
                print("✓ Coluna 'avb' adicionada à tabela notas")
            
            # Adicionar coluna 'rec' (Recuperação) se não existir
            if 'rec' not in colunas_existentes:
                cursor.execute("ALTER TABLE notas ADD COLUMN rec REAL DEFAULT NULL")
                print("✓ Coluna 'rec' adicionada à tabela notas")
            
            # Adicionar coluna 'mb' (Média Bimestral) se não existir
            if 'mb' not in colunas_existentes:
                cursor.execute("ALTER TABLE notas ADD COLUMN mb REAL DEFAULT NULL")
                print("✓ Coluna 'mb' adicionada à tabela notas")
            
            conn.commit()
        except Exception as e:
            print(f"Erro ao aplicar migrações: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    # ===== OPERAÇÕES COM PROFESSORES =====
    def adicionar_professor(self, nome, email, senha, cpf='', data_nascimento='', celular='', endereco='', foto=''):
        """Adiciona um novo professor com dados pessoais"""
        conn = self.conexao()
        cursor = conn.cursor()
        
        # Hash da senha com bcrypt (seguro)
        senha_hash = self.hash_senha(senha)
        
        try:
            cursor.execute('''INSERT INTO professores (nome, email, senha, cpf, data_nascimento, celular, endereco, foto)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (nome, email, senha_hash, cpf, data_nascimento, celular, endereco, foto))
            conn.commit()
            print(f"Professor {nome} cadastrado com sucesso!")
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            print(f"Erro: Email {email} já cadastrado!")
            return None
        finally:
            conn.close()
    
    def atualizar_professor(self, professor_id, nome=None, email=None, cpf=None, data_nascimento=None, celular=None, endereco=None, foto=None, senha=None):
        """Atualiza dados de um professor"""
        conn = self.conexao()
        cursor = conn.cursor()
        
        try:
            # Verificar se email já existe para outro professor (se email for atualizado)
            if email not in (None, ''):
                cursor.execute("SELECT id FROM professores WHERE email = ? AND id != ?", (email, professor_id))
                if cursor.fetchone():
                    print(f"Erro: Email {email} já está cadastrado para outro professor")
                    conn.close()
                    return False
            
            # Construir query dinamicamente com os campos fornecidos
            campos = []
            valores = []
            
            if nome not in (None, ''):
                campos.append('nome = ?')
                valores.append(nome)
            if email not in (None, ''):
                campos.append('email = ?')
                valores.append(email)
            if cpf not in (None, ''):
                campos.append('cpf = ?')
                valores.append(cpf)
            if data_nascimento not in (None, ''):
                campos.append('data_nascimento = ?')
                valores.append(data_nascimento)
            if celular not in (None, ''):
                campos.append('celular = ?')
                valores.append(celular)
            if endereco not in (None, ''):
                campos.append('endereco = ?')
                valores.append(endereco)
            if foto not in (None, ''):
                campos.append('foto = ?')
                valores.append(foto)
            if senha not in (None, ''):
                hash_senha = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode('utf-8')
                campos.append('senha = ?')
                valores.append(hash_senha)
            
            if not campos:
                return False
            
            valores.append(professor_id)
            
            query = f"UPDATE professores SET {', '.join(campos)} WHERE id = ?"
            cursor.execute(query, valores)
            conn.commit()
            
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"Erro ao atualizar professor: {e}")
            return False
        finally:
            conn.close()
    
    def adicionar_disciplina_professor(self, professor_id, disciplina_id):
        """Adiciona uma disciplina ao professor"""
        conn = self.conexao()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''INSERT INTO professor_disciplina (professor_id, disciplina_id)
                VALUES (?, ?)''', (professor_id, disciplina_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            print(f"Disciplina já associada ao professor!")
            return False
        finally:
            conn.close()
    
    def adicionar_serie_professor(self, professor_id, serie_id):
        """Adiciona uma série/turma ao professor"""
        conn = self.conexao()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''INSERT INTO professor_serie (professor_id, serie_id)
                VALUES (?, ?)''', (professor_id, serie_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            print(f"Série já associada ao professor!")
            return False
        finally:
            conn.close()
    
    def obter_disciplinas_professor(self, professor_id):
        """Obtém todas as disciplinas de um professor"""
        conn = self.conexao()
        cursor = conn.cursor()
        cursor.execute('''SELECT d.id, d.nome FROM disciplinas d
                         JOIN professor_disciplina pd ON d.id = pd.disciplina_id
                         WHERE pd.professor_id = ?''', (professor_id,))
        disciplinas = cursor.fetchall()
        conn.close()
        return disciplinas
    
    def obter_series_professor(self, professor_id):
        """Obtém todas as séries/turmas de um professor"""
        conn = self.conexao()
        cursor = conn.cursor()
        cursor.execute('''SELECT s.id, s.nome, s.ano FROM series s
                         JOIN professor_serie ps ON s.id = ps.serie_id
                         WHERE ps.professor_id = ?''', (professor_id,))
        series = cursor.fetchall()
        conn.close()
        return series
    
    def remover_serie_professor(self, professor_id, serie_id):
        """Remove uma série/turma do professor"""
        conn = self.conexao()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''DELETE FROM professor_serie 
                WHERE professor_id = ? AND serie_id = ?''', (professor_id, serie_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao remover série do professor: {e}")
            return False
        finally:
            conn.close()
    
    # ===== GERENCIAMENTO DE PROFESSOR-DISCIPLINA-TURMA =====
    
    def adicionar_disciplina_professor_serie(self, professor_id, disciplina_id, serie_id):
        """Associa uma disciplina a um professor em uma turma específica"""
        conn = self.conexao()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''INSERT INTO professor_disciplina_serie (professor_id, disciplina_id, serie_id)
                VALUES (?, ?, ?)''', (professor_id, disciplina_id, serie_id))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            # Já existe essa associação
            return False
        finally:
            conn.close()
    
    def obter_disciplinas_professor_serie(self, professor_id, serie_id):
        """Obtém todas as disciplinas que um professor leciona em uma turma"""
        conn = self.conexao()
        cursor = conn.cursor()
        cursor.execute('''SELECT d.id, d.nome FROM disciplinas d
                         JOIN professor_disciplina_serie pds ON d.id = pds.disciplina_id
                         WHERE pds.professor_id = ? AND pds.serie_id = ?
                         ORDER BY d.nome''', (professor_id, serie_id))
        disciplinas = cursor.fetchall()
        conn.close()
        return disciplinas
    
    def remover_disciplina_professor_serie(self, professor_id, disciplina_id, serie_id):
        """Remove uma disciplina de um professor em uma turma"""
        conn = self.conexao()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''DELETE FROM professor_disciplina_serie 
                WHERE professor_id = ? AND disciplina_id = ? AND serie_id = ?''', 
                (professor_id, disciplina_id, serie_id))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao remover disciplina da turma: {e}")
            return False
        finally:
            conn.close()
    
    def verificar_login_professor(self, email, senha):
        """Verifica o login do professor"""
        conn = self.conexao()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, nome, senha FROM professores WHERE email = ?', (email,))
        resultado = cursor.fetchone()
        conn.close()
        
        # Verificar senha com bcrypt
        if resultado and self.verificar_senha(senha, resultado['senha']):
            return {'id': resultado['id'], 'nome': resultado['nome']}
        return None
    
    def verificar_login_professor_com_turmas(self, email, senha):
        """Verifica o login do professor e retorna suas turmas"""
        conn = self.conexao()
        cursor = conn.cursor()
        
        # Buscar professor
        cursor.execute('SELECT id, nome, senha FROM professores WHERE email = ?', (email,))
        professor = cursor.fetchone()
        
        if not professor or not self.verificar_senha(senha, professor['senha']):
            conn.close()
            return None
        
        prof_id = professor['id']
        prof_nome = professor['nome']
        
        # Buscar turmas do professor
        cursor.execute('''
            SELECT s.id, s.nome, s.ano 
            FROM series s
            JOIN professor_serie ps ON s.id = ps.serie_id
            WHERE ps.professor_id = ?
            ORDER BY s.nome
        ''', (prof_id,))
        turmas = cursor.fetchall()
        conn.close()
        
        return {
            'id': prof_id,
            'nome': prof_nome,
            'turmas': [dict(t) for t in turmas]
        }
    
    def professor_pode_acessar_turma(self, professor_id, serie_id):
        """Verifica se um professor pode acessar uma turma específica"""
        conn = self.conexao()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 1 FROM professor_serie 
            WHERE professor_id = ? AND serie_id = ?
        ''', (professor_id, serie_id))
        
        resultado = cursor.fetchone() is not None
        conn.close()
        
        return resultado
    
    def aluno_pode_acessar_turma(self, aluno_id, serie_id):
        """Verifica se um aluno pode acessar uma turma específica"""
        conn = self.conexao()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 1 FROM alunos 
            WHERE id = ? AND serie_id = ?
        ''', (aluno_id, serie_id))
        
        resultado = cursor.fetchone() is not None
        conn.close()
        
        return resultado
    
    def verificar_login_aluno(self, email, senha):
        """Verifica o login do aluno com dados da turma"""
        conn = self.conexao()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.id, a.nome, a.matricula, a.serie_id, s.nome as serie_nome, s.ano, a.senha
            FROM alunos a
            JOIN series s ON a.serie_id = s.id
            WHERE a.email = ?
        ''', (email,))
        resultado = cursor.fetchone()
        conn.close()
        
        # Verificar senha com bcrypt
        if resultado and self.verificar_senha(senha, resultado['senha']):
            # Retornar sem a senha
            return {
                'id': resultado['id'],
                'nome': resultado['nome'],
                'matricula': resultado['matricula'],
                'serie_id': resultado['serie_id'],
                'serie_nome': resultado['serie_nome'],
                'ano': resultado['ano']
            }
        return None
    
    def verificar_login_aluno_por_matricula(self, matricula, senha):
        """Verifica o login do aluno usando matrícula ao invés de email"""
        conn = self.conexao()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.id, a.nome, a.matricula, a.serie_id, s.nome as serie_nome, s.ano, a.senha
            FROM alunos a
            JOIN series s ON a.serie_id = s.id
            WHERE a.matricula = ?
        ''', (matricula,))
        resultado = cursor.fetchone()
        conn.close()
        
        # Verificar senha com bcrypt
        if resultado and self.verificar_senha(senha, resultado['senha']):
            # Retornar sem a senha
            return {
                'id': resultado['id'],
                'nome': resultado['nome'],
                'matricula': resultado['matricula'],
                'serie_id': resultado['serie_id'],
                'serie_nome': resultado['serie_nome'],
                'ano': resultado['ano']
            }
        return None
    
    def listar_professores(self):
        """Lista todos os professores"""
        conn = self.conexao()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM professores')
        professores = cursor.fetchall()
        conn.close()
        return professores
    
    def obter_professor_por_id(self, professor_id):
        """Obtém um professor pelo ID"""
        conn = self.conexao()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM professores WHERE id = ?', (professor_id,))
        professor = cursor.fetchone()
        conn.close()
        return professor
    
    # ===== OPERAÇÕES COM DISCIPLINAS =====
    def adicionar_disciplina(self, nome, descricao=''):
        """Adiciona uma nova disciplina"""
        conn = self.conexao()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''INSERT INTO disciplinas (nome, descricao)
                VALUES (?, ?)''', (nome, descricao))
            conn.commit()
            print(f"Disciplina {nome} cadastrada com sucesso!")
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            print(f"Erro: Disciplina {nome} já existe!")
            return None
        finally:
            conn.close()
    
    def listar_disciplinas(self):
        """Lista todas as disciplinas"""
        conn = self.conexao()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM disciplinas')
        disciplinas = cursor.fetchall()
        conn.close()
        return disciplinas
    
    # ===== OPERAÇÕES COM SÉRIES =====
    def adicionar_serie(self, nome, ano, descricao=''):
        """Adiciona uma nova série"""
        conn = self.conexao()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''INSERT INTO series (nome, ano, descricao)
                VALUES (?, ?, ?)''', (nome, ano, descricao))
            conn.commit()
            print(f"Série {nome} cadastrada com sucesso!")
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            print(f"Erro: Série {nome} já existe!")
            return None
        finally:
            conn.close()
    
    def listar_series(self):
        """Lista todas as séries"""
        conn = self.conexao()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM series')
        series = cursor.fetchall()
        conn.close()
        return series
    
    def obter_serie_por_id(self, serie_id):
        """Obtém uma série pelo ID"""
        conn = self.conexao()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM series WHERE id = ?', (serie_id,))
        serie = cursor.fetchone()
        conn.close()
        return serie
    
    # ===== OPERAÇÕES COM ALUNOS =====
    def gerar_matricula(self):
        """Gera uma matrícula automática com formato: 3 letras + 5 números + / + ano"""
        try:
            # 3 letras aleatórias em maiúsculas
            letras = ''.join(random.choices(string.ascii_uppercase, k=3))
            
            # 5 números aleatórios
            numeros = ''.join(random.choices(string.digits, k=5))
            
            # Ano atual
            ano = datetime.now().year
            
            # Formato final: ABC12345/2026
            matricula = f"{letras}{numeros}/{ano}"
            
            # Verificar se a matrícula já existe
            conn = self.conexao()
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM alunos WHERE matricula = ?', (matricula,))
            
            if cursor.fetchone():
                conn.close()
                # Se existe, gerar nova matrícula recursivamente
                return self.gerar_matricula()
            
            conn.close()
            return matricula
        except Exception as e:
            print(f"Erro ao gerar matrícula: {e}")
            return None
    
    def adicionar_aluno(self, nome, email, cpf, cpf_responsavel, endereco, senha, serie_id, 
                       data_nascimento=None, responsavel='', telefone='', foto=None):
        """Adiciona um novo aluno com dados expandidos e matrícula automática"""
        try:
            # Gerar matrícula automaticamente
            matricula = self.gerar_matricula()
            
            if not matricula:
                print("Erro ao gerar matrícula!")
                return None
            
            # Fazer hash da senha com bcrypt (seguro)
            senha_hash = self.hash_senha(senha)
            
            conn = self.conexao()
            cursor = conn.cursor()
            
            cursor.execute('''INSERT INTO alunos 
                (nome, email, matricula, cpf, cpf_responsavel, endereco, senha, 
                 serie_id, data_nascimento, responsavel, telefone)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                (nome, email, matricula, cpf, cpf_responsavel, endereco, senha_hash,
                 serie_id, data_nascimento, responsavel, telefone))
            
            conn.commit()
            aluno_id = cursor.lastrowid
            conn.close()
            
            print(f"Aluno {nome} cadastrado com sucesso! Matrícula: {matricula}")
            return aluno_id
        except Exception as e:
            print(f"Erro ao adicionar aluno: {e}")
            return None
    
    def atualizar_aluno(self, aluno_id, nome=None, email=None, cpf=None, cpf_responsavel=None, 
                       endereco=None, serie_id=None, data_nascimento=None, responsavel=None, telefone=None):
        """Atualiza dados de um aluno"""
        conn = self.conexao()
        cursor = conn.cursor()
        
        try:
            # Construir query dinamicamente com os campos fornecidos
            campos = []
            valores = []
            
            if nome not in (None, ''):
                campos.append('nome = ?')
                valores.append(nome)
            if email not in (None, ''):
                campos.append('email = ?')
                valores.append(email)
            if cpf not in (None, ''):
                campos.append('cpf = ?')
                valores.append(cpf)
            if cpf_responsavel not in (None, ''):
                campos.append('cpf_responsavel = ?')
                valores.append(cpf_responsavel)
            if endereco not in (None, ''):
                campos.append('endereco = ?')
                valores.append(endereco)
            if serie_id is not None:
                campos.append('serie_id = ?')
                valores.append(serie_id)
            if data_nascimento not in (None, ''):
                campos.append('data_nascimento = ?')
                valores.append(data_nascimento)
            if responsavel not in (None, ''):
                campos.append('responsavel = ?')
                valores.append(responsavel)
            if telefone not in (None, ''):
                campos.append('telefone = ?')
                valores.append(telefone)
            
            if not campos:
                return False
            
            valores.append(aluno_id)
            
            query = f"UPDATE alunos SET {', '.join(campos)} WHERE id = ?"
            cursor.execute(query, valores)
            conn.commit()
            
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"Erro ao atualizar aluno: {e}")
            return False
        finally:
            conn.close()
    
    def listar_alunos(self, serie_id=None):
        """Lista alunos, opcionalmente filtrado por série"""
        conn = self.conexao()
        cursor = conn.cursor()
        
        if serie_id:
            cursor.execute('SELECT * FROM alunos WHERE serie_id = ?', (serie_id,))
        else:
            cursor.execute('SELECT * FROM alunos')
        
        alunos = cursor.fetchall()
        conn.close()
        return alunos
    
    def obter_aluno_por_id(self, aluno_id):
        """Obtém um aluno pelo ID"""
        conn = self.conexao()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM alunos WHERE id = ?', (aluno_id,))
        aluno = cursor.fetchone()
        conn.close()
        return aluno
    
    # ===== OPERAÇÕES COM FREQUÊNCIA =====
    def registrar_frequencia(self, aluno_id, data, presente, observacao=''):
        """Registra ou atualiza a frequência de um aluno (UPSERT)"""
        conn = self.conexao()
        cursor = conn.cursor()
        
        try:
            # Verificar se já existe registro para este aluno nesta data
            cursor.execute('SELECT id FROM frequencia WHERE aluno_id = ? AND data = ?', 
                         (aluno_id, data))
            resultado = cursor.fetchone()
            
            if resultado:
                # UPDATE se já existe
                cursor.execute('''UPDATE frequencia 
                    SET presente = ?, observacao = ? 
                    WHERE aluno_id = ? AND data = ?''', 
                    (presente, observacao, aluno_id, data))
                conn.commit()
                print(f"Frequência atualizada para aluno ID {aluno_id} em {data}")
                return resultado[0]
            else:
                # INSERT se não existe
                cursor.execute('''INSERT INTO frequencia (aluno_id, data, presente, observacao)
                    VALUES (?, ?, ?, ?)''', (aluno_id, data, presente, observacao))
                conn.commit()
                print(f"Frequência registrada para aluno ID {aluno_id} em {data}")
                return cursor.lastrowid
        except Exception as e:
            print(f"Erro ao registrar frequência: {e}")
            conn.rollback()
            return None
        finally:
            conn.close()
    
    def obter_frequencia_aluno(self, aluno_id, data_inicio=None, data_fim=None):
        """Obtém o histórico de frequência de um aluno"""
        conn = self.conexao()
        cursor = conn.cursor()
        
        if data_inicio and data_fim:
            cursor.execute('''SELECT * FROM frequencia 
                WHERE aluno_id = ? AND data BETWEEN ? AND ?
                ORDER BY data DESC''', (aluno_id, data_inicio, data_fim))
        else:
            cursor.execute('SELECT * FROM frequencia WHERE aluno_id = ? ORDER BY data DESC', (aluno_id,))
        
        frequencias = cursor.fetchall()
        conn.close()
        return frequencias
    
    def relatorio_frequencia_por_serie(self, serie_id, data_inicio, data_fim):
        """Gera relatório de frequência de uma série"""
        conn = self.conexao()
        cursor = conn.cursor()
        
        cursor.execute('''SELECT a.id, a.nome, a.matricula, COUNT(*) as total_dias,
                         SUM(CASE WHEN f.presente = 1 THEN 1 ELSE 0 END) as dias_presentes,
                         SUM(CASE WHEN f.presente = 0 THEN 1 ELSE 0 END) as dias_ausentes
                FROM alunos a
                LEFT JOIN frequencia f ON a.id = f.aluno_id AND f.data BETWEEN ? AND ?
                WHERE a.serie_id = ?
                GROUP BY a.id
                ORDER BY a.nome''', (data_inicio, data_fim, serie_id))
        
        relatorio = cursor.fetchall()
        conn.close()
        return relatorio
    
    # ===== OPERAÇÕES COM NOTAS =====
    def registrar_nota(self, aluno_id, professor_id, disciplina, nota, bimestre, observacao='', avm=None, avb=None, rec=None):
        """Registra uma nota para um aluno com suporte a AVM, AVB, REC"""
        conn = self.conexao()
        cursor = conn.cursor()
        
        try:
            # Calcular MB (Média Bimestral)
            mb = None
            if avm is not None and avb is not None:
                mb = (float(avm) + float(avb)) / 2
                
                # Se MB < 6 e há recuperação, aplicar fórmula de REC
                if mb < 6 and rec is not None:
                    # Tomar a maior nota entre AVM e AVB, e somar com REC, depois dividir por 2
                    maior_nota = max(float(avm), float(avb))
                    mb = (maior_nota + float(rec)) / 2
                    observacao = f"{observacao} [REC ativada]".strip()
            
            # Se nota não foi passada, usar MB como nota geral
            if nota is None and mb is not None:
                nota = mb
            
            cursor.execute('''INSERT INTO notas (aluno_id, professor_id, disciplina, nota, bimestre, observacao, avm, avb, rec, mb)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
                (aluno_id, professor_id, disciplina, nota, bimestre, observacao, avm, avb, rec, mb))
            conn.commit()
            print(f"Nota registrada para aluno ID {aluno_id} - MB: {mb}")
            return cursor.lastrowid
        except Exception as e:
            print(f"Erro ao registrar nota: {e}")
            return None
        finally:
            conn.close()
    
    def obter_notas_aluno(self, aluno_id, bimestre=None):
        """Obtém as notas de um aluno"""
        conn = self.conexao()
        cursor = conn.cursor()
        
        if bimestre:
            cursor.execute('''SELECT n.*, p.nome as professor 
                FROM notas n
                JOIN professores p ON n.professor_id = p.id
                WHERE n.aluno_id = ? AND n.bimestre = ?
                ORDER BY n.disciplina''', (aluno_id, bimestre))
        else:
            cursor.execute('''SELECT n.*, p.nome as professor 
                FROM notas n
                JOIN professores p ON n.professor_id = p.id
                WHERE n.aluno_id = ?
                ORDER BY n.bimestre, n.disciplina''', (aluno_id,))
        
        notas = cursor.fetchall()
        conn.close()
        return notas
    
    def relatorio_notas_por_serie(self, serie_id, bimestre):
        """Gera relatório de notas de uma série"""
        conn = self.conexao()
        cursor = conn.cursor()
        
        cursor.execute('''SELECT a.id, a.nome, a.matricula, n.disciplina, AVG(n.nota) as media
                FROM alunos a
                LEFT JOIN notas n ON a.id = n.aluno_id AND n.bimestre = ?
                WHERE a.serie_id = ?
                GROUP BY a.id, n.disciplina
                ORDER BY a.nome, n.disciplina''', (bimestre, serie_id))
        
        relatorio = cursor.fetchall()
        conn.close()
        return relatorio
    
    # ===== OPERAÇÕES COM ATIVIDADES =====
    
    def criar_atividade(self, serie_id, professor_id, titulo, descricao='', data_criacao=None, data_entrega=None):
        """Cria uma nova atividade para uma turma"""
        conn = self.conexao()
        cursor = conn.cursor()
        
        if not data_criacao:
            data_criacao = datetime.now().strftime('%Y-%m-%d')
        
        try:
            cursor.execute('''INSERT INTO atividades (serie_id, professor_id, titulo, descricao, data_criacao, data_entrega, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
                (serie_id, professor_id, titulo, descricao, data_criacao, data_entrega, 'ativa'))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Erro ao criar atividade: {e}")
            return None
        finally:
            conn.close()
    
    def obter_atividades_turma(self, serie_id):
        """Obtém todas as atividades de uma turma"""
        conn = self.conexao()
        cursor = conn.cursor()
        
        cursor.execute('''SELECT a.*, p.nome as professor_nome
            FROM atividades a
            JOIN professores p ON a.professor_id = p.id
            WHERE a.serie_id = ? AND a.status = 'ativa'
            ORDER BY a.data_criacao DESC''', (serie_id,))
        
        atividades = cursor.fetchall()
        conn.close()
        return atividades
    
    def excluir_atividade(self, atividade_id):
        """Marca atividade como inativa (soft delete)"""
        conn = self.conexao()
        cursor = conn.cursor()
        
        try:
            cursor.execute('UPDATE atividades SET status = ? WHERE id = ?', ('inativa', atividade_id))
            conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao excluir atividade: {e}")
            return False
        finally:
            conn.close()
    
    def atualizar_atividade(self, atividade_id, titulo=None, descricao=None, data_criacao=None, data_entrega=None, status=None):
        """Atualiza dados de uma atividade"""
        conn = self.conexao()
        cursor = conn.cursor()
        
        try:
            # Construir query dinamicamente com os campos fornecidos
            campos = []
            valores = []
            
            if titulo not in (None, ''):
                campos.append('titulo = ?')
                valores.append(titulo)
            if descricao not in (None, ''):
                campos.append('descricao = ?')
                valores.append(descricao)
            if data_criacao not in (None, ''):
                campos.append('data_criacao = ?')
                valores.append(data_criacao)
            if data_entrega not in (None, ''):
                campos.append('data_entrega = ?')
                valores.append(data_entrega)
            if status not in (None, ''):
                campos.append('status = ?')
                valores.append(status)
            
            if not campos:
                return False
            
            valores.append(atividade_id)
            
            query = f"UPDATE atividades SET {', '.join(campos)} WHERE id = ?"
            cursor.execute(query, valores)
            conn.commit()
            
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            print(f"Erro ao atualizar atividade: {e}")
            return False
        finally:
            conn.close()
    
    # ===== MÉTODOS DE EXCLUSÃO =====
    
    def excluir_professor(self, professor_id, motivo=''):
        """Move professor para arquivo morto (soft delete)"""
        conn = self.conexao()
        try:
            cursor = conn.cursor()
            
            # Obter dados do professor
            cursor.execute('SELECT * FROM professores WHERE id = ?', (professor_id,))
            prof = cursor.fetchone()
            
            if not prof:
                return False
            
            # Inserir no arquivo morto
            cursor.execute('''INSERT INTO professores_mortos 
                (id, nome, email, senha, cpf, data_nascimento, celular, endereco, foto, data_cadastro, motivo_exclusao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (prof['id'], prof['nome'], prof['email'], prof['senha'], prof['cpf'],
                 prof['data_nascimento'], prof['celular'], prof['endereco'], prof['foto'], prof['data_cadastro'], motivo))
            
            # Remover associações do professor
            cursor.execute('DELETE FROM professor_disciplina WHERE professor_id = ?', (professor_id,))
            cursor.execute('DELETE FROM professor_serie WHERE professor_id = ?', (professor_id,))
            
            # Remover professor da tabela ativa
            cursor.execute('DELETE FROM professores WHERE id = ?', (professor_id,))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Erro ao excluir professor: {e}")
            return False
        finally:
            conn.close()
    
    def excluir_aluno(self, aluno_id, motivo=''):
        """Move aluno para arquivo morto (soft delete) com seus registros"""
        conn = self.conexao()
        try:
            cursor = conn.cursor()
            
            # Obter dados do aluno
            cursor.execute('SELECT * FROM alunos WHERE id = ?', (aluno_id,))
            aluno = cursor.fetchone()
            
            if not aluno:
                return False
            
            # Inserir aluno no arquivo morto
            cursor.execute('''INSERT INTO alunos_mortos 
                (id, nome, email, matricula, cpf, cpf_responsavel, endereco, senha, 
                 serie_id, data_nascimento, responsavel, telefone, data_cadastro, motivo_exclusao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (aluno['id'], aluno['nome'], aluno['email'], aluno['matricula'], aluno['cpf'],
                 aluno['cpf_responsavel'], aluno['endereco'], aluno['senha'], aluno['serie_id'],
                 aluno['data_nascimento'], aluno['responsavel'], aluno['telefone'], aluno['data_cadastro'], motivo))
            
            # Mover registros de frequência para arquivo morto
            cursor.execute('SELECT * FROM frequencia WHERE aluno_id = ?', (aluno_id,))
            frequencias = cursor.fetchall()
            for freq in frequencias:
                cursor.execute('''INSERT INTO frequencia_morta 
                    (id, aluno_id, data, presente, observacao, data_registro)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                    (freq['id'], freq['aluno_id'], freq['data'], freq['presente'], 
                     freq['observacao'], freq['data_registro']))
            
            # Mover registros de notas para arquivo morto
            cursor.execute('SELECT * FROM notas WHERE aluno_id = ?', (aluno_id,))
            notas = cursor.fetchall()
            for nota in notas:
                cursor.execute('''INSERT INTO notas_mortas 
                    (id, aluno_id, professor_id, disciplina, nota, bimestre, data_registro, observacao)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (nota['id'], nota['aluno_id'], nota['professor_id'], nota['disciplina'],
                     nota['nota'], nota['bimestre'], nota['data_registro'], nota['observacao']))
            
            # Remover frequência do aluno
            cursor.execute('DELETE FROM frequencia WHERE aluno_id = ?', (aluno_id,))
            
            # Remover notas do aluno
            cursor.execute('DELETE FROM notas WHERE aluno_id = ?', (aluno_id,))
            
            # Remover aluno da tabela ativa
            cursor.execute('DELETE FROM alunos WHERE id = ?', (aluno_id,))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Erro ao excluir aluno: {e}")
            return False
        finally:
            conn.close()
    
    def restaurar_professor(self, professor_id):
        """Restaura professor do arquivo morto"""
        try:
            conn = self.conexao()
            cursor = conn.cursor()
            
            # Obter professor do arquivo morto
            cursor.execute('SELECT * FROM professores_mortos WHERE id = ?', (professor_id,))
            prof = cursor.fetchone()
            
            if not prof:
                return False
            
            # Restaurar na tabela ativa
            cursor.execute('''INSERT INTO professores (id, nome, email, senha, cpf, data_nascimento, celular, endereco, foto, data_cadastro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (prof['id'], prof['nome'], prof['email'], prof['senha'], prof['cpf'],
                 prof['data_nascimento'], prof['celular'], prof['endereco'], prof['foto'], prof['data_cadastro']))
            
            # Remover do arquivo morto
            cursor.execute('DELETE FROM professores_mortos WHERE id = ?', (professor_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao restaurar professor: {e}")
            return False
    
    def restaurar_aluno(self, aluno_id):
        """Restaura aluno e seus registros do arquivo morto"""
        try:
            conn = self.conexao()
            cursor = conn.cursor()
            
            # Obter aluno do arquivo morto
            cursor.execute('SELECT * FROM alunos_mortos WHERE id = ?', (aluno_id,))
            aluno = cursor.fetchone()
            
            if not aluno:
                return False
            
            # Restaurar aluno na tabela ativa
            cursor.execute('''INSERT INTO alunos 
                (id, nome, email, matricula, cpf, cpf_responsavel, endereco, senha, 
                 serie_id, data_nascimento, responsavel, telefone, data_cadastro)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (aluno['id'], aluno['nome'], aluno['email'], aluno['matricula'], aluno['cpf'],
                 aluno['cpf_responsavel'], aluno['endereco'], aluno['senha'], aluno['serie_id'],
                 aluno['data_nascimento'], aluno['responsavel'], aluno['telefone'], aluno['data_cadastro']))
            
            # Restaurar frequências
            cursor.execute('SELECT * FROM frequencia_morta WHERE aluno_id = ?', (aluno_id,))
            frequencias = cursor.fetchall()
            for freq in frequencias:
                cursor.execute('''INSERT INTO frequencia (id, aluno_id, data, presente, observacao, data_registro)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                    (freq['id'], freq['aluno_id'], freq['data'], freq['presente'],
                     freq['observacao'], freq['data_registro']))
                cursor.execute('DELETE FROM frequencia_morta WHERE id = ?', (freq['id'],))
            
            # Restaurar notas
            cursor.execute('SELECT * FROM notas_mortas WHERE aluno_id = ?', (aluno_id,))
            notas = cursor.fetchall()
            for nota in notas:
                cursor.execute('''INSERT INTO notas (id, aluno_id, professor_id, disciplina, nota, bimestre, data_registro, observacao)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (nota['id'], nota['aluno_id'], nota['professor_id'], nota['disciplina'],
                     nota['nota'], nota['bimestre'], nota['data_registro'], nota['observacao']))
                cursor.execute('DELETE FROM notas_mortas WHERE id = ?', (nota['id'],))
            
            # Remover aluno do arquivo morto
            cursor.execute('DELETE FROM alunos_mortos WHERE id = ?', (aluno_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Erro ao restaurar aluno: {e}")
            return False
    
    def listar_arquivo_morto(self):
        """Lista todos os professores e alunos deletados"""
        try:
            conn = self.conexao()
            cursor = conn.cursor()
            
            # Professores mortos
            cursor.execute('SELECT * FROM professores_mortos ORDER BY data_exclusao DESC')
            profs_mortos = [dict(p) for p in cursor.fetchall()]
            
            # Alunos mortos
            cursor.execute('SELECT * FROM alunos_mortos ORDER BY data_exclusao DESC')
            alunos_mortos = [dict(a) for a in cursor.fetchall()]
            
            conn.close()
            return {'professores': profs_mortos, 'alunos': alunos_mortos}
        except Exception as e:
            print(f"Erro ao listar arquivo morto: {e}")
            return {'professores': [], 'alunos': []}
    
    # ===== MÉTODOS DE EDIÇÃO =====
    
    def editar_professor(self, professor_id, nome=None, email=None, cpf=None, data_nascimento=None, celular=None, endereco=None, foto=None):
        """Edita dados do professor"""
        try:
            conn = self.conexao()
            cursor = conn.cursor()
            
            # Construir query dinamicamente
            updates = []
            params = []
            
            if nome is not None:
                updates.append('nome = ?')
                params.append(nome)
            if email is not None:
                updates.append('email = ?')
                params.append(email)
            if cpf is not None:
                updates.append('cpf = ?')
                params.append(cpf)
            if data_nascimento is not None:
                updates.append('data_nascimento = ?')
                params.append(data_nascimento)
            if celular is not None:
                updates.append('celular = ?')
                params.append(celular)
            if endereco is not None:
                updates.append('endereco = ?')
                params.append(endereco)
            if foto is not None:
                updates.append('foto = ?')
                params.append(foto)
            
            if not updates:
                return False
            
            params.append(professor_id)
            query = f"UPDATE professores SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao editar professor: {e}")
            return False
    
    def editar_aluno(self, aluno_id, nome=None, email=None, cpf=None, cpf_responsavel=None, 
                    endereco=None, senha=None, responsavel=None, telefone=None):
        """Edita dados do aluno"""
        try:
            conn = self.conexao()
            cursor = conn.cursor()
            
            # Construir query dinamicamente
            updates = []
            params = []
            
            if nome is not None:
                updates.append('nome = ?')
                params.append(nome)
            if email is not None:
                updates.append('email = ?')
                params.append(email)
            if cpf is not None:
                updates.append('cpf = ?')
                params.append(cpf)
            if cpf_responsavel is not None:
                updates.append('cpf_responsavel = ?')
                params.append(cpf_responsavel)
            if endereco is not None:
                updates.append('endereco = ?')
                params.append(endereco)
            if senha is not None:
                updates.append('senha = ?')
                params.append(senha)
            if responsavel is not None:
                updates.append('responsavel = ?')
                params.append(responsavel)
            if telefone is not None:
                updates.append('telefone = ?')
                params.append(telefone)
            
            if not updates:
                return False
            
            params.append(aluno_id)
            query = f"UPDATE alunos SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao editar aluno: {e}")
            return False
    
    def editar_disciplina(self, disciplina_id, nome=None, descricao=None):
        """Edita dados da disciplina"""
        try:
            conn = self.conexao()
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if nome is not None:
                updates.append('nome = ?')
                params.append(nome)
            if descricao is not None:
                updates.append('descricao = ?')
                params.append(descricao)
            
            if not updates:
                return False
            
            params.append(disciplina_id)
            query = f"UPDATE disciplinas SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao editar disciplina: {e}")
            return False
    
    def excluir_disciplina(self, disciplina_id):
        """Exclui uma disciplina do banco de dados"""
        try:
            conn = self.conexao()
            cursor = conn.cursor()
            
            # Remover associações de professores
            cursor.execute('DELETE FROM professor_disciplina WHERE disciplina_id = ?', (disciplina_id,))
            
            # Excluir a disciplina
            cursor.execute('DELETE FROM disciplinas WHERE id = ?', (disciplina_id,))
            
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao excluir disciplina: {e}")
            return False
    
    def editar_serie(self, serie_id, nome=None, ano=None, descricao=None):
        """Edita dados da série/turma"""
        try:
            conn = self.conexao()
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if nome is not None:
                updates.append('nome = ?')
                params.append(nome)
            if ano is not None:
                updates.append('ano = ?')
                params.append(ano)
            if descricao is not None:
                updates.append('descricao = ?')
                params.append(descricao)
            
            if not updates:
                return False
            
            params.append(serie_id)
            query = f"UPDATE series SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
            
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao editar série: {e}")
            return False
    
    def excluir_serie(self, serie_id):
        """Exclui uma série/turma do banco de dados"""
        try:
            conn = self.conexao()
            cursor = conn.cursor()
            
            # Verificar se há alunos associados à série
            cursor.execute('SELECT COUNT(*) FROM alunos WHERE serie_id = ?', (serie_id,))
            count_alunos = cursor.fetchone()[0]
            
            if count_alunos > 0:
                print(f"Erro: Não é possível excluir a série porque há {count_alunos} alunos associados!")
                conn.close()
                return False
            
            # Remover associações de professores
            cursor.execute('DELETE FROM professor_serie WHERE serie_id = ?', (serie_id,))
            
            # Excluir a série
            cursor.execute('DELETE FROM series WHERE id = ?', (serie_id,))
            
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao excluir série: {e}")
            return False
    
    def obter_estatisticas(self):
        """Obtém estatísticas gerais do banco de dados"""
        conn = self.conexao()
        cursor = conn.cursor()
        
        stats = {}
        
        cursor.execute('SELECT COUNT(*) FROM professores')
        stats['total_professores'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM series')
        stats['total_series'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM alunos')
        stats['total_alunos'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM frequencia')
        stats['total_registros_frequencia'] = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM notas')
        stats['total_registros_notas'] = cursor.fetchone()[0]
        
        conn.close()
        return stats


# Exemplo de uso
if __name__ == '__main__':
    db = BancoDados('escola.db')
    
    # Exibir estatísticas
    print("\n=== ESTATÍSTICAS DO BANCO ===")
    stats = db.obter_estatisticas()
    for chave, valor in stats.items():
        print(f"{chave}: {valor}")
