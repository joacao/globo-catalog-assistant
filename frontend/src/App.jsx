import React, { useState } from 'react';
import { askQuestion } from './services/api';
import ReactMarkdown from 'react-markdown';
import { Send, BookOpen, Bot, User, Loader2, Database } from 'lucide-react';

export default function App() {
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: 'Olá! Sou o Assistente de Curadoria do Catálogo da Editora Globo. Como posso ajudar a sua equipe editorial hoje?',
      references: []
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { sender: 'user', text: userMessage }]);
    setLoading(true);

    try {
      const data = await askQuestion(userMessage);
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
          text: 'Ocorreu um erro ao consultar a base do catálogo. Por favor, tente novamente.',
          references: []
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    // 60% PRIMÁRIA: Fundo neutro corporativo (bg-slate-100)
    <div className="flex flex-col h-screen bg-slate-100 text-slate-800">
      
      {/* 30% SECUNDÁRIA: Header Grafite Escuro com Tipografia Prateada */}
      <header className="bg-slate-900 border-b border-slate-800 px-6 py-4 shadow-md text-white">
        <div className="max-w-5xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            {/* Logo textual no padrão metálico / prateado */}
            <div className="border border-slate-700 bg-slate-800/80 px-3 py-1 rounded-lg text-slate-100 font-black text-sm tracking-wider uppercase">
              EDITORA <span className="text-sky-400">GLOBO</span>
            </div>
            <div className="h-6 w-px bg-slate-700 hidden sm:block"></div>
            <div>
              <h1 className="text-base font-bold leading-tight text-slate-100">
                Curadoria de Catálogo
              </h1>
              <p className="text-xs text-slate-400">
                Sistema Interno de Recuperação Semântica (RAG)
              </p>
            </div>
          </div>
          
          {/* 10% ACENTO: Indicador Ativo com detalhe em Azul Globo */}
          <div className="hidden sm:flex items-center gap-2 bg-slate-800/90 border border-slate-700 text-slate-300 text-xs px-3 py-1.5 rounded-full font-medium">
            <Database size={14} className="text-sky-400" />
            <span>200 Obras Indexadas</span>
          </div>
        </div>
      </header>

      {/* Área Principal de Chat */}
      <main className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6 max-w-4xl mx-auto w-full">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex gap-3 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.sender === 'bot' && (
              // 10% ACENTO: Ícone do bot em Azul Globo
              <div className="w-9 h-9 rounded-xl bg-[#0054a6] text-white flex items-center justify-center shrink-0 shadow-sm">
                <Bot size={20} />
              </div>
            )}

            {/* 30% SECUNDÁRIA: Cards de Leitura em Branco Puro com Bordas Neutras */}
            <div
              className={`max-w-[85%] rounded-2xl p-5 shadow-sm ${
                msg.sender === 'user'
                  ? 'bg-slate-900 text-white rounded-tr-none'
                  : 'bg-white text-slate-800 rounded-tl-none border border-slate-200'
              }`}
            >
              <div className="prose prose-slate max-w-none text-sm leading-relaxed">
                <ReactMarkdown>{msg.text}</ReactMarkdown>
              </div>

              {/* Referências de Livros */}
              {msg.references && msg.references.length > 0 && (
                <div className="mt-5 pt-4 border-t border-slate-100">
                  <div className="flex items-center gap-1.5 text-xs font-bold text-slate-500 mb-3 uppercase tracking-wider">
                    <BookOpen size={14} className="text-[#0054a6]" />
                    <span>Fontes Utilizadas no Catálogo:</span>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {msg.references.map((ref) => (
                      <div
                        key={ref.id}
                        className="bg-slate-50 border border-slate-200 p-3 rounded-lg text-xs hover:border-slate-300 transition-colors"
                      >
                        <span className="font-bold text-slate-800 block truncate">
                          {ref.titulo}
                        </span>
                        <span className="text-slate-500 block text-[11px] mt-0.5">
                          {Array.isArray(ref.autores) ? ref.autores.join(', ') : ref.autores}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {msg.sender === 'user' && (
              <div className="w-9 h-9 rounded-xl bg-slate-800 text-white flex items-center justify-center shrink-0 shadow-sm">
                <User size={20} />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex gap-3 items-center">
            <div className="w-9 h-9 rounded-xl bg-[#0054a6] text-white flex items-center justify-center shrink-0 shadow-sm">
              <Bot size={20} />
            </div>
            <div className="bg-white border border-slate-200 px-5 py-3.5 rounded-2xl rounded-tl-none shadow-sm flex items-center gap-3">
              <Loader2 size={18} className="animate-spin text-[#0054a6]" />
              <span className="text-sm font-medium text-slate-600">
                Pesquisando no catálogo e formatando a resposta...
              </span>
            </div>
          </div>
        )}
      </main>

      {/* Input de Mensagem */}
      <footer className="p-4 md:p-6 bg-slate-100 border-t border-slate-200/80">
        <form
          onSubmit={handleSend}
          className="max-w-4xl mx-auto bg-white p-2 rounded-2xl shadow-sm flex items-center gap-2 border border-slate-200"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ex: Quais livros de negócios ou biografia temos disponíveis?"
            className="flex-1 bg-transparent px-4 py-2.5 text-sm focus:outline-none text-slate-800 placeholder-slate-400"
          />
          
          {/* 10% ACENTO: Botão de Envio em Azul Globo (#0054a6) */}
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="bg-[#0054a6] hover:bg-[#004080] disabled:opacity-40 text-white px-5 py-2.5 rounded-xl flex items-center justify-center gap-2 transition-all font-semibold text-sm shadow-sm active:scale-95"
          >
            <span>Consultar</span>
            <Send size={16} />
          </button>
        </form>
      </footer>
    </div>
  );
}