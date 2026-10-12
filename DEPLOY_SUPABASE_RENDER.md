# 🚀 Deploy no Supabase e Render

## Pré-requisitos

- Conta no [Supabase](https://supabase.com)
- Conta no [Render](https://render.com)
- Repositório GitHub atualizado

---

## 📋 Passo 1: Configurar Supabase (PostgreSQL)

### 1.1 Criar um Projeto no Supabase

1. Acesse [supabase.com](https://supabase.com) e faça login
2. Clique em "New Project"
3. Preencha os dados:
   - **Project Name**: `site-letrasecores`
   - **Database Password**: Use uma senha forte
   - **Region**: Escolha a mais próxima (ex: `us-east-1`)
4. Clique em "Create new project"

### 1.2 Obter a String de Conexão

1. No painel do Supabase, vá para "Settings" → "Database"
2. Copie a **Connection string** (URI)
3. Procure por algo como:
   ```
   postgresql://postgres:[PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres
   ```

---

## 🔌 Passo 2: Configurar Render para Deploy

### 2.1 Conectar GitHub ao Render

1. Acesse [render.com](https://render.com)
2. Faça login ou crie uma conta
3. Clique em "New +" → "Web Service"
4. Selecione "Deploy an existing repository from GitHub"
5. Conecte sua conta GitHub
6. Selecione o repositório `site_letrasecores`

### 2.2 Configurar o Web Service

1. **Name**: `site-letrasecores`
2. **Environment**: `Python 3`
3. **Build Command**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Start Command**:
   ```bash
   gunicorn app:app
   ```
5. **Instance Type**: Escolha o plano (Free ou Premium)

### 2.3 Adicionar Variáveis de Ambiente

Clique em "Environment" e adicione:

```
DATABASE_URL=postgresql://[seu_usuario]:[sua_senha]@db.[seu-project-id].supabase.co:5432/postgres
FLASK_ENV=production
SECRET_KEY=[gere uma chave aleatória forte]
JWT_SECRET_KEY=[gere uma chave JWT forte]
```

> **Dica**: Para gerar chaves aleatórias:
> ```python
> import secrets
> print(secrets.token_hex(32))  # Gera 64 caracteres hexadecimais
> ```

---

## 🔄 Passo 3: Atualizar Repositório GitHub

### 3.1 Atualizar arquivo .env.example

```bash
git add .env.example
git commit -m "docs: adicionar instrucoes de DATABASE_URL para Supabase"
```

### 3.2 Fazer Push das Alterações

```bash
git add banco_dados.py requirements.txt .env.example
git commit -m "feat: adicionar suporte para PostgreSQL/Supabase e SQLite local"
git push origin main
```

### 3.3 Deploy Automático

1. O Render detectará o push automaticamente
2. Iniciará a build
3. Se tudo correr bem, seu site estará online!

Para acompanhar o deploy:
- Acesse o painel do Render
- Clique no seu projeto
- Veja a aba "Events" para logs de build

---

## 🧪 Passo 4: Testar a Conexão com Supabase

### Local (SQLite)

```bash
python -c "from banco_dados import BancoDados; db = BancoDados()"
# Saída: ✓ Usando SQLite local
```

### Produção (PostgreSQL via Render)

Se tiver acesso SSH ao Render:

```bash
render logs  # Ver logs de produção
```

Ou adicione um teste na sua API:

```python
@app.route('/api/health', methods=['GET'])
def health():
    db = BancoDados()
    stats = db.obter_estatisticas()
    return jsonify({
        'status': 'ok',
        'database': 'PostgreSQL' if db.usar_postgresql else 'SQLite',
        'stats': stats
    })
```

---

## 📝 Monitorando seu Banco de Dados

### Via Supabase Studio

1. Acesse seu projeto no Supabase
2. Vá para "Table Editor"
3. Veja e gerencie suas tabelas
4. Execute queries em "SQL Editor"

### Backups Automáticos

Supabase cria backups automáticos. Para restaurar:

1. Vá para "Database" → "Backups"
2. Clique em "Restore from backup"

---

## 🔒 Segurança

### ✅ Faça

- Use `.env` localmente (NUNCA fazer commit)
- Use variáveis de ambiente no Render
- Mude as senhas padrão do admin
- Use JWT para autenticação
- Ativar SSL no Supabase (já vem ativado)

### ❌ Não Faça

- ❌ Commitar `.env` no Git
- ❌ Compartilhar DATABASE_URL
- ❌ Usar senhas fracas
- ❌ Deixar FLASK_DEBUG=True em produção

---

## 🆘 Troubleshooting

### Erro: "could not translate host name to address"

**Solução**: Verifique se a DATABASE_URL está correta no Render

### Erro: "password authentication failed"

**Solução**: Verify your Supabase password in the connection string

### Erro: "relation does not exist"

**Solução**: Rode o script de inicialização:
```python
from banco_dados import inicializar_banco
inicializar_banco()
```

### API retorna erro 500

1. Verifique os logs no Render
2. Verifique a conexão com banco de dados
3. Verifique as variáveis de ambiente

---

## 📚 Referências

- [Documentação Supabase](https://supabase.com/docs)
- [Documentação Render](https://render.com/docs)
- [PostgreSQL Connection Strings](https://www.postgresql.org/docs/current/libpq-connect.html)
- [Gunicorn Settings](https://docs.gunicorn.org/en/stable/settings.html)

---

**Última atualização**: 2026-10-12
**Versão**: 1.0.0
