# Sistema de Gestão Escolar - Banco de Dados

## 📋 Descrição

Sistema completo de banco de dados para gerenciamento de instituição escolar, incluindo:
- ✅ Cadastro e autenticação de professores
- ✅ Cadastro de séries/turmas
- ✅ Cadastro de alunos
- ✅ Registro de frequência de alunos
- ✅ Registro de notas de alunos
- ✅ Relatórios detalhados

## 🗄️ Estrutura do Banco de Dados

### Tabelas

#### **PROFESSORES**
- `id`: Identificador único
- `nome`: Nome completo
- `email`: Email único para login
- `senha`: Senha criptografada (SHA256)
- `disciplina`: Disciplina lecionada
- `data_cadastro`: Data do cadastro

#### **SÉRIES**
- `id`: Identificador único
- `nome`: Nome da série (ex: 1º Ano A)
- `ano`: Ano letivo
- `descricao`: Descrição da série
- `data_cadastro`: Data do cadastro

#### **ALUNOS**
- `id`: Identificador único
- `nome`: Nome completo
- `email`: Email do aluno
- `matricula`: Número de matrícula (único)
- `serie_id`: Referência à série
- `data_nascimento`: Data de nascimento
- `responsavel`: Nome do responsável
- `telefone`: Telefone de contato
- `data_cadastro`: Data do cadastro

#### **FREQUÊNCIA**
- `id`: Identificador único
- `aluno_id`: Referência ao aluno
- `data`: Data do registro
- `presente`: Boolean (1 = presente, 0 = ausente)
- `observacao`: Observações adicionais
- `data_registro`: Data do registro

#### **NOTAS**
- `id`: Identificador único
- `aluno_id`: Referência ao aluno
- `professor_id`: Referência ao professor
- `disciplina`: Nome da disciplina
- `nota`: Valor da nota (0-10)
- `bimestre`: Bimestre (1-4)
- `data_registro`: Data do registro
- `observacao`: Observações adicionais

## 🚀 Como Usar

### 1. Instalação

```bash
# Instalar dependências
pip install -r requirements.txt
```

### 2. Inicializar o Banco de Dados

```bash
# O banco de dados será criado automaticamente na primeira execução
python banco_dados.py
```

### 3. Iniciar o Servidor Flask

```bash
python app.py
```

O servidor estará disponível em: `http://localhost:5000`

## 📡 API REST - Endpoints

### Autenticação
```
POST /api/login
```
**Body:**
```json
{
  "email": "professor@email.com",
  "senha": "senha123"
}
```
**Resposta:**
```json
{
  "sucesso": true,
  "id": 1,
  "nome": "João Silva"
}
```

### Professores

#### Listar todos
```
GET /api/professores
```

#### Criar novo professor
```
POST /api/professores
```
**Body:**
```json
{
  "nome": "João Silva",
  "email": "joao@email.com",
  "senha": "senha123",
  "disciplina": "Matemática"
}
```

### Séries

#### Listar todas
```
GET /api/series
```

#### Criar nova série
```
POST /api/series
```
**Body:**
```json
{
  "nome": "1º Ano A",
  "ano": 2024,
  "descricao": "Primeira série do turno da manhã"
}
```

### Alunos

#### Listar todos (ou por série)
```
GET /api/alunos
GET /api/alunos?serie_id=1
```

#### Criar novo aluno
```
POST /api/alunos
```
**Body:**
```json
{
  "nome": "Maria Santos",
  "email": "maria@email.com",
  "matricula": "2024001",
  "serie_id": 1,
  "data_nascimento": "2010-05-15",
  "responsavel": "José Santos",
  "telefone": "(11) 98765-4321"
}
```

### Frequência

#### Registrar frequência
```
POST /api/frequencia
```
**Body:**
```json
{
  "aluno_id": 1,
  "data": "2024-04-17",
  "presente": true,
  "observacao": "Aluno bem comportado"
}
```

#### Obter frequência de um aluno
```
GET /api/frequencia/1
GET /api/frequencia/1?data_inicio=2024-04-01&data_fim=2024-04-30
```

#### Relatório de frequência por série
```
GET /api/relatorio/frequencia/1?data_inicio=2024-04-01&data_fim=2024-04-30
```

### Notas

#### Registrar nota
```
POST /api/notas
```
**Body:**
```json
{
  "aluno_id": 1,
  "professor_id": 1,
  "disciplina": "Matemática",
  "nota": 8.5,
  "bimestre": 1,
  "observacao": "Ótimo desempenho"
}
```

#### Obter notas de um aluno
```
GET /api/notas/1
GET /api/notas/1?bimestre=1
```

#### Relatório de notas por série
```
GET /api/relatorio/notas/1?bimestre=1
```

### Estatísticas

#### Obter estatísticas gerais
```
GET /api/estatisticas
```
**Resposta:**
```json
{
  "total_professores": 5,
  "total_series": 4,
  "total_alunos": 120,
  "total_registros_frequencia": 2400,
  "total_registros_notas": 480
}
```

## 💾 Exemplo de Uso com Python

```python
from banco_dados import BancoDados

# Inicializar banco de dados
db = BancoDados('escola.db')

# Cadastrar professor
db.adicionar_professor('João Silva', 'joao@email.com', 'senha123', 'Matemática')

# Cadastrar série
db.adicionar_serie('1º Ano A', 2024, 'Turma da manhã')

# Cadastrar aluno
db.adicionar_aluno('Maria Santos', 'maria@email.com', '2024001', 1, '2010-05-15', 'José Santos', '(11) 98765-4321')

# Registrar frequência
db.registrar_frequencia(1, '2024-04-17', True, 'Aluno bem comportado')

# Registrar nota
db.registrar_nota(1, 1, 'Matemática', 8.5, 1, 'Ótimo desempenho')

# Obter notas de um aluno
notas = db.obter_notas_aluno(1)
for nota in notas:
    print(f"{nota['disciplina']}: {nota['nota']}")

# Gerar relatório de frequência
relatorio = db.relatorio_frequencia_por_serie(1, '2024-04-01', '2024-04-30')
for linha in relatorio:
    print(f"{linha['nome']}: {linha['dias_presentes']} dias presentes, {linha['dias_ausentes']} ausências")

# Obter estatísticas
stats = db.obter_estatisticas()
print(f"Total de alunos: {stats['total_alunos']}")
```

## 🔐 Segurança

- Senhas de professores são criptografadas com SHA256
- Queries parametrizadas para prevenção de SQL injection
- Índices para melhor performance
- Constraints de integridade referencial

## 📊 Características

- ✅ Identificadores únicos para cada tabela
- ✅ Relacionamentos entre tabelas (Foreign Keys)
- ✅ Criptografia de senhas
- ✅ Timestamps automáticos
- ✅ Índices para performance
- ✅ Tratamento de erros
- ✅ Validação de dados

## 📝 Notas Importantes

1. O banco de dados SQLite é criado automaticamente como `escola.db`
2. Cada email de professor deve ser único
3. Cada matrícula de aluno deve ser única
4. Cada combinação de aluno + data em frequência deve ser única
5. As senhas são armazenadas criptografadas
6. Todos os timestamps são automáticos

## 🆘 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'flask'"
Solução: Execute `pip install -r requirements.txt`

### Erro: "IntegrityError: UNIQUE constraint failed"
Solução: O email/matrícula já existe. Use valores únicos.

### Erro: "FOREIGN KEY constraint failed"
Solução: Certifique-se de que o ID da série/aluno/professor existe antes de criar registros relacionados.

## 📄 Arquivos

- `banco_dados.py`: Classe BancoDados com todas as operações
- `app.py`: Servidor Flask com API REST
- `database.sql`: Script SQL para criar as tabelas
- `requirements.txt`: Dependências Python
- `README.md`: Esta documentação

---

**Desenvolvido para gerenciamento escolar completo e eficiente!**
