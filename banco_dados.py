"""
Banco de dados para sistema de gestão escolar
Gerenciamento com SQLite (local) e PostgreSQL via Supabase (produção)
"""

import os
import sqlite3
import bcrypt
from datetime import datetime
import random
import string
from typing import Optional, Dict, List, Any

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False


class BancoDados:
    def __init__(self, arquivo_db: str = 'escola.db'):
        """
        Inicializa a conexão com o banco de dados.
        Usa PostgreSQL (Supabase) em produção ou SQLite localmente.
        """
        self.arquivo_db = arquivo_db
        self.database_url = os.environ.get("DATABASE_URL")
        self.usar_postgresql = bool(self.database_url and PSYCOPG2_AVAILABLE)
        
        if self.usar_postgresql:
            print(f"✓ Usando PostgreSQL (Supabase)")
        else:
            print(f"✓ Usando SQLite local")
        
        self.criar_banco_dados()

    def conexao(self):
        """Cria e retorna uma conexão com o banco de dados"""
        if self.usar_postgresql:
            try:
                conn = psycopg2.connect(self.database_url)
                conn.cursor_factory = RealDictCursor
                return conn
            except Exception as e:
                print(f"❌ Erro ao conectar com PostgreSQL: {e}")
                raise
        else:
            conn = sqlite3.connect(self.arquivo_db, timeout=10.0)
            conn.row_factory = sqlite3.Row
            return conn

    # ===== FUNÇÕES DE SEGURANÇA (BCRYPT) =====

    def hash_senha(self, senha: str) -> str:
        """Gera hash seguro da senha usando bcrypt"""
        return bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verificar_senha(self, senha: str, hash_armazenado: str) -> bool:
        """Verifica se a senha corresponde ao hash armazenado"""
        try:
            return bcrypt.checkpw(senha.encode('utf-8'), hash_armazenado.encode('utf-8'))
        except Exception:
            return False

    def usuario_eh_admin(self, user_id: Any) -> bool:
        """Verifica se um usuário é administrador"""
        return str(user_id) in ('0', 'admin')

    def criar_banco_dados(self):
        """Cria as tabelas do banco de dados"""
        conn = self.conexao()
        cursor = conn.cursor()

        try:
            # Verificar se as tabelas já existem
            if self.usar_postgresql:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'professores'
                    )
                """)
            else:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='professores'")
            
            if cursor.fetchone():
                if not self.usar_postgresql:
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='professores'")
                    if cursor.fetchone():
                        print("✓ Tabelas já existem")
                        conn.close()
                        return
                else:
                    print("✓ Tabelas já existem")
                    conn.close()
                    return

            print("🔨 Criando tabelas do banco de dados...")

            # Professores
            cursor.execute('''CREATE TABLE IF NOT EXISTS professores (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                cpf TEXT,
                data_nascimento DATE,
                celular TEXT,
                endereco TEXT,
                foto TEXT,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''' if self.usar_postgresql else '''CREATE TABLE IF NOT EXISTS professores (
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
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                ano INTEGER NOT NULL,
                descricao TEXT,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''' if self.usar_postgresql else '''CREATE TABLE IF NOT EXISTS series (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                ano INTEGER NOT NULL,
                descricao TEXT,
                data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')

            # Alunos
            cursor.execute('''CREATE TABLE IF NOT EXISTS alunos (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                email TEXT,
                matricula TEXT UNIQUE NOT NULL,
                cpf TEXT UNIQUE,
                cpf_responsavel TEXT,
                endereco TEXT,
                senha TEXT,
                serie_id INTEGER NOT NULL REFERENCES series(id),
                data_nascimento DATE,
                responsavel TEXT,
                telefone TEXT,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''' if self.usar_postgresql else '''CREATE TABLE IF NOT EXISTS alunos (
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
                id SERIAL PRIMARY KEY,
                aluno_id INTEGER NOT NULL REFERENCES alunos(id),
                data DATE NOT NULL,
                presente BOOLEAN DEFAULT true,
                observacao TEXT,
                data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(aluno_id, data)
            )''' if self.usar_postgresql else '''CREATE TABLE IF NOT EXISTS frequencia (
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
                id SERIAL PRIMARY KEY,
                aluno_id INTEGER NOT NULL REFERENCES alunos(id),
                professor_id INTEGER NOT NULL REFERENCES professores(id),
                disciplina TEXT NOT NULL,
                nota REAL,
                bimestre INTEGER NOT NULL,
                data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                observacao TEXT,
                avm REAL,
                avb REAL,
                rec REAL,
                mb REAL
            )''' if self.usar_postgresql else '''CREATE TABLE IF NOT EXISTS notas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aluno_id INTEGER NOT NULL,
                professor_id INTEGER NOT NULL,
                disciplina TEXT NOT NULL,
                nota REAL,
                bimestre INTEGER NOT NULL,
                data_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                observacao TEXT,
                avm REAL,
                avb REAL,
                rec REAL,
                mb REAL,
                FOREIGN KEY (aluno_id) REFERENCES alunos(id),
                FOREIGN KEY (professor_id) REFERENCES professores(id)
            )''')

            # Disciplinas
            cursor.execute('''CREATE TABLE IF NOT EXISTS disciplinas (
                id SERIAL PRIMARY KEY,
                nome TEXT UNIQUE NOT NULL,
                descricao TEXT,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''' if self.usar_postgresql else '''CREATE TABLE IF NOT EXISTS disciplinas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL,
                descricao TEXT,
                data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
            )''')

            # Professor - Disciplina
            cursor.execute('''CREATE TABLE IF NOT EXISTS professor_disciplina (
                id SERIAL PRIMARY KEY,
                professor_id INTEGER NOT NULL REFERENCES professores(id),
                disciplina_id INTEGER NOT NULL REFERENCES disciplinas(id),
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(professor_id, disciplina_id)
            )''' if self.usar_postgresql else '''CREATE TABLE IF NOT EXISTS professor_disciplina (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                professor_id INTEGER NOT NULL,
                disciplina_id INTEGER NOT NULL,
                data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (professor_id) REFERENCES professores(id),
                FOREIGN KEY (disciplina_id) REFERENCES disciplinas(id),
                UNIQUE(professor_id, disciplina_id)
            )''')

            # Professor - Série
            cursor.execute('''CREATE TABLE IF NOT EXISTS professor_serie (
                id SERIAL PRIMARY KEY,
                professor_id INTEGER NOT NULL REFERENCES professores(id),
                serie_id INTEGER NOT NULL REFERENCES series(id),
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(professor_id, serie_id)
            )''' if self.usar_postgresql else '''CREATE TABLE IF NOT EXISTS professor_serie (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                professor_id INTEGER NOT NULL,
                serie_id INTEGER NOT NULL,
                data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (professor_id) REFERENCES professores(id),
                FOREIGN KEY (serie_id) REFERENCES series(id),
                UNIQUE(professor_id, serie_id)
            )''')

            # Professor - Disciplina - Série
            cursor.execute('''CREATE TABLE IF NOT EXISTS professor_disciplina_serie (
                id SERIAL PRIMARY KEY,
                professor_id INTEGER NOT NULL REFERENCES professores(id),
                disciplina_id INTEGER NOT NULL REFERENCES disciplinas(id),
                serie_id INTEGER NOT NULL REFERENCES series(id),
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(professor_id, disciplina_id, serie_id)
            )''' if self.usar_postgresql else '''CREATE TABLE IF NOT EXISTS professor_disciplina_serie (
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

            # Atividades
            cursor.execute('''CREATE TABLE IF NOT EXISTS atividades (
                id SERIAL PRIMARY KEY,
                serie_id INTEGER NOT NULL REFERENCES series(id),
                professor_id INTEGER NOT NULL REFERENCES professores(id),
                titulo TEXT NOT NULL,
                descricao TEXT,
                data_criacao DATE,
                data_entrega DATE,
                status TEXT DEFAULT 'ativa',
                data_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''' if self.usar_postgresql else '''CREATE TABLE IF NOT EXISTS atividades (
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

            # Arquivo Morto - Professores
            cursor.execute('''CREATE TABLE IF NOT EXISTS professores_mortos (
                id SERIAL PRIMARY KEY,
                professor_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                email TEXT NOT NULL,
                cpf TEXT,
                data_nascimento DATE,
                celular TEXT,
                endereco TEXT,
                foto TEXT,
                data_cadastro TIMESTAMP,
                data_exclusao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                motivo_exclusao TEXT
            )''' if self.usar_postgresql else '''CREATE TABLE IF NOT EXISTS professores_mortos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                professor_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                email TEXT NOT NULL,
                cpf TEXT,
                data_nascimento DATE,
                celular TEXT,
                endereco TEXT,
                foto TEXT,
                data_cadastro DATETIME,
                data_exclusao DATETIME DEFAULT CURRENT_TIMESTAMP,
                motivo_exclusao TEXT
            )''')

            # Arquivo Morto - Alunos
            cursor.execute('''CREATE TABLE IF NOT EXISTS alunos_mortos (
                id SERIAL PRIMARY KEY,
                aluno_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                email TEXT,
                matricula TEXT NOT NULL,
                cpf TEXT,
                cpf_responsavel TEXT,
                endereco TEXT,
                serie_id INTEGER,
                data_nascimento DATE,
                responsavel TEXT,
                telefone TEXT,
                data_cadastro TIMESTAMP,
                data_exclusao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                motivo_exclusao TEXT
            )''' if self.usar_postgresql else '''CREATE TABLE IF NOT EXISTS alunos_mortos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aluno_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                email TEXT,
                matricula TEXT NOT NULL,
                cpf TEXT,
                cpf_responsavel TEXT,
                endereco TEXT,
                serie_id INTEGER,
                data_nascimento DATE,
                responsavel TEXT,
                telefone TEXT,
                data_cadastro DATETIME,
                data_exclusao DATETIME DEFAULT CURRENT_TIMESTAMP,
                motivo_exclusao TEXT
            )''')

            # Criar índices
            if self.usar_postgresql:
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_alunos_serie ON alunos(serie_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_frequencia_aluno ON frequencia(aluno_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_notas_aluno ON notas(aluno_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_notas_professor ON notas(professor_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_prof_disciplina ON professor_disciplina(professor_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_prof_serie ON professor_serie(professor_id)')
            else:
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_alunos_serie ON alunos(serie_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_frequencia_aluno ON frequencia(aluno_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_notas_aluno ON notas(aluno_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_notas_professor ON notas(professor_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_prof_disciplina ON professor_disciplina(professor_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_prof_serie ON professor_serie(professor_id)')

            conn.commit()
            print("✓ Banco de dados criado com sucesso!")

        except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao criar banco de dados: {e}")
            raise
        finally:
            conn.close()

    # ===== OPERAÇÕES COM PROFESSORES =====

    def adicionar_professor(self, nome: str, email: str, senha: str, cpf: str = '', 
                           data_nascimento: str = '', celular: str = '', 
                           endereco: str = '', foto: str = '') -> Optional[int]:
        """Adiciona um novo professor"""
        conn = self.conexao()
        cursor = conn.cursor()

        try:
            senha_hash = self.hash_senha(senha)
            
            if self.usar_postgresql:
                cursor.execute('''INSERT INTO professores 
                    (nome, email, senha, cpf, data_nascimento, celular, endereco, foto)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id''',
                    (nome, email, senha_hash, cpf, data_nascimento, celular, endereco, foto))
                professor_id = cursor.fetchone()[0]
            else:
                cursor.execute('''INSERT INTO professores 
                    (nome, email, senha, cpf, data_nascimento, celular, endereco, foto)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                    (nome, email, senha_hash, cpf, data_nascimento, celular, endereco, foto))
                professor_id = cursor.lastrowid

            conn.commit()
            print(f"✓ Professor {nome} cadastrado com sucesso!")
            return professor_id

        except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao adicionar professor: {e}")
            return None
        finally:
            conn.close()

    def verificar_login_professor(self, email: str, senha: str) -> Optional[Dict]:
        """Verifica o login do professor"""
        conn = self.conexao()
        cursor = conn.cursor()

        try:
            if self.usar_postgresql:
                cursor.execute('SELECT id, nome, senha FROM professores WHERE email = %s', (email,))
            else:
                cursor.execute('SELECT id, nome, senha FROM professores WHERE email = ?', (email,))
            
            resultado = cursor.fetchone()
            
            if resultado and self.verificar_senha(senha, resultado['senha']):
                return {'id': resultado['id'], 'nome': resultado['nome']}
            return None

        except Exception as e:
            print(f"❌ Erro ao verificar login: {e}")
            return None
        finally:
            conn.close()

    def listar_professores(self) -> List[Dict]:
        """Lista todos os professores"""
        conn = self.conexao()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT * FROM professores ORDER BY nome')
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    # ===== OPERAÇÕES COM ALUNOS =====

    def gerar_matricula(self) -> Optional[str]:
        """Gera uma matrícula automática único"""
        try:
            letras = ''.join(random.choices(string.ascii_uppercase, k=3))
            numeros = ''.join(random.choices(string.digits, k=5))
            ano = datetime.now().year
            matricula = f"{letras}{numeros}/{ano}"

            conn = self.conexao()
            cursor = conn.cursor()
            
            if self.usar_postgresql:
                cursor.execute('SELECT id FROM alunos WHERE matricula = %s', (matricula,))
            else:
                cursor.execute('SELECT id FROM alunos WHERE matricula = ?', (matricula,))

            if cursor.fetchone():
                conn.close()
                return self.gerar_matricula()

            conn.close()
            return matricula

        except Exception as e:
            print(f"❌ Erro ao gerar matrícula: {e}")
            return None

    def adicionar_aluno(self, nome: str, email: str, cpf: str, cpf_responsavel: str,
                       endereco: str, senha: str, serie_id: int,
                       data_nascimento: str = '', responsavel: str = '', 
                       telefone: str = '') -> Optional[int]:
        """Adiciona um novo aluno"""
        try:
            matricula = self.gerar_matricula()
            if not matricula:
                return None

            senha_hash = self.hash_senha(senha)
            conn = self.conexao()
            cursor = conn.cursor()

            if self.usar_postgresql:
                cursor.execute('''INSERT INTO alunos 
                    (nome, email, matricula, cpf, cpf_responsavel, endereco, senha, 
                     serie_id, data_nascimento, responsavel, telefone)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id''',
                    (nome, email, matricula, cpf, cpf_responsavel, endereco, senha_hash,
                     serie_id, data_nascimento, responsavel, telefone))
                aluno_id = cursor.fetchone()[0]
            else:
                cursor.execute('''INSERT INTO alunos 
                    (nome, email, matricula, cpf, cpf_responsavel, endereco, senha, 
                     serie_id, data_nascimento, responsavel, telefone)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (nome, email, matricula, cpf, cpf_responsavel, endereco, senha_hash,
                     serie_id, data_nascimento, responsavel, telefone))
                aluno_id = cursor.lastrowid

            conn.commit()
            print(f"✓ Aluno {nome} cadastrado! Matrícula: {matricula}")
            return aluno_id

        except Exception as e:
            print(f"❌ Erro ao adicionar aluno: {e}")
            return None
        finally:
            conn.close()

    def verificar_login_aluno(self, email: str, senha: str) -> Optional[Dict]:
        """Verifica o login do aluno"""
        conn = self.conexao()
        cursor = conn.cursor()

        try:
            if self.usar_postgresql:
                cursor.execute('''
                    SELECT a.id, a.nome, a.matricula, a.serie_id, s.nome as serie_nome, s.ano, a.senha
                    FROM alunos a JOIN series s ON a.serie_id = s.id WHERE a.email = %s
                ''', (email,))
            else:
                cursor.execute('''
                    SELECT a.id, a.nome, a.matricula, a.serie_id, s.nome as serie_nome, s.ano, a.senha
                    FROM alunos a JOIN series s ON a.serie_id = s.id WHERE a.email = ?
                ''', (email,))

            resultado = cursor.fetchone()

            if resultado and self.verificar_senha(senha, resultado['senha']):
                return {
                    'id': resultado['id'],
                    'nome': resultado['nome'],
                    'matricula': resultado['matricula'],
                    'serie_id': resultado['serie_id'],
                    'serie_nome': resultado['serie_nome'],
                    'ano': resultado['ano']
                }
            return None

        except Exception as e:
            print(f"❌ Erro ao verificar login: {e}")
            return None
        finally:
            conn.close()

    def listar_alunos(self, serie_id: Optional[int] = None) -> List[Dict]:
        """Lista alunos, opcionalmente filtrado por série"""
        conn = self.conexao()
        cursor = conn.cursor()

        try:
            if serie_id:
                if self.usar_postgresql:
                    cursor.execute('SELECT * FROM alunos WHERE serie_id = %s ORDER BY nome', (serie_id,))
                else:
                    cursor.execute('SELECT * FROM alunos WHERE serie_id = ? ORDER BY nome', (serie_id,))
            else:
                cursor.execute('SELECT * FROM alunos ORDER BY nome')

            return [dict(row) for row in cursor.fetchall()]

        finally:
            conn.close()

    # ===== OPERAÇÕES COM SÉRIES =====

    def adicionar_serie(self, nome: str, ano: int, descricao: str = '') -> Optional[int]:
        """Adiciona uma nova série"""
        conn = self.conexao()
        cursor = conn.cursor()

        try:
            if self.usar_postgresql:
                cursor.execute('''INSERT INTO series (nome, ano, descricao)
                    VALUES (%s, %s, %s) RETURNING id''', (nome, ano, descricao))
                serie_id = cursor.fetchone()[0]
            else:
                cursor.execute('''INSERT INTO series (nome, ano, descricao)
                    VALUES (?, ?, ?)''', (nome, ano, descricao))
                serie_id = cursor.lastrowid

            conn.commit()
            print(f"✓ Série {nome} cadastrada com sucesso!")
            return serie_id

        except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao adicionar série: {e}")
            return None
        finally:
            conn.close()

    def listar_series(self) -> List[Dict]:
        """Lista todas as séries"""
        conn = self.conexao()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT * FROM series ORDER BY ano, nome')
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    # ===== OPERAÇÕES COM DISCIPLINAS =====

    def adicionar_disciplina(self, nome: str, descricao: str = '') -> Optional[int]:
        """Adiciona uma nova disciplina"""
        conn = self.conexao()
        cursor = conn.cursor()

        try:
            if self.usar_postgresql:
                cursor.execute('''INSERT INTO disciplinas (nome, descricao)
                    VALUES (%s, %s) RETURNING id''', (nome, descricao))
                disciplina_id = cursor.fetchone()[0]
            else:
                cursor.execute('''INSERT INTO disciplinas (nome, descricao)
                    VALUES (?, ?)''', (nome, descricao))
                disciplina_id = cursor.lastrowid

            conn.commit()
            print(f"✓ Disciplina {nome} cadastrada com sucesso!")
            return disciplina_id

        except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao adicionar disciplina: {e}")
            return None
        finally:
            conn.close()

    def listar_disciplinas(self) -> List[Dict]:
        """Lista todas as disciplinas"""
        conn = self.conexao()
        cursor = conn.cursor()

        try:
            cursor.execute('SELECT * FROM disciplinas ORDER BY nome')
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    # ===== OPERAÇÕES COM NOTAS =====

    def registrar_nota(self, aluno_id: int, professor_id: int, disciplina: str, nota: float,
                      bimestre: int, observacao: str = '', avm: Optional[float] = None,
                      avb: Optional[float] = None, rec: Optional[float] = None) -> Optional[int]:
        """Registra uma nota para um aluno"""
        conn = self.conexao()
        cursor = conn.cursor()

        try:
            mb = None
            if avm is not None and avb is not None:
                mb = (float(avm) + float(avb)) / 2
                if mb < 6 and rec is not None:
                    maior_nota = max(float(avm), float(avb))
                    mb = (maior_nota + float(rec)) / 2
                    observacao = f"{observacao} [REC ativada]".strip()

            if nota is None and mb is not None:
                nota = mb

            if self.usar_postgresql:
                cursor.execute('''INSERT INTO notas 
                    (aluno_id, professor_id, disciplina, nota, bimestre, observacao, avm, avb, rec, mb)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id''',
                    (aluno_id, professor_id, disciplina, nota, bimestre, observacao, avm, avb, rec, mb))
                nota_id = cursor.fetchone()[0]
            else:
                cursor.execute('''INSERT INTO notas 
                    (aluno_id, professor_id, disciplina, nota, bimestre, observacao, avm, avb, rec, mb)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    (aluno_id, professor_id, disciplina, nota, bimestre, observacao, avm, avb, rec, mb))
                nota_id = cursor.lastrowid

            conn.commit()
            print(f"✓ Nota registrada para aluno ID {aluno_id} - MB: {mb}")
            return nota_id

        except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao registrar nota: {e}")
            return None
        finally:
            conn.close()

    def obter_notas_aluno(self, aluno_id: int, bimestre: Optional[int] = None) -> List[Dict]:
        """Obtém as notas de um aluno"""
        conn = self.conexao()
        cursor = conn.cursor()

        try:
            if bimestre:
                if self.usar_postgresql:
                    cursor.execute('''SELECT n.*, p.nome as professor_nome
                        FROM notas n JOIN professores p ON n.professor_id = p.id
                        WHERE n.aluno_id = %s AND n.bimestre = %s ORDER BY n.disciplina''',
                        (aluno_id, bimestre))
                else:
                    cursor.execute('''SELECT n.*, p.nome as professor_nome
                        FROM notas n JOIN professores p ON n.professor_id = p.id
                        WHERE n.aluno_id = ? AND n.bimestre = ? ORDER BY n.disciplina''',
                        (aluno_id, bimestre))
            else:
                if self.usar_postgresql:
                    cursor.execute('''SELECT n.*, p.nome as professor_nome
                        FROM notas n JOIN professores p ON n.professor_id = p.id
                        WHERE n.aluno_id = %s ORDER BY n.bimestre, n.disciplina''', (aluno_id,))
                else:
                    cursor.execute('''SELECT n.*, p.nome as professor_nome
                        FROM notas n JOIN professores p ON n.professor_id = p.id
                        WHERE n.aluno_id = ? ORDER BY n.bimestre, n.disciplina''', (aluno_id,))

            return [dict(row) for row in cursor.fetchall()]

        finally:
            conn.close()

    # ===== OPERAÇÕES COM FREQUÊNCIA =====

    def registrar_frequencia(self, aluno_id: int, data: str, presente: bool, 
                           observacao: str = '') -> Optional[int]:
        """Registra ou atualiza a frequência de um aluno"""
        conn = self.conexao()
        cursor = conn.cursor()

        try:
            if self.usar_postgresql:
                cursor.execute('SELECT id FROM frequencia WHERE aluno_id = %s AND data = %s',
                             (aluno_id, data))
            else:
                cursor.execute('SELECT id FROM frequencia WHERE aluno_id = ? AND data = ?',
                             (aluno_id, data))

            resultado = cursor.fetchone()

            if resultado:
                if self.usar_postgresql:
                    cursor.execute('''UPDATE frequencia SET presente = %s, observacao = %s
                        WHERE aluno_id = %s AND data = %s''',
                        (presente, observacao, aluno_id, data))
                else:
                    cursor.execute('''UPDATE frequencia SET presente = ?, observacao = ?
                        WHERE aluno_id = ? AND data = ?''',
                        (presente, observacao, aluno_id, data))
                conn.commit()
                print(f"✓ Frequência atualizada para aluno ID {aluno_id} em {data}")
                return resultado[0] if isinstance(resultado, tuple) else resultado['id']
            else:
                if self.usar_postgresql:
                    cursor.execute('''INSERT INTO frequencia (aluno_id, data, presente, observacao)
                        VALUES (%s, %s, %s, %s) RETURNING id''',
                        (aluno_id, data, presente, observacao))
                    freq_id = cursor.fetchone()[0]
                else:
                    cursor.execute('''INSERT INTO frequencia (aluno_id, data, presente, observacao)
                        VALUES (?, ?, ?, ?)''',
                        (aluno_id, data, presente, observacao))
                    freq_id = cursor.lastrowid

                conn.commit()
                print(f"✓ Frequência registrada para aluno ID {aluno_id} em {data}")
                return freq_id

        except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao registrar frequência: {e}")
            return None
        finally:
            conn.close()

    def obter_frequencia_aluno(self, aluno_id: int, data_inicio: Optional[str] = None,
                              data_fim: Optional[str] = None) -> List[Dict]:
        """Obtém o histórico de frequência de um aluno"""
        conn = self.conexao()
        cursor = conn.cursor()

        try:
            if data_inicio and data_fim:
                if self.usar_postgresql:
                    cursor.execute('''SELECT * FROM frequencia 
                        WHERE aluno_id = %s AND data BETWEEN %s AND %s
                        ORDER BY data DESC''', (aluno_id, data_inicio, data_fim))
                else:
                    cursor.execute('''SELECT * FROM frequencia 
                        WHERE aluno_id = ? AND data BETWEEN ? AND ?
                        ORDER BY data DESC''', (aluno_id, data_inicio, data_fim))
            else:
                if self.usar_postgresql:
                    cursor.execute('SELECT * FROM frequencia WHERE aluno_id = %s ORDER BY data DESC', (aluno_id,))
                else:
                    cursor.execute('SELECT * FROM frequencia WHERE aluno_id = ? ORDER BY data DESC', (aluno_id,))

            return [dict(row) for row in cursor.fetchall()]

        finally:
            conn.close()

    # ===== OPERAÇÕES COM ATIVIDADES =====

    def criar_atividade(self, serie_id: int, professor_id: int, titulo: str,
                       descricao: str = '', data_criacao: Optional[str] = None,
                       data_entrega: Optional[str] = None) -> Optional[int]:
        """Cria uma nova atividade para uma turma"""
        conn = self.conexao()
        cursor = conn.cursor()

        if not data_criacao:
            data_criacao = datetime.now().strftime('%Y-%m-%d')

        try:
            if self.usar_postgresql:
                cursor.execute('''INSERT INTO atividades 
                    (serie_id, professor_id, titulo, descricao, data_criacao, data_entrega, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id''',
                    (serie_id, professor_id, titulo, descricao, data_criacao, data_entrega, 'ativa'))
                atividade_id = cursor.fetchone()[0]
            else:
                cursor.execute('''INSERT INTO atividades 
                    (serie_id, professor_id, titulo, descricao, data_criacao, data_entrega, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                    (serie_id, professor_id, titulo, descricao, data_criacao, data_entrega, 'ativa'))
                atividade_id = cursor.lastrowid

            conn.commit()
            return atividade_id

        except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao criar atividade: {e}")
            return None
        finally:
            conn.close()

    def obter_atividades_turma(self, serie_id: int) -> List[Dict]:
        """Obtém todas as atividades de uma turma"""
        conn = self.conexao()
        cursor = conn.cursor()

        try:
            if self.usar_postgresql:
                cursor.execute('''SELECT a.*, p.nome as professor_nome
                    FROM atividades a JOIN professores p ON a.professor_id = p.id
                    WHERE a.serie_id = %s AND a.status = 'ativa'
                    ORDER BY a.data_criacao DESC''', (serie_id,))
            else:
                cursor.execute('''SELECT a.*, p.nome as professor_nome
                    FROM atividades a JOIN professores p ON a.professor_id = p.id
                    WHERE a.serie_id = ? AND a.status = 'ativa'
                    ORDER BY a.data_criacao DESC''', (serie_id,))

            return [dict(row) for row in cursor.fetchall()]

        finally:
            conn.close()

    # ===== UTILIDADES =====

    def obter_estatisticas(self) -> Dict[str, int]:
        """Obtém estatísticas gerais do banco de dados"""
        conn = self.conexao()
        cursor = conn.cursor()

        stats = {}

        try:
            cursor.execute('SELECT COUNT(*) as total FROM professores')
            stats['total_professores'] = cursor.fetchone()['total'] if self.usar_postgresql else cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) as total FROM series')
            stats['total_series'] = cursor.fetchone()['total'] if self.usar_postgresql else cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) as total FROM alunos')
            stats['total_alunos'] = cursor.fetchone()['total'] if self.usar_postgresql else cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) as total FROM disciplinas')
            stats['total_disciplinas'] = cursor.fetchone()['total'] if self.usar_postgresql else cursor.fetchone()[0]

            return stats

        except Exception as e:
            print(f"❌ Erro ao obter estatísticas: {e}")
            return {'total_professores': 0, 'total_series': 0, 'total_alunos': 0, 'total_disciplinas': 0}
        finally:
            conn.close()


# Função para inicializar o banco de dados
def inicializar_banco():
    """Inicializa o banco de dados"""
    try:
        db = BancoDados()
        stats = db.obter_estatisticas()
        print(f"\n📊 Estatísticas do banco de dados:")
        print(f"   Professores: {stats['total_professores']}")
        print(f"   Séries: {stats['total_series']}")
        print(f"   Alunos: {stats['total_alunos']}")
        print(f"   Disciplinas: {stats['total_disciplinas']}\n")
        return db
    except Exception as e:
        print(f"❌ Erro ao inicializar banco de dados: {e}")
        raise


if __name__ == '__main__':
    inicializar_banco()
