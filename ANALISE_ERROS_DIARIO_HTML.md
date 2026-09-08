# 🔍 ANÁLISE DE ERROS - diario.html

## 📋 RESUMO DOS PROBLEMAS ENCONTRADOS

Identificados **3 problemas críticos** que impedem:
1. ❌ Cálculo correto de MB (Média Bimestral) com REC
2. ❌ Salvamento de notas no banco de dados
3. ❌ Exibição de atividades agendadas

---

## ⚠️ PROBLEMA #1: Nomes de Colunas Inconsistentes no Banco de Dados

### 🔴 SITUAÇÃO CRÍTICA
**Arquivo afetado:** `banco_dados.py`, `app.py`, `diario.html`

### 📊 Inconsistência Encontrada

#### Criação da Tabela (banco_dados.py, linhas 104-115)
```sql
CREATE TABLE IF NOT EXISTS notas (
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
)
```

**❌ FALTAM COLUNAS:** `avm`, `avb`, `rec`, `mb`

#### Migração Alternativa (atualizar_estrutura_notas.py, linhas 27-44)
```python
novas_colunas = {
    'nota_mensal_1': 'REAL',
    'nota_mensal_2': 'REAL', 
    'nota_mensal_3': 'REAL',
    'nota_bimestral': 'REAL',
    'nota_recuperacao': 'REAL',
    'tipo_nota': "TEXT DEFAULT 'bimestral'"
}
```

**⚠️ NOMES COMPLETAMENTE DIFERENTES!**
- Arquivo de migração usa: `nota_mensal_1`, `nota_bimestral`, `nota_recuperacao`
- Backend espera: `avm`, `avb`, `rec`, `mb`
- Frontend envia: `avm`, `avb`, `rec`

### 🎯 Consequências

#### No Backend (app.py, linha 1003-1043)
```python
# Frontend envia isso:
avm = data.get('avm')      # Avaliação Mensal (peso mensal)
avb = data.get('avb')      # Avaliação Bimestral
rec = data.get('rec')      # Recuperação

# Backend tenta inserir:
cursor.execute('''INSERT INTO notas (aluno_id, professor_id, disciplina, nota, 
    bimestre, observacao, avm, avb, rec, mb)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''')
```

**❌ ERRO ESPERADO:** `OperationalError: no such column: avm` 
(A coluna `avm` não existe na tabela!)

#### No Banco de Dados (banco_dados.py, linhas 876-883)
```python
def registrar_nota(...):
    # Calcula MB (Média Bimestral)
    if avm is not None and avb is not None:
        mb = (float(avm) + float(avb)) / 2
        
        # Se MB < 6 e há REC, recalcula
        if mb < 6 and rec is not None:
            maior_nota = max(float(avm), float(avb))
            mb = (maior_nota + float(rec)) / 2
```

**❌ NUNCA EXECUTA:** Tenta inserir em colunas que não existem!

---

## ⚠️ PROBLEMA #2: Lógica de Recalcular MB com REC Incompleta

### 📍 Arquivo: diario.html (linhas 835-865)

```javascript
function atualizarMB(inputElement) {
    const row = inputElement.closest('tr');
    const avm = parseFloat(row.querySelector('.avm-input').value) || 0;
    const avb = parseFloat(row.querySelector('.avb-input').value) || 0;
    const recInput = row.querySelector('.rec-input');
    const mbDisplay = row.querySelector('.mb-display');
    
    if (!avm || !avb) {
        mbDisplay.textContent = '-';
        recInput.disabled = true;
        recInput.value = '';
        return;
    }
    
    let mb = (avm + avb) / 2;
    mbDisplay.textContent = mb.toFixed(1);
    
    // Se MB < 6, habilitar REC
    if (mb < 6) {
        recInput.disabled = false;
        mbDisplay.style.color = '#dc3545'; // Vermelho
    } else {
        recInput.disabled = true;
        recInput.value = '';
        mbDisplay.style.color = '#28a745'; // Verde
    }
}
```

### 🔴 PROBLEMAS IDENTIFICADOS

1. **Sem Recálculo ao Preenchimento de REC**
   - Quando o professor preenche REC (recuperação), MB **NÃO é recalculado**
   - A função `atualizarMB()` só é chamada ao mudar AVM ou AVB
   - **Resultado:** MB continua com o valor antigo (< 6) mesmo após preencher REC

   **Cenário:**
   ```
   AVM: 4.0 → MB: 4.0 (habilita REC)
   AVB: 4.5 → MB: 4.2 (habilita REC)
   REC: 7.0 → MB: 4.2 (❌ ERRADO! Deveria ser (4.5 + 7.0) / 2 = 5.75)
   ```

2. **Fórmula de REC Não Está Implementada no Frontend**
   - O backend calcula: `(maior_nota + rec) / 2`
   - O frontend calcula: `(avm + avb) / 2` (simples média)
   - **Problema:** Quando REC é preenchido, o frontend não recalcula!

3. **REC Disabled Desabilita Salvamento**
   - Linhas 920 do `salvarNotas()`:
   ```javascript
   const rec = recInput.value.trim(); // ✓ Pega valor mesmo se disabled
   ```
   - Embora pegue o valor, o input está `disabled` visualmente
   - **Comportamento confuso:** Campo aparenta desabilitado mas funciona

---

## ⚠️ PROBLEMA #3: Função `carregarBimestre()` Incompleta

### 📍 Arquivo: diario.html (linhas 738-751)

```javascript
// Filtrar notas por disciplina e bimestre
const notasFiltradas = todasAsNotas.filter(n => {
    // Comparar nome da disciplina ou usar ID se disponível
    return (n.disciplina && n.disciplina.toLowerCase() === disciplinaNome.toLowerCase()) &&
           parseInt(n.bimestre) === parseInt(bimestre);
});
```

### 🔴 PROBLEMA IDENTIFICADO

**Filtro por disciplina usa nome (string) em vez de ID (número)**

- Frontend envia e recebe: `disciplina_id`
- Backend retorna: `n.disciplina` (nome do texto)
- **Resultado:** Comparação case-sensitive pode falhar

**Exemplo:**
```javascript
// Backend retorna:
{ aluno_id: 1, disciplina: "Português", bimestre: 1, avm: 6.5, avb: 7.0 }

// Frontend esperava:
{ aluno_id: 1, disciplina: "português", bimestre: 1, avm: 6.5, avb: 7.0 }

// Filtro com .toLowerCase() deveria funcionar, MAS:
// Aqui está sendo comparado com disciplinaNome (que vem do <option>)
// Se o banco tiver "português" e a option tiver "Português" → falha!
```

---

## ⚠️ PROBLEMA #4: Atividades Não Retornam Dados

### 📍 Arquivo: app.py (linhas 1097-1122)

```python
@app.route('/api/aluno/atividades', methods=['GET'])
@jwt_required()
def obter_atividades_aluno():
    """Retorna atividades agendadas para o aluno"""
    try:
        # ... código ...
        
        # ❌ RETORNA LISTA VAZIA!
        atividades = []
        
        return jsonify(atividades), 200
```

### 🔴 PROBLEMAS IDENTIFICADOS

1. **Endpoint Retorna Lista Vazia (Sempre)**
   - Tem comentário: `# TODO: Criar tabela de atividades e implementar`
   - Retorna: `[]` (vazio)
   - **Resultado:** Atividades nunca aparecem, mesmo que estejam cadastradas

2. **Sem Chamada para Função de Busca**
   - Tabela `atividades` existe em `banco_dados.py` (linha 220-231)
   - Mas a rota não a usa!
   - **Esperado:**
   ```python
   # Buscar atividades para a série do aluno
   atividades = db.listar_atividades_por_serie(serie_id)
   return jsonify([dict(a) for a in atividades]), 200
   ```

3. **Nenhuma Função de Criação de Atividades no Frontend**
   - `diario.html` não tem interface para criar atividades
   - Professor não consegue agendar atividades
   - Aluno não consegue ver atividades

---

## ⚠️ PROBLEMA #5: Cálculo de MB Inicial Carrega Valor Antigo

### 📍 Arquivo: diario.html (linhas 764-770)

```javascript
alunosData.forEach(aluno => {
    const notas_aluno = notasPorAluno[aluno.id];
    const avm_val = notas_aluno.avm !== null ? notas_aluno.avm : '';
    const avb_val = notas_aluno.avb !== null ? notas_aluno.avb : '';
    const rec_val = notas_aluno.rec !== null ? notas_aluno.rec : '';
    const mb_val = notas_aluno.mb !== null ? notas_aluno.mb.toFixed(1) : '-';
```

### 🔴 PROBLEMA

Quando a página carrega:
1. Busca notas antigas do banco: `const todasAsNotas = await response.json()`
2. Preenche inputs com valores antigos: `avm: 5.0, avb: 5.5, rec: null`
3. Calcula MB: `mb = (5.0 + 5.5) / 2 = 5.25` (mostra em vermelho)
4. **Problema:** Se o professor mudou REC de `null` para `8.0`, MB não atualiza visualmente até clicar nos inputs

**Não há chamada a `atualizarMB()` após carregar os dados!**

---

## 📌 FLUXO DO PROBLEMA COMPLETO

```
1. Professor abre diario.html
   ✓ Página carrega
   ✓ Alunos carregam
   
2. Professor seleciona bimestre e disciplina
   ✓ Notas antigas carregam (AVM, AVB do bimestre anterior)
   ✓ MB exibe valor antigo
   ✓ REC habilitado se MB < 6
   
3. Professor preenche NOVAS notas:
   ✓ AVM: 4.0, AVB: 4.5 → MB: 4.2 (✓ Correto, REC habilitado)
   ✓ REC: 8.0 → MB: 4.2 (❌ ERRADO! Deveria ser 5.75)
   
4. Professor clica SALVAR NOTAS
   ❌ Erro: "no such column: avm" (coluna não existe)
   ❌ Nenhuma nota é salva
   
5. Aluno abre diário
   ❌ Notas não aparecem (nunca foram salvas)
   ❌ Atividades não aparecem (função retorna vazio)
```

---

## 📋 CHECKLIST DO QUE PRECISA SER CORRIGIDO

### Prioridade 🔴 CRÍTICA (Bloqueia tudo)

- [ ] **1. Renomear colunas da tabela `notas`**
  - Adicionar: `avm`, `avb`, `rec`, `mb` (ou decidir entre dois nomes)
  - Opção A: ALTER TABLE - adicionar colunas aos dados existentes
  - Opção B: Recriar tabela com nomes corretos

- [ ] **2. Atualizar `atualizar_estrutura_notas.py`**
  - Usar nomes corretos: `avm`, `avb`, `rec`, `mb`
  - OU deletar e usar uma única estratégia

- [ ] **3. Implementar recalcular MB ao mudar REC**
  - Frontend: Adicionar listener `onchange` no campo REC
  - Chamar `atualizarMB(this)` quando REC muda

### Prioridade 🟡 ALTA (Afeta funcionalidade)

- [ ] **4. Implementar endpoint de atividades**
  - Adicionar função `db.listar_atividades_por_serie()`
  - Modificar `/api/aluno/atividades` para retornar dados reais
  - Criar interface no frontend para ver/criar atividades

- [ ] **5. Corrigir filtro de disciplina**
  - Usar `discipline_id` (número) em vez de `disciplina` (nome)
  - Manter backup se nome for necessário

- [ ] **6. Recalcular MB ao carregar dados iniciais**
  - Chamar `atualizarMB()` para cada linha após preenchimento

### Prioridade 🟢 MÉDIA (Melhorias)

- [ ] **7. Validações adicionais de REC**
  - REC só deve ser preenchido se MB < 6
  - Mostrar mensagem clara: "Recuperação é apenas para notas < 6"

- [ ] **8. Testes de integração**
  - Salvar notas e verificar se aparecem
  - Salvar REC e verificar cálculo correto

---

## 🎯 PRÓXIMOS PASSOS RECOMENDADOS

1. **Começar pela correção das colunas** (Problema #1)
   - É a causa raiz de tudo não funcionar
   - Uma vez corrigido, salvamento de notas funcionará

2. **Depois corrigir a lógica de REC** (Problema #2)
   - Adicionar recálculo de MB quando REC muda
   - Testar cenários: MB >= 6, MB < 6 com REC, MB < 6 sem REC

3. **Implementar atividades** (Problema #4)
   - Interface simples no backend
   - Listar e criar atividades

4. **Teste integrado final**
   - Professor cria/edita notas
   - Verifica se notas aparecem no aluno
   - Verifica atividades

---

## 📝 DOCUMENTAÇÃO ORIGINAL ENCONTRADA

Vide `/memories/repo/site_letrasecores_fixes.md` - Todas as correções anteriores estão documentadas
