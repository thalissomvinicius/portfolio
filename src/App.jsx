import React, { useState } from 'react';
import {
  Terminal,
  Cpu,
  Layout,
  FileText,
  CheckCircle2,
  ArrowRight,
  Github,
  Linkedin,
  Mail,
  Code2,
  Database,
  BarChart3,
  Briefcase,
  Layers,
  ExternalLink,
  ChevronDown,
  Monitor,
  Wrench,
  Smartphone,
  Send,
  MessageSquare,
  MapPin,
  Phone,
  Menu,
  X
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const Section = ({ children, className, id }) => (
  <motion.section
    id={id}
    initial={{ opacity: 0, y: 30 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    transition={{ duration: 0.8 }}
    className={`py-12 md:py-24 px-4 md:px-6 max-w-7xl mx-auto ${className}`}
  >
    {children}
  </motion.section>
);

const ProjectCard = ({ title, before, after, tags, icon: Icon, features, link, timeSaved }) => (
  <div className="glass-card p-6 md:p-8 rounded-[1.5rem] md:rounded-[2.5rem] hover:border-blue-500/50 transition-all duration-500 group flex flex-col h-full">
    <div className="flex justify-between items-start mb-6">
      <div className="w-14 h-14 rounded-2xl bg-blue-500/10 flex items-center justify-center group-hover:scale-110 transition-transform">
        <Icon className="w-8 h-8 text-blue-400" />
      </div>
      <div className="flex flex-wrap gap-2 justify-end max-w-[60%]">
        {timeSaved && (
          <span className="px-3 py-1 rounded-full text-[10px] font-black bg-green-500/20 border border-green-500/30 text-green-400 uppercase tracking-wider">
            ⏱️ {timeSaved}
          </span>
        )}
      </div>
    </div>

    <h3 className="text-xl md:text-2xl font-bold mb-6 text-white">{title}</h3>

    <div className="space-y-4 mb-8 flex-grow">
      <div className="bg-red-500/5 border border-red-500/10 p-4 rounded-2xl">
        <span className="text-[10px] font-black text-red-400 uppercase tracking-widest block mb-1">Como era (Antes)</span>
        <p className="text-sm text-slate-400 italic">"{before}"</p>
      </div>
      <div className="bg-green-500/5 border border-green-500/10 p-4 rounded-2xl">
        <span className="text-[10px] font-black text-green-400 uppercase tracking-widest block mb-1">Impacto (Depois)</span>
        <p className="text-sm text-slate-200">{after}</p>
      </div>
    </div>

    <ul className="space-y-2 mb-8">
      {features.map((f, i) => (
        <li key={i} className="flex items-center gap-2 text-xs text-slate-500">
          <div className="w-1 h-1 rounded-full bg-blue-500"></div>
          {f}
        </li>
      ))}
    </ul>

    <div className="flex flex-wrap gap-2 mt-auto items-center justify-between">
      <div className="flex flex-wrap gap-2">
        {tags.map(tag => (
          <span key={tag} className="px-2 py-1 rounded-md text-[9px] font-medium bg-slate-800 text-slate-400">
            {tag}
          </span>
        ))}
      </div>
      {link && (
        <a
          href={link}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold uppercase tracking-wider transition-colors"
        >
          Ver Demo <ExternalLink className="w-3 h-3" />
        </a>
      )}
    </div>
  </div>
);

// Componente Terminal Interativo
const TerminalModal = ({ isOpen, onClose }) => {
  const [input, setInput] = useState('');
  const [history, setHistory] = useState([
    { type: 'system', content: 'Bem-vindo ao Terminal do Portfólio v1.0.0' },
    { type: 'system', content: 'Digite "help" para ver os comandos disponíveis.' }
  ]);
  const inputRef = React.useRef(null);
  const bottomRef = React.useRef(null);

  React.useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  React.useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history]);

  const handleCommand = (cmd) => {
    const args = cmd.trim().toLowerCase().split(' ');
    const command = args[0];

    let output = '';

    const projectDetails = {
      1: {
        name: "VallePrime (Disponibilidades)",
        desc: "Sistema web em tempo real para vendas e orçamento.",
        stack: "React, Vite, API REST, SQL Server",
        link: "https://valleprime.vercel.app"
      },
      2: {
        name: "DocPrint (Portal Corretor)",
        desc: "Portal para recorte e organização de documentos.",
        stack: "React, Tailwind, Framer Motion",
        link: "https://docprint.netlify.app"
      },
      3: {
        name: "Gestor de Lançamentos (War Room)",
        desc: "Sistema centralizado para controle de lançamentos imobiliários.",
        stack: "Streamlit, Python, SQL Server",
        link: null
      },
      4: {
        name: "Pixel-Perfect (Propostas PDF)",
        desc: "Geração de propostas PDF milimetricamente alinhadas.",
        stack: "Python, ReportLab",
        link: null
      }
    };

    switch (command) {
      case 'help':
        output = `Comandos disponíveis:
  - about: Sobre mim
  - skills: Minhas habilidades
  - projects: Listar projetos
  - code [n]: Ver amostra de código do projeto
  - 1, 2, 3...: Ver detalhes do projeto
  - open [n]: Abrir projeto no navegador
  - contact: Contatos
  - clear: Limpar terminal
  - exit: Fechar terminal`;
        break;
      case 'code':
      case 'cat':
        const codeNum = args[1];
        const snippets = {
          1: `// Snippet: VallePrime (Real-time Availability)
const fetchAvailability = async (obraId) => {
  const res = await fetch(\`\${API_URL}/lotes/\${obraId}\`);
  const data = await res.json();
  // Atualiza o estado global com os novos status
  setLotes(data.map(lote => ({
    id: lote.ID,
    status: STATUS_MAP[lote.SITUACAO],
    valor: lote.VALOR_VEND
  })));
};`,
          2: `// Snippet: DocPrint (Image Processing)
const processDocument = async (image) => {
  const canvas = document.createElement('canvas');
  const ctx = canvas.getContext('2d');
  // Aplica filtros para melhorar legibilidade (Preto e Branco)
  ctx.filter = 'grayscale(100%) contrast(120%)';
  ctx.drawImage(image, 0, 0);
  return canvas.toDataURL('image/jpeg', 0.8);
};`,
          3: `/* Snippet: War Room (SQL Financial Logic) */
SELECT 
    v.ID_VENDA,
    c.NOME_CLIENTE,
    SUM(p.VALOR_PARCELA) as TOTAL_PAGO
FROM VENDAS v
INNER JOIN CLIENTES c ON v.ID_CLI = c.ID
LEFT JOIN PARCELAS p ON v.ID_VENDA = p.ID_VENDA
WHERE p.STATUS = 'RECEBIDA'
GROUP BY v.ID_VENDA, c.NOME_CLIENTE;`,
          4: `# Snippet: Pixel-Perfect (Python Coordinate Mapping)
def draw_proposal(c, data):
    # Coordenadas mapeadas via JSON para precisão milimétrica
    c.setFont("Helvetica-Bold", 10)
    c.drawString(105, 752, data['cliente_nome'])
    c.drawString(450, 752, data['cpf_cnpj'])
    # Checkbox inteligente baseado no status
    if data['tipo_pagamento'] == 'SINAL':
        draw_check(c, 45, 612)`
        };

        if (snippets[codeNum]) {
          output = snippets[codeNum];
        } else {
          output = 'Use: code [numero do projeto] (ex: code 1)';
        }
        break;
      case 'about':
        output = 'Thalissom Vinicius | Dev Junior & Especialista em Automação. Foco em resolver problemas reais de negócios com código.';
        break;
      case 'skills':
        output = `Technologias:
  [Frontend] React, Tailwind, Framer Motion
  [Backend] Python, FastAPI, C# (.NET)
  [Database] SQL Server
  [Tools] Git, VS Code, Vercel`;
        break;
      case 'projects':
        output = `Projetos Principais (Digite o número para ver detalhes):
  1. VallePrime (Disponibilidades) [Live Demo]
  2. DocPrint (Portal Corretor) [Live Demo]
  3. Gestor de Lançamentos (War Room)
  4. Pixel-Perfect (Propostas PDF)`;
        break;
      case '1':
      case '2':
      case '3':
      case '4':
        const p = projectDetails[command];
        output = `PROJETO #${command}: ${p.name}
----------------------------------------
${p.desc}
Tech: ${p.stack}
${p.link ? `\n[!] Digite "open ${command}" para abrir o projeto.` : ''}`;
        break;
      case 'open':
        const projNum = args[1];
        if (projectDetails[projNum] && projectDetails[projNum].link) {
          window.open(projectDetails[projNum].link, '_blank');
          output = `Abrindo ${projectDetails[projNum].name}...`;
        } else if (projectDetails[projNum]) {
          output = `O projeto ${projectDetails[projNum].name} não possui link público.`;
        } else {
          output = 'Projeto não encontrado ou número inválido. Use: open [numero]';
        }
        break;
      case 'contact':
        output = `WhatsApp: 91 99169-7664
GitHub: github.com/thalissomvinicius`;
        break;
      case 'clear':
        setHistory([]);
        return;
      case 'exit':
        onClose();
        return;
      default:
        output = `Comando não encontrado: ${command}. Digite "help" para ajuda.`;
    }

    setHistory(prev => [...prev, { type: 'user', content: cmd }, { type: 'system', content: output }]);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim()) return;
    handleCommand(input);
    setInput('');
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-[60] flex items-center justify-center p-0 md:p-4">
      <div className="w-full h-full md:h-auto md:max-w-2xl bg-[#1a1b26] rounded-none md:rounded-xl shadow-2xl overflow-hidden border-0 md:border md:border-slate-700 font-mono text-sm relative">
        {/* Header do Terminal */}
        <div className="bg-[#16161e] px-4 py-2 flex items-center justify-between border-b border-slate-800">
          <div className="flex gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500 cursor-pointer" onClick={onClose}></div>
            <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
          </div>
          <div className="text-slate-400 text-xs">user@thalissom-portfolio:~</div>
          <div className="w-4"></div>
        </div>

        {/* Corpo do Terminal */}
        <div className="p-4 h-[calc(100%-80px)] md:h-[400px] overflow-y-auto text-slate-300" onClick={() => inputRef.current?.focus()}>
          {history.map((line, i) => (
            <div key={i} className={`mb-2 ${line.type === 'user' ? 'text-blue-400' : 'text-green-400 whitespace-pre-wrap'}`}>
              {line.type === 'user' ? <span className="mr-2 text-pink-500">➜ ~</span> : null}
              {line.content}
            </div>
          ))}

          <form onSubmit={handleSubmit} className="flex items-center gap-2 mt-2">
            <span className="text-pink-500">➜ ~</span>
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="flex-1 bg-transparent border-none outline-none text-blue-400 placeholder-slate-600"
              autoFocus
            />
          </form>
          <div ref={bottomRef}></div>
        </div>
      </div>
    </div>
  );
};

// Custom Cursor Component (Optimized)

// Componente Currículo (Print-Friendly)
const ResumeModal = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col items-center py-10 px-4 print:p-0 print:bg-white overflow-y-auto cursor-auto">

      {/* Barra de Ações Superior (Oculta na impressão) */}
      <div className="fixed top-0 left-0 w-full bg-slate-950 border-b border-slate-800 p-3 md:p-4 flex flex-col sm:flex-row justify-between items-center gap-3 z-[100] print:hidden shadow-2xl">
        <h2 className="text-white font-bold flex items-center gap-2 text-sm md:text-base">
          <FileText className="w-5 h-5 text-blue-500" /> Currículo
        </h2>
        <div className="flex gap-2 w-full sm:w-auto">
          <button
            onClick={() => window.print()}
            className="flex-1 sm:flex-none bg-blue-600 text-white px-4 md:px-6 py-2 rounded-xl text-xs md:text-sm font-bold hover:bg-blue-500 transition-all flex items-center justify-center gap-2"
          >
            <FileText className="w-4 h-4" /> PDF
          </button>
          <button
            onClick={onClose}
            className="flex-1 sm:flex-none bg-slate-800 text-white px-4 md:px-6 py-2 rounded-xl text-xs md:text-sm font-bold hover:bg-slate-700 transition-all"
          >
            Sair
          </button>
        </div>
      </div>

      <div className="bg-white text-slate-900 w-full max-w-[210mm] min-h-screen p-8 md:p-[15mm] flex flex-col mt-28 sm:mt-20 print:mt-0 shadow-none mb-10 h-auto rounded-none sm:rounded-xl">

        <header className="border-b-2 border-slate-900 pb-8 mb-8 flex flex-col md:flex-row items-center gap-6 md:gap-8 text-center md:text-left">
          <div className="w-24 h-24 md:w-32 md:h-32 shrink-0 rounded-full border-2 border-slate-200 overflow-hidden">
            <img
              src="photo_profile.png"
              alt="Thalissom Vinicius"
              className="w-full h-full object-cover block"
            />
          </div>
          <div>
            <h1 className="text-3xl md:text-4xl font-black uppercase tracking-tighter mb-1 text-slate-900">Thalissom Vinicius</h1>
            <p className="text-base md:text-lg font-bold text-blue-600 mb-3 tracking-wide">Especialista em Logística, Automação & Negócios</p>
            <div className="flex flex-col md:flex-row flex-wrap gap-x-6 gap-y-2 text-[10px] md:text-xs font-medium text-slate-500 items-center justify-center md:justify-start">
              <span className="flex items-center gap-1.5"><MapPin className="w-3 h-3 text-blue-500" /> Tomé-Açu - PA</span>
              <span className="flex items-center gap-1.5"><Mail className="w-3 h-3 text-blue-500" /> vinicius.devcode.br@gmail.com</span>
              <span className="flex items-center gap-1.5"><Phone className="w-3 h-3 text-blue-500" /> (91) 99169-7664</span>
            </div>
            <div className="mt-2 text-[10px] md:text-xs font-medium text-slate-400 flex items-center gap-1.5 justify-center md:justify-start">
              <Github className="w-3 h-3" /> github.com/thalissomvinicius
            </div>
          </div>
        </header>

        {/* Resumo */}
        <section className="mb-8">
          <h2 className="text-sm font-black uppercase tracking-widest text-blue-600 mb-4 border-b-2 border-blue-100 pb-2">Perfil Profissional</h2>
          <p className="text-slate-700 leading-relaxed text-justify">
            Profissional com 6 anos de experiência na Valle Empreendimentos, com forte atuação em organização de processos e gestão de fluxos.
            Especialista em transformar controles manuais e burocráticos (estoque, fiscal, administrativo) em soluções de alta performance.
            Une sólida vivência administrativa e contábil com domínio em organização logística e automação de dados.
            Foco total em eficiência: garantir que cada item esteja no lugar certo e que cada processo seja rastreável e otimizado.
          </p>
        </section>

        {/* Projetos de Impacto */}
        <section className="mb-8">
          <h2 className="text-sm font-black uppercase tracking-widest text-blue-600 mb-6 border-b-2 border-blue-100 pb-2">Projetos de Impacto</h2>

          <div className="space-y-6">
            <div>
              <div className="flex justify-between items-baseline mb-1">
                <h3 className="font-bold text-lg text-slate-900">Gestor de Lançamentos (War Room)</h3>
                <span className="text-xs font-bold text-green-600 bg-green-100 px-2 py-0.5 rounded-full">Gestão 100% Automática</span>
              </div>
              <p className="text-sm text-slate-600 mb-2 font-medium">Python, Streamlit, SQL Server, ReportLab</p>
              <ul className="list-disc list-outside ml-4 text-sm text-slate-700 space-y-1">
                <li>Complemento estratégico ao ERP UAU (GlobalTEC): entrega os dados e relatórios que o sistema padrão não supre.</li>
                <li>Dashboards dinâmicos e controle total de boletos/lançamentos financeiros.</li>
              </ul>
            </div>

            <div>
              <div className="flex justify-between items-baseline mb-1">
                <h3 className="font-bold text-lg text-slate-900">Sistema de Disponibilidades (VallePrime)</h3>
                <span className="text-xs font-bold text-green-600 bg-green-100 px-2 py-0.5 rounded-full">400+ Acessos/Semana</span>
              </div>
              <p className="text-sm text-slate-600 mb-2 font-medium">React, Vite, SQL Server</p>
              <ul className="list-disc list-outside ml-4 text-sm text-slate-700 space-y-1">
                <li>Plataforma real-time que revolucionou a comunicação externa com corretores.</li>
                <li>Obteve tração imediata com centenas de requisições na primeira semana.</li>
              </ul>
            </div>

            <div>
              <div className="flex justify-between items-baseline mb-1">
                <h3 className="font-bold text-lg text-slate-900">Portal do Corretor (DocPrint)</h3>
                <span className="text-xs font-bold text-green-600 bg-green-100 px-2 py-0.5 rounded-full">Economia: 3h/dia</span>
              </div>
              <p className="text-sm text-slate-600 mb-2 font-medium">React, Tailwind, Framer Motion</p>
              <ul className="list-disc list-outside ml-4 text-sm text-slate-700 space-y-1">
                <li>Recorte inteligente e organização de documentos, padronizando a análise de crédito.</li>
              </ul>
            </div>

            <div>
              <div className="flex justify-between items-baseline mb-1">
                <h3 className="font-bold text-lg text-slate-900">Pixel-Perfect (Python)</h3>
                <span className="text-xs font-bold text-green-600 bg-green-100 px-2 py-0.5 rounded-full">ROI Instantâneo</span>
              </div>
              <p className="text-sm text-slate-700">Script para geração automática de propostas PDF com precisão milimétrica em segundos.</p>
            </div>
          </div>
        </section>

        {/* Experiência */}
        <section className="mb-8">
          <h2 className="text-sm font-black uppercase tracking-widest text-blue-600 mb-6 border-b-2 border-blue-100 pb-2">Experiência Profissional</h2>

          <div className="mb-6">
            <div className="flex justify-between items-baseline">
              <h3 className="font-bold text-lg text-slate-900">Valle Empreendimentos</h3>
              <span className="text-sm font-medium text-slate-500">07/2020 - Presente</span>
            </div>
            <p className="font-medium text-blue-600 text-sm mb-2">Auxiliar Administrativo & Logística (Atuação: Gestão de Fluxos / Automação)</p>
            <p className="text-sm text-slate-700 text-justify">
              Atuação estratégica na organização de fluxos internos e transformação de processos manuais em automação.
              Responsável pela gestão de bases de dados, controle de lançamentos e otimização da logística de documentos e materiais da empresa.
              Forte habilidade na conferência de notas fiscais e conformidade com processos contábeis/administrativos.
            </p>
          </div>

          <div className="mb-4">
            <div className="flex justify-between items-baseline">
              <h3 className="font-bold text-lg text-slate-900">Técnico de Informática (Autônomo)</h3>
              <span className="text-sm font-medium text-slate-500">2019 - Presente</span>
            </div>
            <p className="font-medium text-blue-600 text-sm mb-2">Suporte, Redes e Segurança</p>
            <p className="text-sm text-slate-700 text-justify">
              Atuação autônoma na manutenção de hardware/software e configuração de redes.
              Uso de conhecimentos em <strong>Ethical Hacking</strong> para auditoria e reforço da segurança digital de clientes.
            </p>
          </div>
        </section>

        {/* Grid para Formação e Stack */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">

          <div className="space-y-6">
            {/* Formação */}
            <section>
              <h2 className="text-sm font-black uppercase tracking-widest text-blue-600 mb-4 border-b-2 border-blue-100 pb-2">Formação Acadêmica</h2>
              <div className="space-y-2">
                <div>
                  <h3 className="font-bold text-sm text-slate-900 line-clamp-1">Ensino Superior (Incompleto)</h3>
                  <p className="text-xs text-slate-600">Ciências Contábeis</p>
                </div>
                <div>
                  <h3 className="font-bold text-sm text-slate-900">Ensino Médio Completo</h3>
                </div>
              </div>
            </section>

            {/* Habilidades Práticas */}
            <section>
              <h2 className="text-sm font-black uppercase tracking-widest text-blue-600 mb-4 border-b-2 border-blue-100 pb-2">Habilidades Práticas</h2>
              <ul className="text-xs text-slate-600 space-y-1 text-justify">
                <li>• <strong>Organização:</strong> Gestão de estoques e fluxos de materiais/documentos.</li>
                <li>• <strong>Comunicação:</strong> Habilidade no trato com fornecedores e equipes internas.</li>
                <li>• <strong>Proatividade:</strong> Resolução ágil de problemas e otimização de rotinas.</li>
              </ul>
            </section>
          </div>

          <div className="space-y-6">
            {/* Cursos */}
            <section>
              <h2 className="text-sm font-black uppercase tracking-widest text-blue-600 mb-4 border-b-2 border-blue-100 pb-2">Cursos & Certificações</h2>
              <div className="space-y-2">
                <div>
                  <h3 className="font-bold text-xs text-slate-900">Python & Análise de Dados</h3>
                  <p className="text-[10px] text-slate-500 leading-tight mt-1">
                    Automação, Pandas, Numpy, SQL e Visualização de Dados.
                  </p>
                </div>
                <div>
                  <h3 className="font-bold text-xs text-slate-900">Desenvolvimento Web Completo</h3>
                  <p className="text-[10px] text-slate-500 leading-tight mt-1">
                    HTML5, CSS3, Javascript, PHP, MySQL, Ajax, JQuery, Git.
                  </p>
                </div>
                <div className="flex flex-wrap gap-x-3 text-xs text-slate-700 font-medium">
                  <span>• Hardware & Redes</span>
                  <span>• Pacote Office Avançado</span>
                  <span>• Inglês Básico</span>
                </div>
              </div>
            </section>

            {/* Stack Resumo */}
            <section>
              <h2 className="text-sm font-black uppercase tracking-widest text-blue-600 mb-4 border-b-2 border-blue-100 pb-2">Stack Principal</h2>
              <div className="flex flex-wrap gap-1">
                {['React', 'Vite', 'Python', 'SQL Server', 'Tailwind', 'Git'].map(tech => (
                  <span key={tech} className="px-2 py-1 bg-slate-100 rounded text-[10px] font-bold text-slate-700">
                    {tech}
                  </span>
                ))}
              </div>
            </section>
          </div>

        </div>
      </div>
    </div>
  );
};

const App = () => {
  const [activeTab, setActiveTab] = useState('tech');
  const [isTerminalOpen, setIsTerminalOpen] = useState(false);
  const [isResumeOpen, setIsResumeOpen] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  // Easter Egg: Atalho de teclado (Ctrl + K)
  React.useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setIsTerminalOpen(prev => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  if (isResumeOpen) {
    return <ResumeModal isOpen={true} onClose={() => setIsResumeOpen(false)} />;
  }

  return (
    <div className="bg-[#050507] min-h-screen text-slate-200 selection:bg-blue-500/30 overflow-x-hidden">
      <TerminalModal isOpen={isTerminalOpen} onClose={() => setIsTerminalOpen(false)} />

      <div className="print:hidden">
        {/* Botão Flutuante do Terminal */}
        <motion.button
          onClick={() => setIsTerminalOpen(true)}
          className="fixed bottom-6 right-6 z-40 w-14 h-14 bg-slate-900/80 backdrop-blur-md border border-slate-700 rounded-full flex items-center justify-center text-green-400 shadow-2xl hover:scale-110 transition-transform hover:bg-slate-800 group"
          whileHover={{ rotate: 15 }}
        >
          <Terminal className="w-6 h-6" />
          <span className="absolute right-full mr-4 px-3 py-1 bg-slate-800 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap border border-slate-700">
            Abrir Terminal (Ctrl+K)
          </span>
        </motion.button>

        {/* Navbar */}
        <nav className="fixed top-0 w-full z-50 glass border-b border-white/5 bg-[#0a0a0c]/80 backdrop-blur-xl">
          <div className="max-w-7xl mx-auto px-4 md:px-6 py-4 flex justify-between items-center">
            <div className="text-xl md:text-2xl font-black tracking-tighter flex items-center gap-2 shrink-0">
              THALISSOM<span className="text-blue-500">VINICIUS</span>
            </div>

            <div className="hidden md:flex gap-8 text-sm font-medium text-slate-400">
              <a href="#home" className="hover:text-blue-400 transition-colors uppercase tracking-widest">Início</a>
              <a href="#about" className="hover:text-blue-400 transition-colors uppercase tracking-widest">Perfil</a>
              <a href="#projects" className="hover:text-blue-400 transition-colors uppercase tracking-widest">Projetos</a>
              <a href="#experience" className="hover:text-blue-400 transition-colors uppercase tracking-widest">Habilidades</a>
              <button onClick={() => setIsResumeOpen(true)} className="hover:text-blue-400 transition-colors uppercase tracking-widest">
                Currículo
              </button>
            </div>

            <div className="flex items-center gap-2 md:gap-4">
              <span className="text-[10px] font-black text-slate-600 hidden lg:block uppercase tracking-[0.2em]">Assinatura: <span className="text-blue-500">Vinicius Dev</span></span>
              <a href="https://wa.me/5591991697664" target="_blank" className="xs:inline-flex btn-primary py-2 px-3 md:px-5 text-[10px] md:text-sm uppercase tracking-wider flex items-center gap-2">
                <MessageSquare className="w-4 h-4" />
                <span className="hidden md:inline">Whatsapp</span>
              </a>
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="md:hidden text-white p-2 hover:bg-white/5 rounded-lg transition-colors"
                aria-label="Menu"
              >
                {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
              </button>
            </div>
          </div>

          {/* Mobile Menu Overlay */}
          <AnimatePresence>
            {isMenuOpen && (
              <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="md:hidden border-t border-white/5 bg-[#0a0a0c]/95 backdrop-blur-xl overflow-hidden"
              >
                <div className="flex flex-col p-8 gap-6 text-center text-base font-bold uppercase tracking-[0.2em]">
                  <a href="#home" onClick={() => setIsMenuOpen(false)} className="text-slate-100 hover:text-blue-500 transition-colors py-2">Início</a>
                  <a href="#about" onClick={() => setIsMenuOpen(false)} className="text-slate-100 hover:text-blue-500 transition-colors py-2">Perfil</a>
                  <a href="#projects" onClick={() => setIsMenuOpen(false)} className="text-slate-100 hover:text-blue-500 transition-colors py-2">Projetos</a>
                  <a href="#experience" onClick={() => setIsMenuOpen(false)} className="text-slate-100 hover:text-blue-500 transition-colors py-2">Habilidades</a>
                  <button
                    onClick={() => { setIsResumeOpen(true); setIsMenuOpen(false); }}
                    className="text-slate-100 hover:text-blue-400 transition-colors uppercase py-2 font-bold tracking-[0.2em]"
                  >
                    Currículo
                  </button>
                  <a href="https://wa.me/5591991697664" target="_blank" className="btn-primary py-4 px-6 justify-center mt-4 text-sm flex items-center gap-2">
                    <MessageSquare className="w-5 h-5" />
                    <span className="hidden sm:inline">Fale no Whatsapp</span>
                  </a>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </nav>

        {/* Seção Hero */}
        <section id="home" className="pt-32 pb-20 px-6 min-h-screen flex items-center justify-center relative overflow-hidden">
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full -z-10 bg-[radial-gradient(circle_at_center,rgba(59,130,246,0.08),transparent_70%)]"></div>

          <div className="w-full max-w-6xl mx-auto grid md:grid-cols-2 gap-12 items-center px-4">
            {/* Foto - Lado Esquerdo */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1 }}
              className="flex justify-center md:justify-start order-1 md:order-none"
            >
              <div className="relative">
                <div className="absolute inset-0 bg-blue-500 rounded-full blur-3xl opacity-20 animate-pulse scale-110"></div>
                <img
                  src="photo_profile.png"
                  alt="Thalissom Vinicius"
                  className="w-56 h-56 md:w-80 md:h-80 rounded-full border-4 border-white/10 shadow-2xl relative z-10 object-cover object-center"
                />
              </div>
            </motion.div>

            {/* Texto - Lado Direito */}
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 1 }}
              className="text-center md:text-left md:-ml-20 z-10"
            >
              <div className="inline-flex items-center gap-2 px-6 py-2 rounded-full glass mb-6 text-blue-400 text-[10px] font-black uppercase tracking-[0.3em] border-blue-500/20 mx-auto md:mx-0">
                <span className="w-2 h-2 rounded-full bg-blue-500 animate-ping"></span>
                Em Busca de Desafios
              </div>
              <h1 className="text-4xl md:text-7xl font-black mb-6 tracking-tighter leading-tight md:leading-none">
                Desenvolvedor <br />
                <span className="text-gradient">com Visão de Negócios.</span>
              </h1>
              <p className="text-base md:text-lg text-slate-400 max-w-xl mb-8 leading-relaxed font-light mx-auto md:mx-0">
                Especialista em organização e automação de fluxos.
                Há 6 anos otimizando processos logísticos e administrativos na Valle Empreendimentos.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center md:justify-start items-center md:items-start">
                <a href="#projects" className="w-full sm:w-auto btn-primary text-base md:text-lg px-8 rounded-2xl justify-center">
                  Explorar Projetos <ArrowRight className="w-5 h-5" />
                </a>
                <a href="https://github.com/thalissomvinicius" target="_blank" className="w-full sm:w-auto btn-secondary text-base md:text-lg px-8 rounded-2xl justify-center">
                  GitHub <Github className="w-5 h-5" />
                </a>
              </div>
            </motion.div>
          </div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1, duration: 1 }}
            className="absolute bottom-10 left-1/2 -translate-x-1/2 cursor-pointer"
            onClick={() => document.getElementById('about').scrollIntoView({ behavior: 'smooth' })}
          >
            <div className="w-px h-16 bg-gradient-to-b from-blue-500 to-transparent mx-auto"></div>
          </motion.div>
        </section>

        {/* Seção Sobre */}
        <Section id="about" className="grid md:grid-cols-2 gap-12 md:gap-20 items-center">
          <div className="relative">
            <div className="absolute -top-20 -left-20 w-64 h-64 bg-blue-500/10 blur-[100px] rounded-full"></div>
            <h2 className="text-3xl md:text-5xl font-black mb-8 tracking-tighter italic">"Trabalho pesado se resolve com <span className="text-blue-500">código.</span>"</h2>
            <div className="space-y-6 text-base md:text-lg text-slate-400 leading-relaxed font-light">
              <p>
                Minha trajetória na <span className="text-slate-100 font-semibold uppercase tracking-wider">Valle Empreendimentos</span> é marcada pela proatividade. Embora atue formalmente no Administrativo, assumi o papel estratégico de transformar processos manuais em automação de software, elevando o patamar tecnológico da empresa.
              </p>
              <p>
                <span className="text-blue-400 font-bold block mb-2 underline decoration-blue-500/50">Formação Acadêmica:</span>
                Parei no 7º semestre de <span className="text-slate-100">Ciências Contábeis</span> e tranquei a universidade no <span className="text-slate-100 font-bold">8º semestre</span>. Esta base contábil me dá autoridade para falar de SPED, IRPJ, Conciliação e Compliance com qualquer diretor financeiro.
              </p>
              <p>
                Além de desenvolvedor, sou especialista em <span className="text-slate-100 font-semibold">Organização, Logística de Dados e Processos Administrativos</span>. Minha fome é por alavancar resultados através da ordem e da eficiência técnica.
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4 mt-12">
              <div className="glass p-6 rounded-3xl border-l-4 border-blue-500">
                <div className="text-4xl font-black text-white">06</div>
                <div className="text-[10px] text-slate-500 uppercase tracking-[0.2em] mt-2 font-bold">Anos na Mesma Empresa</div>
              </div>
              <div className="glass p-6 rounded-3xl border-l-4 border-cyan-500">
                <div className="text-4xl font-black text-white">100%</div>
                <div className="text-[10px] text-slate-500 uppercase tracking-[0.2em] mt-2 font-bold">Foco em Automação</div>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-6">
            <div className="glass-card p-8 rounded-[2rem] relative overflow-hidden group">
              <div className="flex gap-6 items-start">
                <div className="w-16 h-16 rounded-2xl bg-orange-500/10 flex items-center justify-center shrink-0">
                  <Wrench className="w-8 h-8 text-orange-400" />
                </div>
                <div>
                  <h4 className="font-black text-xl mb-2 uppercase tracking-tight">Especialista em Hardware</h4>
                  <p className="text-slate-400 text-sm leading-relaxed">Manutenção preventiva, corretiva e otimização de infraestrutura tecnológica industrial.</p>
                </div>
              </div>
            </div>
            <div className="glass-card p-8 rounded-[2rem] relative overflow-hidden group">
              <div className="flex gap-6 items-start">
                <div className="w-16 h-16 rounded-2xl bg-purple-500/10 flex items-center justify-center shrink-0">
                  <Monitor className="w-8 h-8 text-purple-400" />
                </div>
                <div>
                  <h4 className="font-black text-xl mb-2 uppercase tracking-tight">Especialista em Software</h4>
                  <p className="text-slate-400 text-sm leading-relaxed">Dev Junior, integração de APIs e gestão de bancos de dados SQL Server.</p>
                </div>
              </div>
            </div>
            <div className="glass-card p-8 rounded-[2rem] relative overflow-hidden group border-blue-500/30">
              <div className="flex gap-6 items-start">
                <div className="w-16 h-16 rounded-2xl bg-blue-500/10 flex items-center justify-center shrink-0">
                  <Layers className="w-8 h-8 text-blue-400" />
                </div>
                <div>
                  <h4 className="font-black text-xl mb-2 uppercase tracking-tight">Designer & Interface</h4>
                  <p className="text-slate-400 text-sm leading-relaxed">Criação de interfaces premium e sistemas que os usuários amam utilizar.</p>
                </div>
              </div>
            </div>
          </div>
        </Section>

        {/* Seção Projetos */}
        <Section id="projects">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-12 md:mb-16 gap-6">
            <div className="max-w-2xl">
              <div className="text-blue-500 font-black tracking-[0.4em] uppercase text-[10px] mb-4">Matriz de Resultados</div>
              <h2 className="text-4xl md:text-6xl font-black tracking-tighter">O que eu <span className="text-blue-500">resolvi.</span></h2>
            </div>
            <div className="glass px-6 py-4 rounded-2xl w-full md:w-auto text-left md:text-right">
              <p className="text-slate-500 text-[10px] font-bold uppercase tracking-widest mb-1">Métrica Global</p>
              <p className="text-white font-black text-xl md:text-2xl tracking-tighter">Redução de 80% em erros manuais</p>
            </div>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-2 gap-8">
            <ProjectCard
              title="SISTEMA DE DISPONIBILIDADES (VALLEPRIME)"
              before="Corretores recebiam a disponibilidade de lotes apenas 2x ao dia via planilhas manuais. Vendas eram perdidas por informações desatualizadas."
              after="Sistema web em tempo real que revolucionou a comunicação externa: obteve mais de 400 acessos e requisições na primeira semana de lançamento."
              tags={['React', 'Vite', 'API REST', 'SQL Server', 'Vercel']}
              icon={Monitor}
              features={['Consulta em tempo real', '400+ Acessos na primeira semana', 'Gerador de orçamentos integrado', 'Painel responsivo mobile']}
              link="https://valleprime.vercel.app"
              timeSaved="Economiza 10h/semana"
            />
            <ProjectCard
              title="PORTAL DO CORRETOR (DOCPRINT)"
              before="Corretores recebiam fotos de documentos de clientes mal enquadradas e desorganizadas. A gestão documental era caótica e lenta."
              after="Portal para recorte inteligente de imagens, organização de documentos e acompanhamento de índices de reajuste do mercado imobiliário (IGPM/IPCA)."
              tags={['React', 'Tailwind CSS', 'Framer Motion', 'jsPDF', 'Netlify']}
              icon={FileText}
              features={['Recorte inteligente de documentos', 'Organização automática por cliente', 'Monitoramento de índices IGPM/IPCA', 'Interface mobile-first']}
              link="https://docprint.netlify.app"
              timeSaved="Economiza 3h/dia"
            />
            <ProjectCard
              title="GESTOR DE LANÇAMENTOS (WAR ROOM)"
              before="O ERP padrão do mercado (UAU GlobalTEC) não supria as necessidades de visualização de dados, relatórios customizados e gestão ágil de boletos."
              after="Sistema centralizado que preenche as lacunas do ERP: dashboards com gráficos dinâmicos, controle total de boletos e relatórios financeiros instantâneos."
              tags={['Streamlit', 'Python', 'SQL Server', 'Pandas', 'ReportLab']}
              icon={Layout}
              features={['Complemento estratégico ao ERP UAU', 'Gráficos e dashboards financeiros', 'Geração automática de contratos/relatórios', 'Gestão simplificada de boletos']}
              timeSaved="Gestão 100% Automática"
            />
            <ProjectCard
              title="SISTEMA PIXEL-PERFECT (PROPOSTAS)"
              before="O setor comercial preenchia propostas manualmente em arquivos de imagem/PDF, gastando 20 min por cliente e com frequentes erros de digitação e alinhamento."
              after="Geração instantânea (milissegundos) de propostas PDF com alinhamento milimétrico, validando dados e garantindo um visual 100% profissional."
              tags={['Python', 'ReportLab', 'Mapeamento de Pixels', 'Automação PDF']}
              icon={FileText}
              features={['Mapeamento por coordenadas JSON', 'Conversão mm para pontos PDF', 'Geração de Checkboxes inteligentes', 'Alinhamento vertical automático']}
              timeSaved="20min → 5seg"
            />
            <ProjectCard
              title="DASHBOARD DE RECEBIMENTO DIÁRIO"
              before="A conciliação bancária exigia exportar múltiplos CSVs e cruzar dados manualmente em planilhas pesadas para saber o faturamento real do dia."
              after="Dashboard Dev Junior que consome direto do SQL Server, apresentando gráficos comparativos de 12 meses e exportação otimizada para Excel em um clique."
              tags={['FastAPI', 'React', 'Pandas', 'SQL Server']}
              icon={BarChart3}
              features={['Conexão em tempo real com BD', 'Gráficos de tendência financeira', 'Exportação para Excel', 'Interface moderna glassmorphism']}
              timeSaved="Economiza 2h/dia"
            />
            <ProjectCard
              title="ORGANIZADOR DE ARQUIVOS (CONTRATOS)"
              before="Milhares de arquivos de contratos e aditivos ficavam dispersos. Encontrar um documento específico levava minutos e risco de perda era alto."
              after="Script inteligente que separa e organiza documentos automaticamente por empresa (VALLE/ML), Quadra e Lote seguindo regras lógicas rígidas."
              tags={['Python', 'Sistema de Arquivos', 'Automação', 'Logística Empresarial']}
              icon={Layers}
              features={['Detecção automática de Quadra/Lote', 'Criação estruturada de pastas', 'Log de arquivamento', 'Interface desktop amigável']}
              timeSaved="Economiza 4h/semana"
            />
          </div>
        </Section>

        {/* Seção Habilidades */}
        <Section id="experience" className="bg-blue-600/5 rounded-[4rem] px-12 py-24 border border-blue-500/10 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-96 h-96 bg-blue-500/5 blur-[120px] rounded-full"></div>

          <div className="text-center mb-16">
            <h2 className="text-5xl font-black tracking-tighter mb-6">Escopo de <span className="text-blue-500">Atuação.</span></h2>
            <div className="inline-flex flex-col sm:flex-row glass p-1 rounded-2xl overflow-hidden">
              <button
                onClick={() => setActiveTab('tech')}
                className={`px-6 md:px-10 py-3 rounded-xl text-[10px] md:text-xs font-black uppercase tracking-widest transition-all ${activeTab === 'tech' ? 'bg-blue-600 shadow-xl shadow-blue-500/30 text-white' : 'text-slate-500 hover:text-slate-100'}`}
              >
                Tecnologia & T.I
              </button>
              <button
                onClick={() => setActiveTab('adm')}
                className={`px-6 md:px-10 py-3 rounded-xl text-[10px] md:text-xs font-black uppercase tracking-widest transition-all ${activeTab === 'adm' ? 'bg-blue-600 shadow-xl shadow-blue-500/30 text-white' : 'text-slate-500 hover:text-slate-100'}`}
              >
                Gestão & Logística
              </button>
            </div>
          </div>

          <AnimatePresence mode="wait">
            {activeTab === 'tech' ? (
              <motion.div
                key="tech"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="grid md:grid-cols-3 gap-8"
              >
                <div className="glass-card p-8 rounded-3xl">
                  <Terminal className="text-blue-500 w-10 h-10 mb-6" />
                  <h4 className="font-bold text-lg mb-4 uppercase">Desenvolvimento</h4>
                  <ul className="space-y-3 text-sm text-slate-400">
                    <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-blue-500" /> Python (Automação de alto nível)</li>
                    <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-blue-500" /> C# (.NET Core / WinForms)</li>
                    <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-blue-500" /> React & TypeScript</li>
                    <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-blue-500" /> SQL Server (Consultas Otimizadas)</li>
                  </ul>
                </div>
                <div className="glass-card p-8 rounded-3xl">
                  <Cpu className="text-cyan-500 w-10 h-10 mb-6" />
                  <h4 className="font-bold text-lg mb-4 uppercase">Infraestrutura & Hardware</h4>
                  <ul className="space-y-3 text-sm text-slate-400">
                    <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-cyan-500" /> Manutenção Profissional de Hardware</li>
                    <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-cyan-500" /> Gestão de Sistemas Operacionais</li>
                    <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-cyan-500" /> Scripts de Automação PowerShell</li>
                    <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-cyan-500" /> Configuração de Redes</li>
                  </ul>
                </div>
                <div className="glass-card p-8 rounded-3xl">
                  <Layout className="text-purple-500 w-10 h-10 mb-6" />
                  <h4 className="font-bold text-lg mb-4 uppercase">Design & Ferramentas</h4>
                  <ul className="space-y-3 text-sm text-slate-400">
                    <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-purple-500" /> Design de Interface Moderno</li>
                    <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-purple-500" /> Identidade Visual</li>
                    <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-purple-500" /> Canva & Ferramentas Gráficas</li>
                    <li className="flex items-center gap-2"><CheckCircle2 className="w-4 h-4 text-purple-500" /> Github (thalissomvinicius)</li>
                  </ul>
                </div>
              </motion.div>
            ) : (
              <motion.div
                key="adm"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="grid md:grid-cols-2 gap-12"
              >
                <div className="space-y-8">
                  <h3 className="text-3xl font-black tracking-tight mb-8">Especialista em <span className="text-blue-500">Fluxos.</span></h3>
                  <div className="grid grid-cols-1 gap-4">
                    {[
                      'Organização de Estoque e Fluxo de Materiais',
                      'Conferência Rigorosa de Notas Fiscais (XML/DANFE)',
                      'Gestão de Almoxarifado Digital e Físico',
                      'Atendimento ao Cliente e Relacionamento com Fornecedores',
                      'Inventário e Controle de Patrimônio'
                    ].map(item => (
                      <div key={item} className="flex gap-4 items-center bg-white/5 p-5 rounded-2xl border border-white/5 hover:border-blue-500/30 transition-all">
                        <CheckCircle2 className="w-6 h-6 text-blue-500 shrink-0" />
                        <span className="text-slate-300 font-medium">{item}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="glass-card p-10 rounded-[3rem] border-blue-500/20 bg-blue-500/5 items-center flex flex-col justify-center text-center">
                  <div className="w-20 h-20 rounded-full bg-blue-500/20 flex items-center justify-center mb-8">
                    <Briefcase className="w-10 h-10 text-blue-400" />
                  </div>
                  <h4 className="font-black text-2xl mb-4">Quase Contador (8º Semestre)</h4>
                  <p className="text-slate-400 leading-relaxed max-w-sm">
                    Domínio de princípios contábeis, análise de balanço e compliance fiscal aplicados à automação de dados. Minha linguagem é técnica, meus resultados são contábeis.
                  </p>
                  <div className="mt-8 flex gap-2">
                    <div className="px-4 py-2 bg-blue-500/10 rounded-full text-[10px] font-black text-blue-400 uppercase tracking-widest">7/8 Semestres</div>
                    <div className="px-4 py-2 bg-blue-500/10 rounded-full text-[10px] font-black text-blue-400 uppercase tracking-widest">Contabilidade Completa</div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </Section>

        {/* Seção CTA */}
        <Section className="text-center">
          <div className="max-w-4xl mx-auto glass p-16 rounded-[4rem] border-blue-500/30 relative">
            <div className="absolute -top-10 left-1/2 -translate-x-1/2 w-20 h-20 rounded-3xl bg-blue-600 flex items-center justify-center shadow-2xl shadow-blue-500/50">
              <Send className="w-10 h-10 text-white" />
            </div>
            <h2 className="text-3xl md:text-5xl font-black mb-6 tracking-tighter mt-4">Pronto para <span className="text-blue-500">alavancar</span> seu setor?</h2>
            <p className="text-slate-400 text-base md:text-lg mb-12 max-w-2xl mx-auto">
              Seja para automatizar planilhas, gerenciar infraestrutura de T.I ou criar sistemas modernos. Vamos conversar sobre como posso acelerar sua empresa.
            </p>
            <div className="flex flex-col md:flex-row gap-6 justify-center items-center">
              <a href="https://wa.me/5591991697664" target="_blank" className="btn-primary text-xl px-12 py-5 rounded-2xl flex items-center gap-3">
                <MessageSquare className="w-6 h-6" /> 91 99169-7664
              </a>
              <div className="flex gap-4">
                <a href="mailto:vinicius.devcode.br@gmail.com" className="w-16 h-16 rounded-2xl glass flex items-center justify-center hover:bg-slate-800 transition-all hover:scale-110 border border-white/10" title="Enviar E-mail">
                  <Mail className="w-8 h-8 text-white" />
                </a>
                <a href="https://github.com/thalissomvinicius" target="_blank" className="w-16 h-16 rounded-2xl glass flex items-center justify-center hover:bg-slate-800 transition-all hover:scale-110 border border-white/10" title="GitHub">
                  <Github className="w-8 h-8 text-white" />
                </a>
              </div>
            </div>
          </div>
        </Section>

        {/* Rodapé */}
        <footer className="py-20 px-6 border-t border-white/5 text-center bg-[#050507]">
          <div className="text-4xl font-black tracking-tighter mb-4">
            THALISSOM<span className="text-blue-500">VINICIUS</span>
          </div>
          <div className="text-[10px] font-black text-slate-700 uppercase tracking-[0.5em] mb-12">
            Produto da Assinatura <span className="text-blue-500/50 italic">Vinicius Dev</span>
          </div>
          <p className="text-slate-500 text-sm font-medium">
            © 2026 Thalissom Vinicius Cruz. <br className="md:hidden" />
            <span className="hidden md:inline mx-2">•</span>
            Desenvolvedor, Designer & Especialista Adm/Fiscal.
          </p>
        </footer>
      </div>
    </div>
  );
};

export default App;
