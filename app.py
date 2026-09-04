"""
API Flask para sistema de gestão escolar - VERSÃO SEGURA
Gerencia todas as operações do banco de dados com JWT e Bcrypt
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from banco_dados import BancoDados
from config import SECRET_KEY, JWT_SECRET_KEY, CORS_ORIGINS, JWT_ACCESS_TOKEN_EXPIRES
from datetime import datetime, timedelta
import json
import os

# ===== FERIADOS BRASILEIROS 2026 =====
FERIADOS_2026 = {
    '2026-01-01',  # Ano Novo
    '2026-02-17',  # Carnaval (terça)
    '2026-02-18',  # Quarta de Cinzas
    '2026-04-03',  # Sexta-feira Santa
    '2026-04-21',  # Tiradentes
    '2026-05-01',  # Dia do Trabalho
    '2026-09-07',  # Independência
    '2026-10-12',  # N. Sra. Aparecida
    '2026-11-02',  # Finados
    '2026-11-20',  # Consciência Negra
    '2026-11-23',  # Corpus Christi (6ª após Páscoa)
    '2026-12-25',  # Natal
}

def eh_dia_util(data_str):
    """Verifica se uma data é dia útil (seg-sex, não feriado)"""
    data = datetime.strptime(data_str, '%Y-%m-%d').date()
    
    # Verifica se é feriado
    if data_str in FERIADOS_2026:
        return False
    
    # Verifica se é fim de semana (5=sábado, 6=domingo)
    if data.weekday() >= 5:
        return False
    
    return True

def contar_dias_uteis(data_inicio_str, data_fim_str):
    """Conta dias úteis entre duas datas"""
    data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
    data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
    
    dias_uteis = 0
    data_atual = data_inicio
    
    while data_atual <= data_fim:
        if eh_dia_util(data_atual.strftime('%Y-%m-%d')):
            dias_uteis += 1
        data_atual += timedelta(days=1)
    
    return dias_uteis

app = Flask(__name__, static_folder='.', static_url_path='')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max para upload

# ===== CONFIGURAÇÕES DE SEGURANÇA =====

# CORS - Restrito a domínios específicos
cors_config = {
    'origins': CORS_ORIGINS,
    'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    'allow_headers': ['Content-Type', 'Authorization'],
    'supports_credentials': True
}
CORS(app, resources={'/api/*': cors_config})

# JWT Configuration
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=JWT_ACCESS_TOKEN_EXPIRES)
jwt = JWTManager(app)

# Inicializar banco de dados
db = BancoDados('escola.db')

# ===== ROTAS ESTÁTICAS (SERVIR HTML) =====

@app.route('/')
def index():
    """Serve a página inicial"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def servir_arquivo_estatico(filename):
    """Serve arquivos estáticos (HTML, CSS, JS, imagens)"""
    # Validar extensões permitidas
    extensoes_permitidas = ['.html', '.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.json']
    _, ext = os.path.splitext(filename)
    
    if ext.lower() not in extensoes_permitidas:
        return jsonify({'erro': 'Tipo de arquivo não permitido'}), 403
    
    try:
        return send_from_directory('.', filename)
    except FileNotFoundError:
        return jsonify({'erro': 'Arquivo não encontrado'}), 404

@app.route('/fotos_alunos/<filename>')
def servir_foto(filename):
    """Serve as fotos dos alunos"""
    try:
        return send_from_directory('fotos_alunos', filename)
    except:
        return jsonify({'erro': 'Foto não encontrada'}), 404

# ===== ROTAS DE AUTENTICAÇÃO (SEM JWT_REQUIRED) =====

@app.route('/api/login', methods=['POST'])
def login():
    """Login de professor ou aluno - Retorna JWT Token"""
    try:
        data = request.get_json(silent=True) or {}
        email = data.get('email', '').strip()
        matricula = data.get('matricula', '').strip()
        senha = data.get('senha', '').strip()
        tipo_usuario = data.get('tipo_usuario', '').strip().lower()
        
        if not senha:
            return jsonify({'erro': 'Senha é obrigatória'}), 400
        
        if not tipo_usuario:
            return jsonify({'erro': 'Tipo de usuário não informado'}), 400
        
        # Validar tipo de usuário - normalizar para minúsculas
        tipos_validos = ['professor', 'aluno', 'administrador', 'admin']
        if tipo_usuario not in tipos_validos:
            return jsonify({'erro': f'Tipo de usuário inválido: {tipo_usuario}'}), 400
        
        # Normalizar 'admin' para 'administrador'
        if tipo_usuario == 'admin':
            tipo_usuario = 'administrador'
        
        if tipo_usuario == 'administrador':
            # Login de administrador
            if not email:
                return jsonify({'erro': 'Email é obrigatório para administrador'}), 400
            if email == 'admin@escola.com' and senha == 'Admin2026':
                access_token = create_access_token(
                    identity='0',
                    additional_claims={'tipo': 'administrador', 'id': 0, 'nome': 'Administrador', 'email': email}
                )
                return jsonify({
                    'sucesso': True,
                    'access_token': access_token,
                    'id': 0,
                    'nome': 'Administrador',
                    'tipo': 'administrador'
                }), 200
            else:
                return jsonify({'erro': 'Credenciais de admin inválidas'}), 401
        
        elif tipo_usuario == 'aluno':
            # Login de aluno - pode usar email OU matrícula
            if matricula:
                # Login com matrícula
                resultado = db.verificar_login_aluno_por_matricula(matricula, senha)
            elif email:
                # Login com email
                resultado = db.verificar_login_aluno(email, senha)
            else:
                return jsonify({'erro': 'Email ou matrícula são obrigatórios'}), 400
            
            if resultado:
                access_token = create_access_token(
                    identity=str(resultado['id']),
                    additional_claims={
                        'tipo': 'aluno',
                        'nome': resultado['nome'],
                        'serie_id': resultado['serie_id']
                    }
                )
                return jsonify({
                    'sucesso': True,
                    'access_token': access_token,
                    'id': resultado['id'],
                    'nome': resultado['nome'],
                    'matricula': resultado['matricula'],
                    'serie_id': resultado['serie_id'],
                    'serie_nome': resultado['serie_nome'],
                    'tipo': 'aluno'
                }), 200
            else:
                return jsonify({'erro': 'Matrícula/Email ou senha incorretos'}), 401
        
        else:  # professor
            # Login de professor
            if not email:
                return jsonify({'erro': 'Email é obrigatório para professor'}), 400
            resultado = db.verificar_login_professor_com_turmas(email, senha)
            if resultado:
                access_token = create_access_token(
                    identity=str(resultado['id']),
                    additional_claims={
                        'tipo': 'professor',
                        'nome': resultado['nome'],
                        'turmas': [t['id'] for t in resultado['turmas']]
                    }
                )
                return jsonify({
                    'sucesso': True,
                    'access_token': access_token,
                    'id': resultado['id'],
                    'nome': resultado['nome'],
                    'turmas': resultado['turmas'],
                    'tipo': 'professor'
                }), 200
            else:
                return jsonify({'erro': 'Email ou senha incorretos'}), 401
    
    except Exception as e:
        print(f"Erro no login: {e}")
        return jsonify({'erro': 'Erro ao processar login'}), 500

@app.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout do usuário (token JWT é invalidado no cliente)"""
    return jsonify({'mensagem': 'Logout realizado com sucesso'}), 200

# ===== ROTAS DE VALIDAÇÃO =====

@app.route('/api/validar-token', methods=['GET'])
@jwt_required()
def validar_token():
    """Valida se o token JWT é válido"""
    try:
        user_id = get_jwt_identity()
        return jsonify({
            'valido': True,
            'user_id': user_id
        }), 200
    except Exception as e:
        return jsonify({'valido': False, 'erro': str(e)}), 401

@app.route('/api/validar-acesso-turma', methods=['POST'])
@jwt_required()
def validar_acesso_turma():
    """Valida se um professor ou aluno pode acessar uma turma específica"""
    try:
        from flask_jwt_extended import get_jwt
        
        data = request.json
        user_id = int(get_jwt_identity())
        jwt_claims = get_jwt()
        user_type = jwt_claims.get('tipo', 'professor')  # Default para professor se tipo não estiver presente
        
        serie_id = data.get('serie_id')
        
        if not serie_id:
            return jsonify({'erro': 'Série ID é obrigatório'}), 400
        
        try:
            serie_id = int(serie_id)
        except (ValueError, TypeError):
            return jsonify({'erro': 'Série ID deve ser um número'}), 400
        
        # Verificar acesso baseado no tipo de usuário
        if user_type == 'aluno':
            pode_acessar = db.aluno_pode_acessar_turma(user_id, serie_id)
        else:  # professor
            pode_acessar = db.professor_pode_acessar_turma(user_id, serie_id)
        
        if not pode_acessar:
            return jsonify({'erro': 'Acesso negado a esta turma'}), 403
        
        return jsonify({
            'user_id': user_id,
            'user_type': user_type,
            'serie_id': serie_id,
            'pode_acessar': pode_acessar
        }), 200
    
    except Exception as e:
        return jsonify({'erro': 'Erro ao validar acesso'}), 500

# ===== ROTAS DE PROFESSORES =====

@app.route('/api/professores', methods=['GET'])
@jwt_required()
def listar_professores():
    """Lista todos os professores (apenas admin)"""
    try:
        user_id = get_jwt_identity()
        
        # Validar permissão
        if not db.usuario_eh_admin(user_id):
            return jsonify({'erro': 'Acesso negado'}), 403
        
        professores = db.listar_professores()
        return jsonify([dict(p) for p in professores]), 200
    
    except Exception as e:
        return jsonify({'erro': 'Erro ao listar professores'}), 500

@app.route('/api/professores/<int:professor_id>', methods=['GET'])
@jwt_required()
def obter_professor(professor_id):
    """Obtém um professor específico por ID"""
    try:
        user_id = get_jwt_identity()
        user_id = int(user_id)
        
        # Professor pode ver seus próprios dados
        # Admin pode ver qualquer um
        if user_id != professor_id and not db.usuario_eh_admin(str(user_id)):
            return jsonify({'erro': 'Acesso negado'}), 403
        
        professor = db.obter_professor_por_id(professor_id)
        if professor:
            return jsonify(dict(professor)), 200
        else:
            return jsonify({'erro': 'Professor não encontrado'}), 404
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/professores/<int:professor_id>/series', methods=['GET'])
@jwt_required()
def obter_series_professor(professor_id):
    """Obtém as séries/turmas de um professor"""
    try:
        user_id = int(get_jwt_identity())
        
        # Professor pode ver apenas suas turmas, admin pode ver todas
        if user_id != professor_id and not db.usuario_eh_admin(str(user_id)):
            return jsonify({'erro': 'Acesso negado'}), 403
        
        series = db.obter_series_professor(professor_id)
        return jsonify([dict(s) for s in series]), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/professores/<int:professor_id>/series/<int:serie_id>', methods=['POST'])
@jwt_required()
def adicionar_turma_professor(professor_id, serie_id):
    """Associa uma turma a um professor (apenas admin)"""
    try:
        user_id = int(get_jwt_identity())
        
        # Apenas admin pode adicionar turmas
        if not db.usuario_eh_admin(str(user_id)):
            return jsonify({'erro': 'Apenas administradores podem associar turmas'}), 403
        
        # Verificar se professor existe
        prof = db.obter_professor_por_id(professor_id)
        if not prof:
            return jsonify({'erro': 'Professor não encontrado'}), 404
        
        # Verificar se série existe
        serie = db.obter_serie_por_id(serie_id)
        if not serie:
            return jsonify({'erro': 'Série não encontrada'}), 404
        
        # Adicionar associação
        db.adicionar_serie_professor(professor_id, serie_id)
        
        return jsonify({'sucesso': True, 'mensagem': 'Turma adicionada com sucesso'}), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/professores/<int:professor_id>/series/<int:serie_id>', methods=['DELETE'])
@jwt_required()
def remover_turma_professor(professor_id, serie_id):
    """Remove uma turma de um professor (apenas admin)"""
    try:
        user_id = int(get_jwt_identity())
        
        # Apenas admin pode remover turmas
        if not db.usuario_eh_admin(str(user_id)):
            return jsonify({'erro': 'Apenas administradores podem remover turmas'}), 403
        
        # Remover associação
        db.remover_serie_professor(professor_id, serie_id)
        
        return jsonify({'sucesso': True, 'mensagem': 'Turma removida com sucesso'}), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/professores', methods=['POST'])
@jwt_required()
def criar_professor():
    """Cria um novo professor (apenas admin)"""
    try:
        user_id = int(get_jwt_identity())
        
        # Validar permissão (apenas admin)
        if not db.usuario_eh_admin(str(user_id)):
            return jsonify({'erro': 'Apenas administradores podem criar professores'}), 403
        
        data = request.json
        
        nome = data.get('nome', '').strip()
        email = data.get('email', '').strip()
        senha = data.get('senha', '').strip()
        cpf = data.get('cpf', '').strip()
        data_nascimento = data.get('data_nascimento', '').strip()
        celular = data.get('celular', '').strip()
        endereco = data.get('endereco', '').strip()
        foto = data.get('foto', '').strip()
        disciplinas = data.get('disciplinas', [])
        series = data.get('series', [])
        
        if not all([nome, email, senha]):
            return jsonify({'erro': 'Nome, email e senha são obrigatórios'}), 400
        
        # Adicionar professor
        id_novo = db.adicionar_professor(nome, email, senha, cpf, data_nascimento, celular, endereco, foto)
        
        if id_novo:
            # Associar disciplinas
            for disc_id in disciplinas:
                db.adicionar_disciplina_professor(id_novo, disc_id)
            
            # Associar séries
            for serie_id in series:
                db.adicionar_serie_professor(id_novo, serie_id)
            
            return jsonify({
                'sucesso': True,
                'id': id_novo,
                'mensagem': f'Professor {nome} cadastrado com sucesso'
            }), 201
        else:
            return jsonify({'erro': 'Email já cadastrado ou erro ao cadastrar'}), 400
    
    except Exception as e:
        return jsonify({'erro': f'Erro ao criar professor: {str(e)}'}), 500

@app.route('/api/professores/<int:professor_id>', methods=['PUT'])
@jwt_required()
def editar_professor(professor_id):
    """Edita dados de um professor"""
    try:
        user_id = int(get_jwt_identity())
        
        # Professor pode editar apenas seus próprios dados, admin pode editar qualquer um
        if user_id != professor_id and not db.usuario_eh_admin(str(user_id)):
            return jsonify({'erro': 'Acesso negado'}), 403
        
        data = request.get_json(silent=True) or {}
        
        resultado = db.atualizar_professor(
            professor_id,
            nome=data.get('nome'),
            email=data.get('email'),
            cpf=data.get('cpf'),
            data_nascimento=data.get('data_nascimento'),
            celular=data.get('celular'),
            endereco=data.get('endereco'),
            foto=data.get('foto'),
            senha=data.get('senha')
        )
        
        if resultado:
            return jsonify({'sucesso': True, 'mensagem': 'Professor atualizado com sucesso'}), 200
        else:
            return jsonify({'erro': 'Erro ao atualizar professor'}), 400
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/professores/<int:professor_id>', methods=['DELETE'])
@jwt_required()
def deletar_professor(professor_id):
    """Deleta um professor (apenas admin)"""
    try:
        user_id = int(get_jwt_identity())
        
        # Apenas admin pode deletar
        if not db.usuario_eh_admin(str(user_id)):
            return jsonify({'erro': 'Apenas administradores podem deletar professores'}), 403
        
        if db.excluir_professor(professor_id):
            return jsonify({'sucesso': True, 'mensagem': 'Professor deletado com sucesso'}), 200
        else:
            return jsonify({'erro': 'Erro ao deletar professor ou professor não encontrado'}), 400
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# ===== ROTAS DE DISCIPLINAS =====

@app.route('/api/disciplinas', methods=['GET'])
@jwt_required()
def listar_disciplinas():
    """Lista todas as disciplinas"""
    try:
        disciplinas = db.listar_disciplinas()
        return jsonify([dict(d) for d in disciplinas]), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/disciplinas', methods=['POST'])
@jwt_required()
def criar_disciplina():
    """Cria uma nova disciplina (apenas admin)"""
    try:
        user_id = int(get_jwt_identity())
        
        if not db.usuario_eh_admin(str(user_id)):
            return jsonify({'erro': 'Apenas administradores podem criar disciplinas'}), 403
        
        data = request.json
        
        nome = data.get('nome', '').strip()
        descricao = data.get('descricao', '').strip()
        
        if not nome:
            return jsonify({'erro': 'Nome da disciplina é obrigatório'}), 400
        
        id_novo = db.adicionar_disciplina(nome, descricao)
        
        if id_novo:
            return jsonify({
                'sucesso': True,
                'id': id_novo,
                'mensagem': f'Disciplina {nome} cadastrada com sucesso'
            }), 201
        else:
            return jsonify({'erro': 'Erro ao cadastrar disciplina'}), 400
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/disciplinas/<int:disciplina_id>', methods=['PUT'])
@jwt_required()
def editar_disciplina(disciplina_id):
    """Edita dados de uma disciplina (apenas admin)"""
    try:
        user_id = int(get_jwt_identity())
        
        if not db.usuario_eh_admin(str(user_id)):
            return jsonify({'erro': 'Apenas administradores podem editar disciplinas'}), 403
        
        data = request.json
        
        resultado = db.editar_disciplina(
            disciplina_id,
            nome=data.get('nome'),
            descricao=data.get('descricao')
        )
        
        if resultado:
            return jsonify({'sucesso': True, 'mensagem': 'Disciplina atualizada com sucesso'}), 200
        else:
            return jsonify({'erro': 'Erro ao atualizar disciplina'}), 400
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/disciplinas/<int:disciplina_id>', methods=['DELETE'])
@jwt_required()
def deletar_disciplina(disciplina_id):
    """Deleta uma disciplina (apenas admin)"""
    try:
        user_id = int(get_jwt_identity())
        
        if not db.usuario_eh_admin(str(user_id)):
            return jsonify({'erro': 'Apenas administradores podem deletar disciplinas'}), 403
        
        if db.excluir_disciplina(disciplina_id):
            return jsonify({'sucesso': True, 'mensagem': 'Disciplina deletada com sucesso'}), 200
        else:
            return jsonify({'erro': 'Erro ao deletar disciplina'}), 400
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# ===== ROTAS DE SÉRIES =====

@app.route('/api/series', methods=['GET'])
def listar_series():
    """Lista todas as séries (público - sem autenticação)"""
    try:
        series = db.listar_series()
        return jsonify([dict(s) for s in series]), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/series', methods=['POST'])
@jwt_required()
def criar_serie():
    """Cria uma nova série (apenas admin)"""
    try:
        user_id = int(get_jwt_identity())
        
        if not db.usuario_eh_admin(str(user_id)):
            return jsonify({'erro': 'Apenas administradores podem criar séries'}), 403
        
        data = request.json
        
        nome = data.get('nome', '').strip()
        ano = data.get('ano')
        descricao = data.get('descricao', '').strip()
        
        if not nome or ano is None:
            return jsonify({'erro': 'Nome e ano são obrigatórios'}), 400
        
        try:
            ano = int(ano)
        except (ValueError, TypeError):
            return jsonify({'erro': 'Ano deve ser um número válido'}), 400
        
        id_novo = db.adicionar_serie(nome, ano, descricao)
        
        if id_novo:
            return jsonify({
                'sucesso': True,
                'id': id_novo,
                'mensagem': f'Série {nome} cadastrada com sucesso'
            }), 201
        else:
            return jsonify({'erro': 'Erro ao cadastrar série'}), 400
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/series/<int:serie_id>', methods=['PUT'])
@jwt_required()
def editar_serie(serie_id):
    """Edita dados de uma série (apenas admin)"""
    try:
        user_id = int(get_jwt_identity())
        
        if not db.usuario_eh_admin(str(user_id)):
            return jsonify({'erro': 'Apenas administradores podem editar séries'}), 403
        
        data = request.json
        
        resultado = db.editar_serie(
            serie_id,
            nome=data.get('nome'),
            ano=data.get('ano'),
            descricao=data.get('descricao')
        )
        
        if resultado:
            return jsonify({'sucesso': True, 'mensagem': 'Série atualizada com sucesso'}), 200
        else:
            return jsonify({'erro': 'Erro ao atualizar série'}), 400
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/series/<int:serie_id>', methods=['DELETE'])
@jwt_required()
def deletar_serie(serie_id):
    """Deleta uma série (apenas admin)"""
    try:
        user_id = int(get_jwt_identity())
        
        if not db.usuario_eh_admin(str(user_id)):
            return jsonify({'erro': 'Apenas administradores podem deletar séries'}), 403
        
        if db.excluir_serie(serie_id):
            return jsonify({'sucesso': True, 'mensagem': 'Série deletada com sucesso'}), 200
        else:
            return jsonify({'erro': 'Série possui alunos associados e não pode ser deletada'}), 400
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# ===== ROTAS DE ALUNOS =====

@app.route('/api/alunos', methods=['GET'])
@jwt_required()
def listar_alunos():
    """Lista todos os alunos, opcionalmente filtrado por série"""
    try:
        user_id = int(get_jwt_identity())
        serie_id = request.args.get('serie_id', type=int)
        
        # Se professor, validar acesso à série
        if serie_id:
            if not db.professor_pode_acessar_turma(user_id, serie_id):
                return jsonify({'erro': 'Acesso negado a esta série'}), 403
        
        alunos = db.listar_alunos(serie_id)
        
        # Enriquecer dados dos alunos com informações da série
        alunos_enriquecidos = []
        for aluno in alunos:
            aluno_dict = dict(aluno)
            try:
                serie = db.conexao().execute('SELECT nome FROM series WHERE id = ?', (aluno['serie_id'],)).fetchone()
                aluno_dict['serie_nome'] = serie['nome'] if serie else '-'
            except:
                aluno_dict['serie_nome'] = '-'
            alunos_enriquecidos.append(aluno_dict)
        
        return jsonify(alunos_enriquecidos), 200
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/alunos/<int:aluno_id>', methods=['GET'])
@jwt_required()
def obter_aluno(aluno_id):
    """Obtém um aluno específico por ID"""
    try:
        aluno = db.obter_aluno_por_id(aluno_id)
        if aluno:
            aluno_dict = dict(aluno)
            try:
                serie = db.conexao().execute('SELECT nome FROM series WHERE id = ?', (aluno['serie_id'],)).fetchone()
                aluno_dict['serie_nome'] = serie['nome'] if serie else '-'
            except:
                aluno_dict['serie_nome'] = '-'
            return jsonify(aluno_dict), 200
        else:
            return jsonify({'erro': 'Aluno não encontrado'}), 404
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/alunos', methods=['POST'])
@jwt_required()
def criar_aluno():
    """Cria um novo aluno"""
    try:
        import base64
        
        user_id = int(get_jwt_identity())
        
        # Validar permissão
        if not db.usuario_eh_admin(str(user_id)):
            return jsonify({'erro': 'Apenas administradores podem criar alunos'}), 403
        
        data = request.json
        
        nome = data.get('nome', '').strip()
        email = data.get('email', '').strip()
        cpf = data.get('cpf', '').strip()
        cpf_responsavel = data.get('cpf_responsavel', '').strip()
        endereco = data.get('endereco', '').strip()
        senha = data.get('senha', '').strip()
        serie_id = data.get('serie_id')
        data_nascimento = data.get('data_nascimento', '').strip()
        responsavel = data.get('responsavel', '').strip()
        telefone = data.get('telefone', '').strip()
        foto_base64 = data.get('foto')
        
        if not all([nome, cpf, serie_id]):
            return jsonify({'erro': 'Nome, CPF e série são obrigatórios'}), 400
        
        # Processar foto se fornecida
        nome_foto = None
        if foto_base64:
            try:
                pasta_fotos = 'fotos_alunos'
                if not os.path.exists(pasta_fotos):
                    os.makedirs(pasta_fotos)
                
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                nome_arquivo = f"{cpf.replace('.', '').replace('-', '')}_{timestamp}.png"
                caminho_foto = os.path.join(pasta_fotos, nome_arquivo)
                
                if foto_base64.startswith('data:image'):
                    foto_base64 = foto_base64.split(',')[1]
                
                foto_bytes = base64.b64decode(foto_base64)
                with open(caminho_foto, 'wb') as f:
                    f.write(foto_bytes)
                
                nome_foto = nome_arquivo
            except Exception as e:
                print(f'Erro ao salvar foto: {e}')
        
        id_novo = db.adicionar_aluno(nome, email, cpf, cpf_responsavel, endereco, senha, serie_id, 
                                      data_nascimento, responsavel, telefone, nome_foto)
        
        if id_novo:
            cursor = db.conexao().cursor()
            cursor.execute('SELECT matricula FROM alunos WHERE id = ?', (id_novo,))
            aluno = cursor.fetchone()
            matricula = aluno['matricula'] if aluno else None
            
            return jsonify({
                'sucesso': True,
                'id': id_novo,
                'matricula': matricula,
                'mensagem': f'Aluno {nome} cadastrado com sucesso. Matrícula: {matricula}'
            }), 201
        else:
            return jsonify({'erro': 'Erro ao cadastrar aluno'}), 400
    
    except Exception as e:
        return jsonify({'erro': f'Erro ao criar aluno: {str(e)}'}), 500

@app.route('/api/alunos/<int:aluno_id>', methods=['PUT'])
@jwt_required()
def editar_aluno(aluno_id):
    """Edita dados de um aluno"""
    try:
        user_id = int(get_jwt_identity())
        
        # Validar permissão - apenas admin pode editar
        if not db.usuario_eh_admin(str(user_id)):
            return jsonify({'erro': 'Apenas administradores podem editar alunos'}), 403
        
        data = request.get_json(silent=True) or {}
        
        resultado = db.atualizar_aluno(
            aluno_id,
            nome=data.get('nome'),
            email=data.get('email'),
            cpf=data.get('cpf'),
            cpf_responsavel=data.get('cpf_responsavel'),
            endereco=data.get('endereco'),
            serie_id=data.get('serie_id'),
            data_nascimento=data.get('data_nascimento'),
            responsavel=data.get('responsavel'),
            telefone=data.get('telefone')
        )
        
        if resultado:
            return jsonify({'sucesso': True, 'mensagem': 'Aluno atualizado com sucesso'}), 200
        else:
            return jsonify({'erro': 'Erro ao atualizar aluno ou nenhum campo foi alterado'}), 400
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/alunos/<int:aluno_id>', methods=['DELETE'])
@jwt_required()
def deletar_aluno(aluno_id):
    """Deleta um aluno (apenas admin)"""
    try:
        user_id = int(get_jwt_identity())
        
        # Validar permissão - apenas admin pode deletar
        if not db.usuario_eh_admin(str(user_id)):
            return jsonify({'erro': 'Apenas administradores podem deletar alunos'}), 403
        
        data = request.get_json(silent=True, force=True) or {}
        motivo = data.get('motivo', 'Exclusão solicitada pelo administrador')
        
        if db.excluir_aluno(aluno_id, motivo):
            return jsonify({'sucesso': True, 'mensagem': 'Aluno deletado com sucesso'}), 200
        else:
            return jsonify({'erro': 'Erro ao deletar aluno ou aluno não encontrado'}), 400
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# ===== ROTAS DE FREQUÊNCIA =====

@app.route('/api/frequencia', methods=['GET'])
@jwt_required()
def listar_frequencia():
    """Lista frequências, opcionalmente filtradas por série"""
    try:
        user_id = int(get_jwt_identity())
        serie_id = request.args.get('serie_id', type=int)
        
        if serie_id:
            # Validar acesso
            if not db.professor_pode_acessar_turma(user_id, serie_id):
                return jsonify({'erro': 'Acesso negado'}), 403
        
        if serie_id:
            conn = db.conexao()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT f.* FROM frequencia f
                JOIN alunos a ON f.aluno_id = a.id
                WHERE a.serie_id = ?
                ORDER BY f.data DESC
            ''', (serie_id,))
            frequencias = cursor.fetchall()
            conn.close()
            return jsonify([dict(f) for f in frequencias]), 200
        else:
            conn = db.conexao()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM frequencia ORDER BY data DESC')
            frequencias = cursor.fetchall()
            conn.close()
            return jsonify([dict(f) for f in frequencias]), 200
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/frequencia', methods=['POST'])
@jwt_required()
def registrar_frequencia():
    """Registra a frequência de um aluno"""
    try:
        user_id = int(get_jwt_identity())
        data = request.json
        
        aluno_id = data.get('aluno_id')
        data_freq = data.get('data')
        presente = data.get('presente', True)
        observacao = data.get('observacao', '').strip()
        
        if not aluno_id or not data_freq:
            return jsonify({'erro': 'ID do aluno e data são obrigatórios'}), 400
        
        id_novo = db.registrar_frequencia(aluno_id, data_freq, presente, observacao)
        
        if id_novo:
            return jsonify({
                'sucesso': True,
                'id': id_novo,
                'mensagem': 'Frequência registrada com sucesso'
            }), 201
        else:
            return jsonify({'erro': 'Erro ao registrar frequência'}), 400
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# ===== ROTAS DE NOTAS =====

@app.route('/api/disciplinas-turma/<int:serie_id>', methods=['GET'])
@jwt_required()
def listar_disciplinas_professor_turma(serie_id):
    """Lista as disciplinas que um professor leciona em uma turma específica"""
    try:
        professor_id = int(get_jwt_identity())
        
        # Verificar se o professor tem acesso à turma
        if not db.professor_pode_acessar_turma(professor_id, serie_id):
            return jsonify({'erro': 'Acesso negado'}), 403
        
        # Obter disciplinas do professor nessa turma
        disciplinas = db.obter_disciplinas_professor_serie(professor_id, serie_id)
        
        if not disciplinas:
            # Se não houver disciplinas específicas associadas, retornar disciplinas globais do professor
            # (para compatibilidade com dados antigos)
            disciplinas = db.obter_disciplinas_professor(professor_id)
        
        resultado = [{'id': d[0], 'nome': d[1]} for d in disciplinas]
        return jsonify(resultado), 200
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/notas', methods=['GET'])
@jwt_required()
def listar_notas():
    """Lista notas, opcionalmente filtradas por série"""
    try:
        user_id = int(get_jwt_identity())
        serie_id = request.args.get('serie_id', type=int)
        
        if serie_id:
            if not db.professor_pode_acessar_turma(user_id, serie_id):
                return jsonify({'erro': 'Acesso negado'}), 403
            
            # Obter disciplinas que o professor leciona nessa turma
            disciplinas = db.obter_disciplinas_professor_serie(user_id, serie_id)
            disciplinas_ids = [d[0] for d in disciplinas]
            
            conn = db.conexao()
            cursor = conn.cursor()
            
            # Se tem disciplinas específicas associadas, filtrar por elas
            if disciplinas_ids:
                placeholders = ','.join(['?'] * len(disciplinas_ids))
                cursor.execute(f'''
                    SELECT n.* FROM notas n
                    JOIN alunos a ON n.aluno_id = a.id
                    JOIN disciplinas d ON n.disciplina = d.nome
                    WHERE a.serie_id = ? AND d.id IN ({placeholders})
                    ORDER BY n.bimestre, d.nome, a.nome
                ''', [serie_id] + disciplinas_ids)
            else:
                # Compatibilidade: se não tem disciplinas específicas, retornar todas (comportamento antigo)
                cursor.execute('''
                    SELECT n.* FROM notas n
                    JOIN alunos a ON n.aluno_id = a.id
                    WHERE a.serie_id = ?
                    ORDER BY n.bimestre, a.nome
                ''', (serie_id,))
            
            notas = cursor.fetchall()
            conn.close()
            return jsonify([dict(n) for n in notas]), 200
        else:
            conn = db.conexao()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM notas ORDER BY bimestre, aluno_id')
            notas = cursor.fetchall()
            conn.close()
            return jsonify([dict(n) for n in notas]), 200
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@app.route('/api/notas', methods=['POST'])
@jwt_required()
def registrar_nota():
    """Registra uma nota para um aluno com AVM, AVB, REC"""
    try:
        user_id = int(get_jwt_identity())
        data = request.json
        
        aluno_id = data.get('aluno_id')
        professor_id = data.get('professor_id')
        disciplina = data.get('disciplina', '').strip()
        bimestre = data.get('bimestre')
        observacao = data.get('observacao', '').strip()
        
        # Novos campos
        avm = data.get('avm')
        avb = data.get('avb')
        rec = data.get('rec')
        nota = data.get('nota')
        
        # Validação: precisa de aluno_id, professor_id, disciplina, bimestre
        # E deve ter OU (avm e avb) OU nota
        if not all([aluno_id, professor_id, disciplina, bimestre]):
            return jsonify({'erro': 'Campos obrigatórios: aluno_id, professor_id, disciplina, bimestre'}), 400
        
        if (avm is None or avb is None) and nota is None:
            return jsonify({'erro': 'Forneça AVM e AVB, ou nota'}), 400
        
        # Converter para float se fornecido
        avm = float(avm) if avm is not None else None
        avb = float(avb) if avb is not None else None
        rec = float(rec) if rec is not None else None
        nota = float(nota) if nota is not None else None
        
        id_novo = db.registrar_nota(aluno_id, professor_id, disciplina, nota, bimestre, observacao, avm, avb, rec)
        
        if id_novo:
            return jsonify({
                'sucesso': True,
                'id': id_novo,
                'mensagem': 'Nota registrada com sucesso'
            }), 201
        else:
            return jsonify({'erro': 'Erro ao registrar nota'}), 400
    
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# ===== ROTAS DE ESTATÍSTICAS =====

@app.route('/api/estatisticas', methods=['GET'])
@jwt_required()
def obter_estatisticas():
    """Obtém estatísticas gerais"""
    try:
        stats = db.obter_estatisticas()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

# ===== TRATAMENTO DE ERROS =====

@app.errorhandler(404)
def nao_encontrado(erro):
    return jsonify({'erro': 'Rota não encontrada'}), 404

@app.errorhandler(500)
def erro_servidor(erro):
    return jsonify({'erro': 'Erro interno do servidor'}), 500

@app.errorhandler(401)
def nao_autorizado(erro):
    return jsonify({'erro': 'Não autorizado. Token JWT inválido ou expirado'}), 401

@app.errorhandler(403)
def acesso_negado(erro):
    return jsonify({'erro': 'Acesso negado'}), 403

# ===== ROTAS PARA DASHBOARD DO ALUNO =====

@app.route('/api/aluno/atividades', methods=['GET'])
@jwt_required()
def obter_atividades_aluno():
    """Retorna atividades agendadas para o aluno"""
    try:
        identity = get_jwt_identity()
        aluno_id = int(identity) if identity != '0' else None
        
        if not aluno_id or aluno_id == 0:
            return jsonify({'erro': 'Acesso não autorizado'}), 401
        
        # Buscar informações do aluno (incluindo série)
        aluno = db.obter_aluno_por_id(aluno_id)
        if not aluno:
            return jsonify({'erro': 'Aluno não encontrado'}), 404
        
        serie_id = aluno[3]  # serie_id está na posição 3
        
        # Buscar atividades para a série do aluno
        # Por enquanto, retorna lista vazia pois não temos tabela de atividades
        # TODO: Criar tabela de atividades e implementar
        atividades = []
        
        return jsonify(atividades), 200
    except Exception as e:
        print(f'Erro ao obter atividades: {str(e)}')
        return jsonify({'erro': 'Erro ao obter atividades'}), 500

@app.route('/api/aluno/frequencia', methods=['GET'])
@jwt_required()
def obter_frequencia_aluno():
    """Retorna frequência do aluno agregada por mês"""
    try:
        identity = get_jwt_identity()
        aluno_id = int(identity) if identity != '0' else None
        
        if not aluno_id or aluno_id == 0:
            return jsonify({'erro': 'Acesso não autorizado'}), 401
        
        # Verificar se aluno existe
        aluno = db.obter_aluno_por_id(aluno_id)
        if not aluno:
            return jsonify({'erro': 'Aluno não encontrado'}), 404
        
        # Buscar frequência
        frequencia = db.obter_frequencia_aluno(aluno_id)
        
        # Agrupar por mês
        frequencia_por_mes = {}
        for f in frequencia:
            data = f[2]  # f[2] é a data
            observacao = f[4]  # f[4] é a observação
            mes_ano = data[:7]  # formato YYYY-MM
            
            # Ignorar registros de SEM_AULA ou FERIADO
            if observacao and ('SEM_AULA' in observacao or 'FERIADO' in observacao):
                continue
            
            if mes_ano not in frequencia_por_mes:
                frequencia_por_mes[mes_ano] = {
                    'mes': mes_ano,
                    'dias_uteis': 0,
                    'faltas': 0,
                    'presencas': 0,
                    'percentual': 0
                }
            
            # Apenas contar se é dia útil
            if eh_dia_util(data):
                frequencia_por_mes[mes_ano]['dias_uteis'] += 1
                if f[3]:  # f[3] é presente (true/false)
                    frequencia_por_mes[mes_ano]['presencas'] += 1
                else:
                    frequencia_por_mes[mes_ano]['faltas'] += 1
        
        # Calcular percentuais
        resultado = []
        total_dias_uteis = 0
        total_faltas = 0
        
        for mes_ano in sorted(frequencia_por_mes.keys()):
            dados = frequencia_por_mes[mes_ano]
            if dados['dias_uteis'] > 0:
                dados['percentual'] = round((dados['presencas'] / dados['dias_uteis']) * 100, 1)
                total_dias_uteis += dados['dias_uteis']
                total_faltas += dados['faltas']
                resultado.append(dados)
        
        # Calcular percentual geral
        percentual_geral = 0
        if total_dias_uteis > 0:
            percentual_geral = round(((total_dias_uteis - total_faltas) / total_dias_uteis) * 100, 1)
        
        return jsonify({
            'resumo': {
                'dias_uteis_totais': total_dias_uteis,
                'faltas_totais': total_faltas,
                'percentual_geral': percentual_geral
            },
            'por_mes': resultado
        }), 200
    except Exception as e:
        print(f'Erro ao obter frequência: {str(e)}')
        return jsonify({'erro': 'Erro ao obter frequência'}), 500

@app.route('/api/aluno/notas', methods=['GET'])
@jwt_required()
def obter_notas_aluno():
    """Retorna notas do aluno com informações detalhadas"""
    try:
        identity = get_jwt_identity()
        aluno_id = int(identity) if identity != '0' else None
        
        if not aluno_id or aluno_id == 0:
            return jsonify({'erro': 'Acesso não autorizado'}), 401
        
        # Verificar se aluno existe
        aluno = db.obter_aluno_por_id(aluno_id)
        if not aluno:
            return jsonify({'erro': 'Aluno não encontrado'}), 404
        
        # Buscar notas
        notas = db.obter_notas_aluno(aluno_id)
        
        resultado = []
        for n in notas:
            # Estrutura da tupla: 0=id, 1=aluno_id, 2=professor_id, 3=disciplina, 4=nota,
            # 5=bimestre, 6=data_registro, 7=observacao, 8=avm, 9=avb, 10=rec, 11=mb, ..., professor_nome
            professor_nome = n[-1] if n[-1] else 'Não definido'
            
            resultado.append({
                'id': n[0],
                'disciplina': n[3],
                'bimestre': n[5],
                'avm': n[8],  # Avaliação Mensal
                'avb': n[9],  # Avaliação Bimestral
                'rec': n[10],  # Recuperação
                'mb': n[11],   # Média Bimestral
                'observacao': n[7],
                'professor_nome': professor_nome
            })
        
        return jsonify(resultado), 200
    except Exception as e:
        print(f'Erro ao obter notas: {str(e)}')
        return jsonify({'erro': 'Erro ao obter notas'}), 500

# ===== ROTAS DE ATIVIDADES =====

@app.route('/api/atividades', methods=['GET'])
@jwt_required()
def obter_atividades():
    """Retorna atividades de uma turma (para o aluno ver)"""
    try:
        identity = get_jwt_identity()
        aluno_id = int(identity) if identity != '0' else None
        
        if not aluno_id or aluno_id == 0:
            return jsonify({'erro': 'Acesso não autorizado'}), 401
        
        # Obter aluno e sua série
        aluno = db.obter_aluno_por_id(aluno_id)
        if not aluno:
            return jsonify({'erro': 'Aluno não encontrado'}), 404
        
        serie_id = aluno[8]  # serie_id está na posição 8 da tupla
        
        # Obter atividades da turma
        atividades = db.obter_atividades_turma(serie_id)
        
        resultado = []
        for ativ in atividades:
            resultado.append({
                'id': ativ[0],
                'titulo': ativ[3],
                'descricao': ativ[4],
                'data_criacao': ativ[5],
                'data_entrega': ativ[6],
                'professor': ativ[9]
            })
        
        return jsonify(resultado), 200
    except Exception as e:
        print(f'Erro ao obter atividades: {str(e)}')
        return jsonify({'erro': 'Erro ao obter atividades'}), 500

@app.route('/api/atividades', methods=['POST'])
@jwt_required()
def criar_atividade():
    """Cria uma nova atividade (professor)"""
    try:
        identity = get_jwt_identity()
        professor_id = int(identity) if identity != '0' else None
        
        if not professor_id or professor_id == 0:
            return jsonify({'erro': 'Acesso não autorizado'}), 401
        
        data = request.get_json(silent=True) or {}
        serie_id = data.get('serie_id')
        titulo = data.get('titulo', '').strip()
        descricao = data.get('descricao', '').strip()
        data_criacao = data.get('data_criacao')
        data_entrega = data.get('data_entrega')
        
        if not serie_id or not titulo:
            return jsonify({'erro': 'Série e título são obrigatórios'}), 400
        
        atividade_id = db.criar_atividade(serie_id, professor_id, titulo, descricao, data_criacao, data_entrega)
        
        if atividade_id:
            return jsonify({'sucesso': True, 'id': atividade_id, 'mensagem': 'Atividade criada com sucesso'}), 201
        else:
            return jsonify({'erro': 'Erro ao criar atividade'}), 500
    except Exception as e:
        print(f'Erro ao criar atividade: {str(e)}')
        return jsonify({'erro': 'Erro ao criar atividade'}), 500

@app.route('/api/atividades/<int:atividade_id>', methods=['DELETE'])
@jwt_required()
def deletar_atividade(atividade_id):
    """Deleta uma atividade (professor)"""
    try:
        identity = get_jwt_identity()
        professor_id = int(identity) if identity != '0' else None
        
        if not professor_id or professor_id == 0:
            return jsonify({'erro': 'Acesso não autorizado'}), 401
        
        if db.excluir_atividade(atividade_id):
            return jsonify({'sucesso': True, 'mensagem': 'Atividade excluída'}), 200
        else:
            return jsonify({'erro': 'Erro ao excluir atividade'}), 500
    except Exception as e:
        print(f'Erro ao excluir atividade: {str(e)}')
        return jsonify({'erro': 'Erro ao excluir atividade'}), 500

if __name__ == '__main__':
    print("Iniciando servidor Flask com JWT e Bcrypt...")
    app.run(debug=False, host='0.0.0.0', port=5000)
