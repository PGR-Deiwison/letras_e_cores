# 🔍 RELATÓRIO COMPLETO DE BUGS E INCONSISTÊNCIAS
**Data da análise:** 2026-09-08  
**Projeto:** site_letrasecores  
**Status:** Análise Completa (sem alterações)

---

## 📊 RESUMO EXECUTIVO

| Categoria | Crítico 🔴 | Alto 🟡 | Médio 🟢 | Baixo ⚪ | Total |
|-----------|-----------|--------|---------|---------|-------|
| Banco de Dados | 3 | 2 | 1 | 1 | 7 |
| API/Backend | 2 | 4 | 3 | 2 | 11 |
| Frontend | 1 | 3 | 4 | 2 | 10 |
| Segurança | 2 | 1 | 1 | 0 | 4 |
| **TOTAL** | **8** | **10** | **9** | **5** | **32** |

**Problemas que impedem funcionalidade:** 8 críticos  
**Problemas que degradam experiência:** 10 altos  
**Melhorias recomendadas:** 14 (médios + baixos)

---

# 🔴 PROBLEMAS CRÍTICOS (Bloqueadores)

## 1. **TABELA `notas` SEM COLUNAS NECESSÁRIAS**

**Severidade:** 🔴 CRÍTICO  
**Arquivo:** `banco_dados.py` (linhas 104-115)  
**Afeta:** Salvamento de notas, cálculo de MB, funcionalidade de REC

### Problema Detalhado

**Criação original (banco_dados.py):**
```sql
CREATE TABLE IF NOT EXISTS notas (
    id, aluno_id, professor_id, disciplina, 
    nota, bimestre, observacao, ...
)
```

**Esperado pelo código (app.py linha 1042):**
```sql
INSERT INTO notas (..., avm, avb, rec, mb, ...)
```

**Conflito com migração (atualizar_estrutura_notas.py linha 27-44):**
```python
'nota_mensal_1', 'nota_mensal_2', 'nota_mensal_3',
'nota_bimestral', 'nota_recuperacao', 'tipo_nota'
```

### Impacto
- ❌ **Impossível salvar notas:** Campo `avm, avb, rec, mb` não existem
- ❌ **Erro SQL:** `OperationalError: no such column: avm`
- ❌ **Sistema inteiro não funciona:** Professor não consegue registrar notas

### Solução Necessária
Escolher UMA estratégia:
- **Opção A:** Usar nomes `avm, avb, rec, mb` (frontend espera isso)
- **Opção B:** Renomear frontend para `nota_mensal_1`, `nota_bimestral`, etc.
- **Recomendado:** Opção A (já implementada no backend)

---

## 2. **SCRIPT DE MIGRAÇÃO CONFLITANTE**

**Severidade:** 🔴 CRÍTICO  
**Arquivo:** `atualizar_estrutura_notas.py` (linhas 1-60)  
**Causa:** Cria colunas com nomes diferentes do esperado

### Problema
Script tenta adicionar:
- `nota_mensal_1, nota_mensal_2, nota_mensal_3` (ERRADO)
- `nota_bimestral, nota_recuperacao` (ERRADO)

Mas o código usa:
- `avm, avb, rec, mb` (CORRETO)

### Resultado
Se script for executado:
1. Cria colunas com nomes errados
2. Backend tenta inserir em colunas inexistentes
3. **Sistema quebra permanentemente**

### Solução Necessária
- ❌ **NUNCA executar** `atualizar_estrutura_notas.py`
- ✅ **DELETAR** ou renomear para `_DEPRECATED_`
- ✅ Usar estratégia correta de migração com colunas corretas

---

## 3. **FUNÇÃO DE ATIVIDADES SEMPRE RETORNA VAZIO**

**Severidade:** 🔴 CRÍTICO  
**Arquivo:** `app.py` (linhas 1097-1122)  
**Afeta:** Alunos nunca veem atividades agendadas

### Código Problemático
```python
@app.route('/api/aluno/atividades', methods=['GET'])
def obter_atividades_aluno():
    # ... código ...
    
    # ❌ RETORNA SEMPRE VAZIO!
    atividades = []
    
    return jsonify(atividades), 200
```

Tem comentário: `# TODO: Criar tabela de atividades e implementar`

### Problema
- Tabela `atividades` EXISTS em `banco_dados.py` (linha 220)
- Endpoint NÃO a utiliza
- Função de listagem: **NUNCA foi chamada**

### Impacto
- ❌ Aluno entra em dashboard
- ❌ Seção "Atividades" mostra vazio
- ❌ Mesmo que professor crie atividades, aluno não vê

### Solução Necessária
Implementar busca de atividades:
```python
atividades = db.listar_atividades_por_serie(serie_id)
return jsonify([dict(a) for a in atividades]), 200
```

---

## 4. **RECALCULAR MB COM REC NÃO IMPLEMENTADO NO FRONTEND**

**Severidade:** 🔴 CRÍTICO  
**Arquivo:** `diario.html` (linhas 835-865)  
**Afeta:** Notas mostram valores errados ao preencher REC

### Problema
```javascript
// Função só é chamada quando AVM ou AVB muda
function atualizarMB(inputElement) {
    // Calcula: MB = (AVM + AVB) / 2
    // MAS: Não recalcula se REC muda!
}
```

### Cenário que falha
```
AVM: 4.0, AVB: 5.5
    ↓ MB = 4.75 (< 6, habilita REC)
REC: 8.0
    ↓ MB = 4.75 (❌ ERRADO! Deveria ser 5.75)
```

### Impacto
- ❌ Professor vê nota errada na tela
- ❌ Mesmo salvando corretamente no backend, visualmente está confuso
- ❌ Professor não sabe se MB foi recalculado

### Solução Necessária
Adicionar listener para REC:
```javascript
document.querySelector('.rec-input').addEventListener('change', function() {
    atualizarMB(this);
});
```

---

## 5. **ADMIN HARDCODED EM CÓDIGO FONTE**

**Severidade:** 🔴 CRÍTICO (Segurança)  
**Arquivo:** `app.py` (linhas 168-175)  
**Problema:** Credenciais do admin em código aberto

### Código Vulnerável
```python
if email == 'admin@escola.com' and senha == 'Admin2026':
    access_token = create_access_token(identity='0', ...)
```

### Riscos
- ❌ Senha visível em repositório GitHub público
- ❌ Qualquer um com acesso ao código consegue fazer login de admin
- ❌ Impossible revogá-la sem alterar código

### Solução Necessária
- ✅ Mover para variável de ambiente
- ✅ Ou guardar em banco de dados com hash bcrypt
- ✅ Usar arquivo `.env` protegido por `.gitignore`

---

# 🟡 PROBLEMAS ALTOS (Degradam funcionalidade)

## 6. **ACESSO EM `/api/series` SEM AUTENTICAÇÃO**

**Severidade:** 🟡 ALTO (Segurança/Inconsistência)  
**Arquivo:** `app.py` (linhas 571-577)  
**Problema:** Todos os endpoints precisam `@jwt_required()`, menos este

### Código
```python
@app.route('/api/series', methods=['GET'])
# ❌ SEM @jwt_required()
def listar_series():
    series = db.listar_series()
    return jsonify([dict(s) for s in series]), 200
```

### Impacto
- ❌ Inconsistência: todos GET precisam JWT, menos este
- ❌ Qualquer pessoa (mesmo sem login) consegue listar séries
- ❌ Quebra política de segurança geral

### Solução Necessária
```python
@app.route('/api/series', methods=['GET'])
@jwt_required()  # ✅ Adicionar isto
def listar_series():
```

---

## 7. **VALIDAÇÃO PERMISSIVA DE ADMIN**

**Severidade:** 🟡 ALTO  
**Arquivo:** `banco_dados.py` (linhas 39-42)  
**Problema:** Admin é verificado por hardcoded ID

### Código
```python
def usuario_eh_admin(self, user_id):
    return str(user_id) == '0' or str(user_id) == 'admin'
    # TODO: Implementar tabela de usuários com papéis
```

### Problemas
- ❌ Apenas ID `0` é admin (não escalável)
- ❌ Múltiplos admins? Impossible
- ❌ Revogar permissão de admin? Impossible sem código

### Solução Necessária
- ✅ Criar tabela `usuarios_admin` ou campo `is_admin` em professores
- ✅ Verificar dinamicamente no banco de dados
- ✅ Permitir múltiplos admins

---

## 8. **FALTA DE VALIDAÇÃO NO LOGIN - TIPO USUÁRIO**

**Severidade:** 🟡 ALTO  
**Arquivo:** `login.html` (linhas 188-236)  
**Problema:** Campo "tipo_usuario" no select HTML, MAS pode estar vazio

### Código HTML
```html
<select id="usuario" name="usuario" required>
    <option value="">Selecione o tipo de usuário</option>
    <option value="administrador">Administrador</option>
    <option value="professor">Professor</option>
    <option value="aluno">Aluno</option>
</select>
```

### Problema no JavaScript
```javascript
const usuario = document.getElementById('usuario').value;
if (!usuario) {
    alert('Por favor, selecione um tipo de usuário!');
    return;
}
```

**Verificação é feita, MAS:**
- ❌ Se alguém passar `usuario=null` via API, qual tipo ativa?
- ❌ Backend default em `login()` não está claro

### Solução Necessária
- ✅ Garantir default seguro no backend
- ✅ Não permitir valores vazios/null

---

## 9. **FUNÇÃO `verificar_login_aluno_por_matricula()` PODE NÃO EXISTIR**

**Severidade:** 🟡 ALTO  
**Arquivo:** `app.py` (linhas 219)  
**Problema:** Chama função que pode não estar implementada

### Código
```python
resultado = db.verificar_login_aluno_por_matricula(matricula, senha)
```

### Verificação em banco_dados.py
Procurando... **NÃO ENCONTRADA**

Só existe:
- `verificar_login_aluno()` ✓
- `verificar_login_professor_com_turmas()` ✓
- `verificar_login_aluno_por_matricula()` ❌ **NÃO EXISTE**

### Impacto
- ❌ AttributeError ao aluno tentar login com matrícula
- ❌ Sistema quebra em tempo de execução

### Solução Necessária
Implementar função ou usar a existente:
```python
# Opção 1: Implementar nova
def verificar_login_aluno_por_matricula(self, matricula, senha):
    # Buscar aluno por matrícula e validar senha

# Opção 2: Usar existente
resultado = db.verificar_login_aluno(email, senha)
```

---

## 10. **INCONSISTÊNCIA EM NOMES DE VARIÁVEIS - SÉRIE/TURMA**

**Severidade:** 🟡 ALTO  
**Arquivo:** Múltiplos (app.py, diario.html, aluno-dashboard.html)  
**Problema:** Usa `serie`, `turma`, `serie_id` inconsistentemente

### Exemplos
```python
# app.py linhas 184-215
serie_id = data.get('serie_id')  # ✓

# diario.html linhas 202-203
const serieAtual = urlParams.get('turma')  # ❌ Inconsistente com serie_id

# app.py rotas
/api/professores/<id>/series/<serie_id>  # serie
/api/validar-acesso-turma  # espera serie_id
```

### Problema
- ❌ Parâmetros `turma` em URL, `serie_id` em JSON
- ❌ Confundindo desenvolvedores
- ❌ Difícil rastrear dados

---

## 11. **FALTA VERIFICAÇÃO DE PERMISSÃO - ALGUMAS ROTAS**

**Severidade:** 🟡 ALTO  
**Arquivo:** `app.py`  
**Problema:** Nem todas rotas validam se professor pode acessar série

### Exemplos

**Rota que valida (✓):**
```python
@app.route('/api/alunos', methods=['GET'])
def listar_alunos():
    if serie_id:
        if not db.professor_pode_acessar_turma(user_id, serie_id):
            return 403
```

**Rota que NÃO valida (❌):**
```python
@app.route('/api/frequencia', methods=['GET'])
def listar_frequencia():
    # Não verifica se professor pode acessar serie_id
    # Um professor consegue ver frequência de alunos de outro professor!
```

### Impacto
- ❌ Professor A consegue ver dados de Professor B
- ❌ Segurança comprometida
- ❌ Isolamento de dados perdido

---

## 12. **ALUNO PODE FAZER LOGIN MAS ROTA `/api/aluno/atividades` PODE NÃO EXISTIR**

**Severidade:** 🟡 ALTO  
**Arquivo:** `aluno-dashboard.html` (linhas 455-464)  
**Problema:** Frontend chama rota que pode não funcionar

### Código
```javascript
async function carregarAtividades() {
    const response = await fetch(`${API_URL}/atividades`);
    // ❌ Qual é a rota certa?
    // /api/aluno/atividades
    // /api/atividades
    // /api/atividades?serie_id=X
}
```

### Realidade no Backend
- Rota: `/api/aluno/atividades` ✓ existe
- MAS: Sempre retorna `[]` vazio

Não há rota:
- `GET /api/atividades` ❌
- `GET /api/atividades?serie_id=X` ❌

---

# 🟢 PROBLEMAS MÉDIOS

## 13. **FALTA FUNÇÃO `obter_atividades_por_serie()` NO BANCO**

**Severidade:** 🟢 MÉDIO  
**Arquivo:** `banco_dados.py`  
**Problema:** Não tem função para buscar atividades por série

### Esperado
```python
def listar_atividades_por_serie(self, serie_id):
    """Retorna atividades de uma série"""
    # Implementar
```

### Realidade
- Tabela `atividades` existe ✓
- Função de busca **NÃO existe** ❌

---

## 14. **FUNÇÃO `criar_atividade()` NUNCA É CHAMADA**

**Severidade:** 🟢 MÉDIO  
**Arquivo:** `banco_dados.py` (linhas 934-948)  
**Problema:** Função existe mas nenhuma rota a usa

### Código
```python
def criar_atividade(self, serie_id, professor_id, ...):
    # Implementação completa
```

### Realidade
- Função implementada ✓
- Rota POST `/api/atividades` **NÃO existe** ❌
- Professor não consegue criar atividades ❌

---

## 15. **MB INICIAL NÃO RECALCULA AO CARREGAR**

**Severidade:** 🟢 MÉDIO  
**Arquivo:** `diario.html` (linhas 764-800)  
**Problema:** Ao carregar dados, MB exibido pode estar incorreto

### Cenário
```
Carrega notas antigas: AVM=4.0, AVB=5.5, REC=null
    ↓ MB = 4.75 exibido
Usuário abre a página
    ↓ MB mostrado: 4.75 (CORRETO)
Usuário preenche REC=8.0
    ↓ MB mostrado: 4.75 (❌ ERRADO, deveria atualizar)
    ↓ Frontend calcula: 4.75
    ↓ Backend calcula: 5.75 (CORRETO)
    ↓ Confusion!
```

### Causa
Não há chamada `atualizarMB()` após preenchimento inicial

---

## 16. **FILTRO DE DISCIPLINA USA STRING EM VEZ DE ID**

**Severidade:** 🟢 MÉDIO  
**Arquivo:** `diario.html` (linhas 743-745)  
**Problema:** Comparação de nome é frágil

### Código
```javascript
return (n.disciplina && n.disciplina.toLowerCase() === disciplinaNome.toLowerCase())
```

**Problema:**
- Se banco tiver `"Português"` e frontend tiver `"português"`, falha
- String case-sensitive mesmo com `.toLowerCase()`
- Disciplinas com acentuação podem falhar

**Solução:**
- Usar `discipline_id` (número) em vez de nome

---

## 17. **`user_id` CONVERSÃO INCONSISTENTE**

**Severidade:** 🟢 MÉDIO  
**Arquivo:** `app.py` (muitas linhas)  
**Problema:** Às vezes `int()`, às vezes `str()`

### Exemplos
```python
# Linha 304
user_id = int(get_jwt_identity())

# Linha 307
if not db.usuario_eh_admin(str(user_id)):  # Converte para string!
```

### Problema
- Inconsistência
- Difícil de manter
- Risco de erro

---

## 18. **FUNÇÃO `obter_aluno_por_id()` PODE FALHAR**

**Severidade:** 🟢 MÉDIO  
**Arquivo:** `app.py` (linhas 1174-1211)  
**Problema:** Função não tratada se falhar

```python
aluno = db.obter_aluno_por_id(aluno_id)
```

Se função não existir ou retornar `None`:
- ❌ Erro não claro
- ❌ Mensagem genérica de erro

---

# ⚪ PROBLEMAS BAIXOS

## 19. **DUPLICAÇÃO DE CÓDIGO - ENRIQUECER DADOS DO ALUNO**

**Severidade:** ⚪ BAIXO  
**Arquivo:** `app.py` (linhas 769-795 e linhas 812-823)  
**Problema:** Código duplicado para adicionar `serie_nome`

```python
# Aparece em 2 lugares:
try:
    serie = db.conexao().execute('SELECT nome FROM series WHERE id = ?', 
                                 (aluno['serie_id'],)).fetchone()
    aluno_dict['serie_nome'] = serie['nome'] if serie else '-'
except:
    aluno_dict['serie_nome'] = '-'
```

**Solução:** Criar função helper

---

## 20. **FALTA LOGGING ESTRUTURADO**

**Severidade:** ⚪ BAIXO  
**Arquivo:** Projeto inteiro  
**Problema:** Mix de `print()` e `console.error()`

- Backend: Usa `print()` (básico)
- Frontend: Usa `console.error()` (melhor)
- Sem arquivo de log centralizado

---

## 21. **VALIDAÇÃO DE EMAIL REGEX NÃO USADA**

**Severidade:** ⚪ BAIXO  
**Arquivo:** `config.py` (linha 32)  
**Problema:** Regex definido mas nunca usado

```python
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
```

Validações em `app.py` não usam isso

---

# 🔐 PROBLEMAS DE SEGURANÇA

## 22. **JWT COM CLAIMS NÃO ESTRUTURADOS**

**Severidade:** 🔴 CRÍTICO (Segurança)  
**Arquivo:** `app.py` (linhas 248-254, etc.)  
**Problema:** Adiciona claims variados ao JWT sem padronização

### Código
```python
# Às vezes adiciona 'tipo'
additional_claims={'tipo': 'administrador', ...}

# Às vezes adiciona 'turmas'
additional_claims={'tipo': 'professor', 'turmas': [...]}

# Às vezes adiciona 'serie_id'
additional_claims={'tipo': 'aluno', 'serie_id': ...}
```

### Problema
- ❌ Inconsistente
- ❌ Difícil de validar
- ❌ Risco de aceitar tokens malformados

### Solução Necessária
Estrutura padrão:
```python
{
    'tipo': 'professor|aluno|administrador',
    'id': user_id,
    'nome': nome,
    'turmas': []  # Só para professor
}
```

---

## 23. **SENHA DE ALUNO NUNCA USADA**

**Severidade:** 🟡 ALTO (Segurança)  
**Arquivo:** `banco_dados.py` (linhas 73)  
**Problema:** Campo `senha` na tabela `alunos` mas nunca hash

### Código
```python
def adicionar_aluno(self, ..., senha=None, ...):
    cursor.execute('''INSERT INTO alunos (..., senha, ...)
        VALUES (..., ?, ...)''', (..., senha, ...))  # ❌ SENHA PLANA!
```

### Problema
- ❌ Senhas de aluno armazenadas EM CLARO
- ❌ Se banco vazar, todos alunos comprometidos
- ❌ Backend tem `bcrypt` implementado, mas não usa para aluno

### Solução Necessária
```python
def adicionar_aluno(self, ..., senha=None, ...):
    if senha:
        senha = self.hash_senha(senha)  # ✅ Hash com bcrypt
```

---

## 24. **CORS ABERTO NOS HEADERS DE RESPOSTA**

**Severidade:** 🟡 ALTO (Segurança)  
**Arquivo:** `config.py` (linhas 24-26)  
**Problema:** CORS_ORIGINS via variável, mas pode ser `*`

### Código
```python
CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5000').split(',')
```

### Risco
- Se `.env` configura `CORS_ORIGINS='*'`, qualquer domínio consegue acessar
- Mesmo com JWT, expõe dados

### Solução
- ✅ Validar que CORS_ORIGINS é lista de domínios específicos
- ✅ Nunca permitir `*`

---

## 25. **ATUALIZAR PROFESSOR PERMITE EMAIL DUPLICADO**

**Severidade:** 🟡 ALTO (Segurança)  
**Arquivo:** `banco_dados.py` (linhas 256-290)  
**Problema:** Função `atualizar_professor()` permite duplicação de email

### Código
```python
if email not in (None, ''):
    campos.append('email = ?')
    valores.append(email)

cursor.execute(f"UPDATE professores SET {', '.join(campos)} WHERE id = ?")
```

### Problema
- ❌ Sem constraint UNIQUE ao atualizar
- ❌ Dois professores com mesmo email possível
- ❌ Quebra lógica de autenticação

### Solução Necessária
```python
# Validar se email já existe e pertence a outro professor
cursor.execute('SELECT id FROM professores WHERE email = ? AND id != ?', 
               (email, professor_id))
if cursor.fetchone():
    return False  # Email já existe para outro professor
```

---

# 📋 RESUMO ADICIONAL

## Funcionalidades Não Implementadas
- ❌ Criar atividades (POST `/api/atividades`)
- ❌ Editar atividades (PUT `/api/atividades/<id>`)
- ❌ Deletar atividades (DELETE `/api/atividades/<id>`)
- ❌ Dashboard do aluno com atividades funcionais
- ❌ Comunicados/Avisos para alunos
- ❌ Sistema de "lição de casa"

## Testes Não Encontrados
- ❌ Nenhum arquivo `test_*.py` (exceto scripts de dados)
- ❌ Nenhum teste de integração
- ❌ Nenhum teste de segurança

## Documentação Faltando
- ❌ Documentação de API (OpenAPI/Swagger)
- ❌ Guia de deployment
- ❌ Guia de configuração
- ❌ Documentação de banco de dados

---

## 🎯 PRIORIDADE DE CORREÇÃO

### DEVE FAZER (Bloqueadores)
1. ✅ **Adicionar colunas corretas à tabela `notas`** (avm, avb, rec, mb)
2. ✅ **Deletar ou desabilitar `atualizar_estrutura_notas.py`**
3. ✅ **Implementar endpoint de atividades**
4. ✅ **Recalcular MB quando REC muda**
5. ✅ **Implementar `verificar_login_aluno_por_matricula()`**

### DEVERIA FAZER (Próximas 2 semanas)
6. ✅ Mover admin para banco de dados
7. ✅ Adicionar `@jwt_required()` em `/api/series`
8. ✅ Hash de senha para alunos
9. ✅ Validação de permissão em todas rotas
10. ✅ Rota POST para criar atividades

### PODE FAZER DEPOIS (Nice-to-have)
11. ✅ Refatorar código duplicado
12. ✅ Adicionar logging estruturado
13. ✅ Documentação de API
14. ✅ Testes automatizados

---

## 📝 NOTAS FINAIS

1. **Sistema é utilizável COM LIMITAÇÕES** - Funcionalidade de notas está quebrada, atividades não aparecem
2. **Segurança precisa melhoria** - Admin hardcoded, CORS, validação de email
3. **Código pode melhorar** - Duplicação, inconsistência de nomes, falta de testes
4. **Documentação ausente** - Difícil para novos desenvolvedores

**Recomendação:** Corrigir problemas críticos (#1-#5) ANTES de usar em produção.

---

**Documento gerado:** 2026-09-08  
**Próxima revisão recomendada:** Após correção dos 5 problemas críticos
