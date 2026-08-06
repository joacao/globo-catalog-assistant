# 📚 Assistente de Curadoria de Catálogo | Editora Globo
Sistema de Recuperação Aumentada por Geração (RAG) desenvolvido para auxiliar na curadoria, consulta e filtragem inteligente do catálogo de livros da Editora Globo, integrando busca vetorial, LLMs e observabilidade completa.

# 🚀 Tecnologias Utilizadas
- Backend: Python 3.11, FastAPI, Uvicorn, Pydantic v2

- Banco de Dados Vetorial: Qdrant

- Inteligência Artificial: OpenAI API (gpt-4o-mini e modelos de Embedding)

- Observabilidade & Monitoramento: Langfuse (self-hosted via Docker)

- Containerização: Docker & Docker Compose

# 🛠️ Arquitetura do Sistema

Plaintext
[ Frontend / React ] 
       │
       ▼ (HTTP POST /api/v1/ask)
[ Backend / FastAPI ] ──(Gera Embedding)──► [ OpenAI API ]
       │                                        │
       ├─(Busca Vetorial + Filtros)──────────► [ Qdrant DB ]
       │
       └─(Traces, Tokens e Custos)──────────► [ Langfuse (Porta 3001) ]

# ⚙️ Configuração e Instalação
1. Clonar o Repositório

`git clone https://github.com/seu-usuario/globo-catalog-assistant.git`
`cd globo-catalog-assistant`

2. Subir a Aplicação com Docker Compose
Execute o comando abaixo para iniciar todos os serviços (Backend, Qdrant, Langfuse e Banco de Dados de suporte)
`sudo docker compose up`

3. Configurar as Variáveis de Ambiente
Crie um arquivo .env na raiz do projeto baseado no exemplo abaixo:

`OPENAI_API_KEY=sk-sua-chave-openai-aqui`

`QDRANT_HOST=qdrant`
`QDRANT_PORT=6333`

`LANGFUSE_HOST=http://langfuse-web:3000`
`LANGFUSE_PUBLIC_KEY=pk-lf-sua-chave-publica`
`LANGFUSE_SECRET_KEY=sk-lf-sua-secret-key`

Para gerar uma chave de API na OpenAI acesse esse [site] (https://platform.openai.com/api-keys) e no canto superior direito clique em "Create new secret key" Observação será necessário o Login

Para conectar o backend ao Langfuse e habilitar a observabilidade do sistema RAG (rastreamento de traces, latência, consumo de tokens e custos), siga os passos abaixo:

1. Acesse o Painel do Langfuse:
- Abra o navegador em http://localhost:3001 ou clique no atalho "Langfuse Traces" na barra lateral da interface do chat.

2. Criar Conta / Login:
- Na primeira execução da instância local, crie uma conta administrativa preenchendo os campos de registro.

3. Criar ou Selecionar um Projeto:
- Abra o projeto existente ou crie um novo projeto no menu superior esquerdo (ex: Editora Globo).

4.Gerar as Chaves de API:
- No menu lateral esquerdo do painel do Langfuse, acesse Settings (Configurações).
- Vá até a seção API Keys e clique em Create new API keys.

5. Atualizar o arquivo .env:

- Copie a Public Key (pk-lf-...) e a Secret Key (sk-lf-...) geradas e adicione-as ao seu arquivo .env na raiz do repositório

6. Recarregar o Backend:
- Caso o container do backend já esteja em execução, reinicie o serviço para aplicar as novas credenciais:

Bash
`sudo docker compose restart backend`

4. Popular o Catálogo (Ingestão)
Com os containers no ar, rode o script de ingestão para gerar os embeddings e indexar os 200 livros no Qdrant:

`sudo docker compose exec backend python scripts/ingest_books.py`

# 📊 Observabilidade com Langfuse
O projeto conta com monitoramento integrado de ponta a ponta via Langfuse.

Acesse o painel local em: http://localhost:3001

Lá você poderá inspecionar em tempo real:

Latência de cada requisição.

Consumo de Tokens de prompt e completion.

Custo estimado por chamada da OpenAI.

O Prompt Contextualizado enviado para o modelo.

# 🧪 Documentação da API (Swagger)
Com a aplicação rodando, acesse a documentação interativa gerada automaticamente pelo FastAPI em:
http://localhost:8000/docs

## ⚖️ Decisões Arquiteturais e Trade-offs

* **Modelo LLM (`gpt-4o-mini`):** Priorizado para otimizar tempo de resposta e custo por consulta na curadoria do catálogo, mantendo precisão adequada para RAG contextualizado.
* **Infraestrutura do Langfuse (v2):** Mantida em container local com PostgreSQL para garantir um ambiente autosuficiente e de baixo consumo de recursos hardware durante os testes.
* **Estratégia de Cache:** Implementação de `@lru_cache` para embeddings de busca, reduzindo o tráfego de rede e o consumo de quota da API.

# Fonte de dados
- Os dados de catálogo (`books.json`) foram fornecidos pela Editora Globo como parte do desafio técnico, não foram gerados nem coletados por mim.

# ⚠️ Limitações Conhecidas e Próximos Passos (Visão de Produto & Engenharia)
Esta seção documenta decisões conscientes de escopo tomadas para garantir uma entrega robusta dentro do prazo, além de indicar as evoluções naturais do projeto para um ambiente de produção.

1. Qualidade e Corte na Busca Semântica

- Como está hoje: O banco vetorial sempre retorna os 5 livros com maior proximidade conceitual da pergunta. Se o usuário pesquisar algo totalmente fora do universo do catálogo (ex: "como trocar o pneu do carro"), o banco entregará os itens "menos distantes" e o sistema dependerá do system prompt do LLM para reconhecer que não há relação e responder que não encontrou.

- Evolução de Produto: Adicionar um limiar mínimo de similaridade (score threshold). Se a busca vetorial não atingir uma nota mínima de relevância, o fluxo é interrompido antes de chamar o LLM, economizando custos de API e reduzindo a latência para o usuário.

2. Combinação de Palavras-Chave e Conceitos (Busca Híbrida)

- Como está hoje: A busca é 100% baseada no significado da frase (busca semântica por embeddings).

Evolução de Produto: Busca Híbrida e Arquitetura Agêntica:
Para resolver falhas com nomes próprios, códigos ou termos específicos, a melhoria imediata seria a Busca Híbrida (combinando vetores densos do Qdrant com busca por texto exato via BM25). Em um segundo momento, a adição de Tool Calling via MCP permitiria que a IA atuasse como um agente completo, decidindo se deve realizar uma busca semântica, uma consulta exata ou acessar sistemas externos da editora.

3. Arquitetura de Nuvem e Serverless
Como está hoje: A infraestrutura com Qdrant local via Docker é ideal para desenvolvimento, testes e execução em máquinas dedicadas.

Evolução para Produção: Caso a aplicação seja implantada em ambientes serverless de nuvem (como Google Cloud Run), a camada de dados vetoriais deve evoluir para um cluster gerenciado do Qdrant ou utilizar estratégias de reconciliação via snapshots, garantindo que os dados persistam de forma independente do ciclo de vida dos containers.

4. Regras de Negócio e Estoque em Tempo Real
Como está hoje: A curadoria recomenda livros exclusivamente com base na afinidade do conteúdo (título, gênero e sinopse).

Evolução de Produto: Conectar o payload da busca com o sistema de inventário ou ERP da editora. Isso permitiria aplicar filtros de negócio em tempo real — como ocultar livros esgotados, priorizar lançamentos ou destacar títulos em promoção diretamente na resposta da IA.

### 💰 Estimativa de Custo por Requisição
O custo de cada chamada é calculado e rastreado dinamicamente pelo **Langfuse** com base no consumo real de tokens (prompt + resposta) do modelo `gpt-4o-mini`. Os relatórios consolidados e a métrica por requisição podem ser auditados em tempo real no painel local (`http://localhost:3001`).

# 🤖 Uso Prático de IA no Processo de Desenvolvimento
A utilização do Gemini neste projeto seguiu um princípio claro: a IA atuou como um acelerador de produtividade e digitação de código, enquanto o papel de arquiteto e a tomada de decisão técnica permaneceram 100% sob o controle do desenvolvedor.

1. Contexto e Motivação
Diante de uma rotina com tempo restrito para digitação manual linha a linha, o uso de IA Generativa foi adotado como uma decisão estratégica de processo. O objetivo foi otimizar o tempo de execução sem abrir mão do rigor técnico, permitindo focar no que realmente importa: o desenho da arquitetura, a escolha das ferramentas e a resolução de problemas de integração entre os containers.

2. Metodologia: Controle Passo a Passo vs. "Caixa Preta"
Em vez de delegar a criação do sistema por meio de um comando genérico ("monte um assistente de RAG para mim") ou entregar um documento passivo para a IA decidir o projeto, a solução foi construída de forma incremental e totalmente guiada:

Arquitetura Orientada pelo Desenvolvedor: O pipeline do RAG (FastAPI, Qdrant, Langfuse e Docker), a estrutura de camadas e as estratégias de contorno (como o uso de decorators @observe para viabilizar a comunicação REST na v2 do Langfuse) foram desenhados previamente na mente do desenvolvedor.

Acelerador de Digitação: O Gemini foi utilizado para traduzir instruções técnicas diretas em blocos de código concretos, eliminando o tempo gasto com código boilerplate e sintaxe repetitiva.

3. Validação, Refatoração e Propriedade do Código
Nenhum código gerado foi integrado ao repositório de forma cega. O processo de validação envolveu:

Depuração de Logs: Diagnóstico e análise profunda de erros nos containers via docker logs, identificando conflitos de pacotes (pip), portas e rotas de API.

Refatoração e Padronização: Revisão manual do código para alinhar rotas do FastAPI, adequar o tratamento de exceções, traduzir e reescrever comentários e padronizar nomes de variáveis para o português do projeto.

4. Transparência Técnica
Essa abordagem garante que nenhuma linha de código no repositório seja uma "caixa preta". Todo o fluxo — desde a geração do vetor no Qdrant até a exportação de traces para o Langfuse — é dominado em detalhes pelo desenvolvedor, demonstrando que a IA serve como um amplificador de velocidade para uma arquitetura bem definida, mantendo a responsabilidade técnica e o conhecimento técnico integralmente no engenheiro de IA.