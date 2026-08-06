import React, { useState, useRef, useEffect } from 'react';
import { askQuestion } from './services/api';
import ReactMarkdown from 'react-markdown';
import { Send, BookOpen, Bot, User, Wrench, ExternalLink, X } from 'lucide-react';

// Links técnicos: só aparecem pra quem clica no ícone de ferramentas no header.
// Um usuário leigo nunca precisa ver isso pra usar o assistente.
const TECH_LINKS = [
  { label: 'Traces (Langfuse)', hint: 'Latência, tokens e custo de cada resposta', url: 'http://localhost:3001' },
  { label: 'Painel do Qdrant', hint: 'Coleção de vetores e busca', url: 'http://localhost:6333/dashboard' },
  { label: 'Documentação da API', hint: 'Swagger / OpenAPI', url: 'http://localhost:8000/docs' },
];

// Ecoa o padrão de listras diagonais do ícone da logo da Editora Globo.
// Usado no chip do header e no indicador de "carregando".
function StripeMark({ className = '' }) {
  return (
    <svg viewBox="0 0 32 32" fill="none" className={className} aria-hidden="true">
      <rect width="32" height="32" rx="9" fill="url(#stripe-gradient)" />
      <g stroke="white" strokeWidth="2.4" strokeLinecap="round" opacity="0.92">
        <line x1="8" y1="23" x2="14" y2="9" />
        <line x1="13" y1="23" x2="19" y2="9" />
        <line x1="18" y1="23" x2="24" y2="9" />
      </g>
      <defs>
        <linearGradient id="stripe-gradient" x1="0" y1="0" x2="32" y2="32" gradientUnits="userSpaceOnUse">
          <stop stopColor="#1D3AE0" />
          <stop offset="0.55" stopColor="#7B2FE0" />
          <stop offset="1" stopColor="#C22BD1" />
        </linearGradient>
      </defs>
    </svg>
  );
}

export default function App() {
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: 'Olá! Sou o Assistente de Curadoria do Catálogo da Editora Globo. Pergunte sobre títulos, autores, gêneros ou peça sugestões de leitura.',
      references: []
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  // Mantém o ID da conversa entre turnos. Fica null até a primeira resposta
  // do backend, que é quem gera o UUID (conversa nova sem ID -> backend cria;
  // conversa existente -> reenviamos o mesmo ID nas próximas perguntas).
  const [conversationId, setConversationId] = useState(null);
  const [toolsOpen, setToolsOpen] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { sender: 'user', text: userMessage }]);
    setLoading(true);

    try {
      const data = await askQuestion(userMessage, conversationId);
      setConversationId(data.conversation_id); // guarda pro próximo turno
      setMessages((prev) => [
        ...prev,
        {
          sender: 'bot',
          text: data.answer,
          references: data.references || []
        }
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          sender: 'bot',
          text: 'Não consegui consultar o catálogo agora. Tente novamente em instantes.',
          references: []
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-paper text-ink">

      {/* Header: identidade da marca concentrada aqui, resto da página fica neutro */}
      <header className="relative bg-ink text-white">
        <div className="max-w-4xl mx-auto flex items-center justify-between px-5 py-3.5">
          <div className="flex items-center gap-4">
            {/* LOGO OFICIAL */}
            <img 
              src="/logo-editora-globo.png" 
              alt="Logo Editora Globo" 
              className="h-14 w-auto object-contain drop-shadow-md"
            />
            
            {/* Divisor vertical discreto */}
            <div className="h-10 w-[1px] bg-white/30 rounded-full mx-1"></div>

            <div>
              <h1 className="text-2xl font-bold text-white tracking-tight">Desafio Técnico</h1>
              <p className="text-blue-100 text-sm font-medium">Assistente de Curadoria do Catálogo</p>
            </div>
          </div>

          {/* Acesso técnico discreto - não é navegação principal, é um detalhe pra quem sabe o que procura */}
          <div className="relative">
            <button
              onClick={() => setToolsOpen((v) => !v)}
              aria-expanded={toolsOpen}
              aria-label="Ferramentas técnicas"
              className="flex items-center gap-1.5 text-white/70 hover:text-white text-xs font-medium px-3 py-2 rounded-lg hover:bg-white/10 transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-globo-magenta"
            >
              <Wrench size={14} />
              <span className="hidden sm:inline">Ferramentas</span>
            </button>

            {toolsOpen && (
              <>
                <div className="fixed inset-0 z-10" onClick={() => setToolsOpen(false)} />
                <div className="absolute right-0 top-full mt-2 w-64 bg-white text-ink rounded-xl shadow-xl border border-mist z-20 overflow-hidden">
                  <div className="flex items-center justify-between px-4 py-2.5 border-b border-mist">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-ink/50">
                      Acesso técnico
                    </span>
                    <button
                      onClick={() => setToolsOpen(false)}
                      aria-label="Fechar"
                      className="text-ink/40 hover:text-ink"
                    >
                      <X size={14} />
                    </button>
                  </div>
                  {TECH_LINKS.map((link) => (
                    <a
                      key={link.url}
                      href={link.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-start justify-between gap-2 px-4 py-3 hover:bg-mist/60 transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-globo-violet"
                    >
                      <span>
                        <span className="block text-sm font-semibold">{link.label}</span>
                        <span className="block text-xs text-ink/50">{link.hint}</span>
                      </span>
                      <ExternalLink size={13} className="shrink-0 mt-0.5 text-ink/30" />
                    </a>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>
        {/* Fio de gradiente: única outra aparição da cor de marca fora do chip da logo */}
        <div className="h-[3px] bg-globo-gradient" />
      </header>

      {/* Área de Chat */}
      <main className="flex-1 overflow-y-auto px-4 md:px-6 py-6 space-y-5 max-w-3xl mx-auto w-full">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex gap-3 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.sender === 'bot' && (
              <div className="w-8 h-8 rounded-lg bg-globo-gradient text-white flex items-center justify-center shrink-0 shadow-sm">
                <Bot size={16} />
              </div>
            )}

            <div
              className={`max-w-[85%] rounded-2xl px-5 py-4 ${
                msg.sender === 'user'
                  ? 'bg-ink text-white rounded-tr-sm'
                  : 'bg-white text-ink rounded-tl-sm border border-mist shadow-sm'
              }`}
            >
              <div
                className={`prose prose-sm max-w-none leading-relaxed prose-p:my-1.5 prose-headings:font-display ${
                  msg.sender === 'user' ? 'prose-invert text-white' : 'text-ink'
                }`}
              >
                <ReactMarkdown>{msg.text}</ReactMarkdown>
              </div>

              {msg.references && msg.references.length > 0 && (
                <div className="mt-4 pt-3.5 border-t border-mist">
                  <div className="flex items-center gap-1.5 text-[11px] font-bold text-ink/40 mb-2.5 uppercase tracking-wider">
                    <BookOpen size={13} />
                    <span>Fontes no catálogo</span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {msg.references.map((ref) => (
                      <div
                        key={ref.id}
                        className="bg-mist/50 border-l-2 border-globo-violet px-3 py-2 rounded-r-lg text-xs"
                      >
                        <span className="font-semibold text-ink block truncate">
                          {ref.titulo}
                        </span>
                        <span className="text-ink/50 block text-[11px] mt-0.5">
                          {Array.isArray(ref.autores) ? ref.autores.join(', ') : ref.autores}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {msg.sender === 'user' && (
              <div className="w-8 h-8 rounded-lg bg-mist text-ink/50 flex items-center justify-center shrink-0">
                <User size={16} />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex gap-3 items-center">
            <div className="w-8 h-8 rounded-lg bg-globo-gradient text-white flex items-center justify-center shrink-0">
              <Bot size={16} />
            </div>
            <div className="bg-white border border-mist px-5 py-3.5 rounded-2xl rounded-tl-sm shadow-sm flex items-center gap-3 overflow-hidden">
              <div className="relative w-16 h-1.5 bg-mist rounded-full overflow-hidden">
                <div className="stripe-loader absolute inset-y-0 w-1/3 bg-globo-gradient rounded-full" />
              </div>
              <span className="text-sm text-ink/50">Consultando o catálogo…</span>
            </div>
          </div>
        )}
        <div ref={scrollRef} />
      </main>

      {/* Input */}
      <footer className="px-4 md:px-6 py-4 bg-paper border-t border-mist">
        <form
          onSubmit={handleSend}
          className="max-w-3xl mx-auto bg-white p-1.5 rounded-2xl shadow-sm flex items-center gap-2 border border-mist focus-within:border-globo-violet/50 transition-colors"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ex: Quais livros de negócios ou biografia temos disponíveis?"
            className="flex-1 bg-transparent px-3.5 py-2.5 text-sm focus:outline-none text-ink placeholder-ink/35"
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="bg-globo-gradient disabled:opacity-35 text-white w-10 h-10 rounded-xl flex items-center justify-center transition-all active:scale-95 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-globo-violet"
            aria-label="Enviar pergunta"
          >
            <Send size={16} />
          </button>
        </form>
      </footer>
    </div>
  );
}