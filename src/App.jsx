import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { ArrowDownRight, ArrowUpRight, BarChart3, BriefcaseBusiness, Check, ChevronRight, Database, Github, Layers3, Mail, Map, Menu, Satellite, Smartphone, Sprout, X } from 'lucide-react'

const projects = [
  { number: '01', title: 'Ecossistema de operação agrícola', context: 'Vila Nova Agroindustrial · Sistema interno', description: 'Dashboard integrado para acompanhar CQO, coletas, inventário, rampa, equipes e informações georreferenciadas em uma única operação.', stack: ['React', 'Supabase', 'SQL', 'Mapas'], icon: Sprout, tone: 'lime' },
  { number: '02', title: 'Controle de cotas CFF', context: 'Vila Nova Agroindustrial · Aplicação web', description: 'Painel semanal conectado à balança, com saldos por produtor, alertas operacionais, qualidade CQO e histórico auditável de alterações.', stack: ['Next.js', 'Cloudflare D1', 'API HMAC', 'TypeScript'], icon: BarChart3, tone: 'amber' },
  { number: '03', title: 'Coletas mobile offline-first', context: 'Vila Nova Agroindustrial · Aplicativo Android', description: 'Aplicativo de campo que registra formulários, GPS, fotos e assinaturas mesmo sem internet e sincroniza os dados com segurança quando a conexão retorna.', stack: ['React Native', 'Expo', 'SQLite', 'Supabase'], icon: Smartphone, tone: 'blue' },
  { number: '04', title: 'Inteligência geográfica agrícola', context: 'Vila Nova Agroindustrial · Dados e visualização', description: 'Painéis de qualidade e fertilizantes com leitura por fazenda e parcela, indicadores de perdas e mapas de intensidade para apoiar decisões no campo.', stack: ['GeoJSON', 'Recharts', 'Excel', 'Power BI'], icon: Map, tone: 'violet' },
]

const capabilities = [
  { icon: Layers3, title: 'Produto ponta a ponta', text: 'Do entendimento da rotina até a interface, banco, regras de negócio, testes e entrega para o usuário final.' },
  { icon: Database, title: 'Dados que viram decisão', text: 'Integro SQL, APIs, planilhas e bases operacionais para criar indicadores confiáveis e rastreáveis.' },
  { icon: Satellite, title: 'Tecnologia no campo', text: 'Construo soluções móveis, offline e geográficas para ambientes onde conectividade e usabilidade são críticas.' },
]

const olderWork = [
  ['VallePrime', 'Disponibilidade de lotes em tempo real para o time comercial.'],
  ['Gerador de propostas', 'Automação de documentos comerciais com geração precisa de PDF.'],
  ['War Room UAU', 'Indicadores e rotinas para apoiar a gestão financeira e imobiliária.'],
]

const reveal = { initial: { opacity: 0, y: 24 }, whileInView: { opacity: 1, y: 0 }, viewport: { once: true, margin: '-80px' }, transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] } }

function App() {
  const [menuOpen, setMenuOpen] = useState(false)
  useEffect(() => { document.body.style.overflow = menuOpen ? 'hidden' : ''; return () => { document.body.style.overflow = '' } }, [menuOpen])
  const closeMenu = () => setMenuOpen(false)

  return (
    <div className="site-shell">
      <header className="site-header">
        <a className="brand" href="#inicio" aria-label="Ir para o início">TV<span>.</span></a>
        <nav className="desktop-nav" aria-label="Navegação principal"><a href="#projetos">Projetos</a><a href="#sobre">Sobre</a><a href="#trajetoria">Trajetória</a></nav>
        <a className="header-cta" href="#contato">Vamos conversar <ArrowUpRight size={16} /></a>
        <button className="menu-button" onClick={() => setMenuOpen(true)} aria-label="Abrir menu"><Menu size={24} /></button>
      </header>

      {menuOpen && <div className="mobile-menu" role="dialog" aria-modal="true" aria-label="Menu">
        <button onClick={closeMenu} aria-label="Fechar menu"><X size={28} /></button>
        <a href="#projetos" onClick={closeMenu}>Projetos</a><a href="#sobre" onClick={closeMenu}>Sobre</a><a href="#trajetoria" onClick={closeMenu}>Trajetória</a><a href="#contato" onClick={closeMenu}>Contato</a>
      </div>}

      <main>
        <section className="hero" id="inicio">
          <div className="hero-grid" aria-hidden="true" />
          <motion.div className="hero-copy" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7 }}>
            <div className="availability"><span /> Tecnologia aplicada à operação · Vila Nova Agroindustrial</div>
            <h1>Transformo operações complexas em <em>software que funciona.</em></h1>
            <p>Sou Thalissom Vinicius. Desenvolvo sistemas, dashboards e automações que conectam dados, pessoas e decisões — do escritório ao campo.</p>
            <div className="hero-actions"><a className="primary-button" href="#projetos">Ver projetos <ArrowDownRight size={19} /></a><a className="text-link" href="mailto:vinicius.devcode.br@gmail.com">vinicius.devcode.br@gmail.com <ArrowUpRight size={16} /></a></div>
          </motion.div>
          <motion.figure className="hero-portrait" initial={{ opacity: 0, x: 24 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.7, delay: 0.25 }}>
            <div className="portrait-frame">
              <img src={`${import.meta.env.BASE_URL}photo_profile.png`} alt="Thalissom Vinicius" />
              <span className="portrait-corner" aria-hidden="true">TV</span>
            </div>
            <figcaption><span>Thalissom Vinicius</span><small>Desenvolvedor de sistemas</small></figcaption>
          </motion.figure>
          <motion.div className="hero-status" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.45 }}><span>Belém, Pará · Brasil</span><span>Desenvolvimento · Dados · Produto</span></motion.div>
        </section>

        <section className="statement" id="sobre">
          <motion.div {...reveal}><span className="section-index">01 / PERFIL</span><p className="statement-lead">Não entrego apenas telas. Entendo o processo, encontro o gargalo e construo a solução completa.</p></motion.div>
          <motion.div className="statement-side" {...reveal} transition={{ ...reveal.transition, delay: 0.1 }}><p>Minha formação em Ciências Contábeis e a experiência dentro de operações reais me deram uma visão incomum: consigo conversar com a gestão, compreender a rotina e traduzir tudo em tecnologia utilizável.</p><div className="skill-row">{['React & Next.js', 'Python & SQL', 'React Native', 'BI & Geodados'].map((skill) => <span key={skill}>{skill}</span>)}</div></motion.div>
        </section>

        <section className="projects-section" id="projetos">
          <motion.div className="section-heading" {...reveal}><div><span className="section-index">02 / TRABALHO RECENTE</span><h2>Sistemas construídos para a operação real.</h2></div><p>Cases apresentados em nível conceitual para preservar dados e processos internos da empresa.</p></motion.div>
          <div className="project-list">{projects.map((project, index) => { const Icon = project.icon; return <motion.article className={`project-card ${project.tone}`} key={project.title} {...reveal} transition={{ ...reveal.transition, delay: index * 0.05 }}><div className="project-number">{project.number}</div><div className="project-icon"><Icon size={28} strokeWidth={1.6} /></div><div className="project-content"><span>{project.context}</span><h3>{project.title}</h3><p>{project.description}</p><div className="tag-list">{project.stack.map((item) => <span key={item}>{item}</span>)}</div></div><div className="private-mark"><Check size={14} /> Case documentado</div></motion.article> })}</div>
        </section>

        <section className="capabilities-section">
          <motion.div className="section-heading compact" {...reveal}><div><span className="section-index">03 / COMO EU TRABALHO</span><h2>Negócio primeiro. Código com propósito.</h2></div></motion.div>
          <div className="capability-grid">{capabilities.map((item, index) => { const Icon = item.icon; return <motion.div className="capability-card" key={item.title} {...reveal} transition={{ ...reveal.transition, delay: index * 0.08 }}><Icon size={25} /><h3>{item.title}</h3><p>{item.text}</p></motion.div> })}</div>
        </section>

        <section className="timeline-section" id="trajetoria">
          <motion.div className="section-heading" {...reveal}><div><span className="section-index">04 / TRAJETÓRIA</span><h2>Experiência construída dentro do negócio.</h2></div></motion.div>
          <div className="timeline">
            <motion.div className="timeline-row current" {...reveal}><span className="timeline-date">ATUAL</span><div><span>Vila Nova Agroindustrial</span><h3>Tecnologia aplicada à operação industrial e agrícola</h3><p>Desenvolvimento de produtos internos, integração de dados, soluções de campo e inteligência operacional.</p></div><BriefcaseBusiness size={24} /></motion.div>
            <motion.div className="timeline-row" {...reveal}><span className="timeline-date">6 ANOS</span><div><span>Valle Empreendimentos</span><h3>Processos, automação e sistemas para o mercado imobiliário</h3><p>Uma trajetória que começou na operação administrativa e evoluiu para a criação de ferramentas próprias.</p></div><ChevronRight size={24} /></motion.div>
          </div>
          <motion.div className="archive" {...reveal}><span>Projetos que marcaram essa fase</span>{olderWork.map(([title, text]) => <div key={title}><strong>{title}</strong><p>{text}</p></div>)}</motion.div>
        </section>

        <section className="contact-section" id="contato"><motion.div {...reveal}><span className="section-index light">05 / CONTATO</span><h2>Tem um processo difícil esperando uma solução?</h2><p>Vamos conversar sobre sistemas, dados, automação e tecnologia aplicada ao seu negócio.</p><div className="contact-actions"><a href="mailto:vinicius.devcode.br@gmail.com">Enviar um e-mail <Mail size={19} /></a><a href="https://wa.me/5591991697664" target="_blank" rel="noreferrer">Conversar no WhatsApp <ArrowUpRight size={19} /></a></div></motion.div></section>
      </main>

      <footer><a className="brand" href="#inicio">TV<span>.</span></a><p>© 2026 Thalissom Vinicius Cruz</p><a href="https://github.com/thalissomvinicius" target="_blank" rel="noreferrer"><Github size={18} /> GitHub</a></footer>
    </div>
  )
}

export default App
