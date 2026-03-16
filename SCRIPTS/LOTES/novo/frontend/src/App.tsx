import { useState, useEffect } from 'react';
import './index.css';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LoginView } from './components/LoginView';
import { Sidebar } from './components/Sidebar';
import { DashboardExecutivo } from './components/DashboardExecutivo';
import { ConsultaVenda } from './components/ConsultaVenda';
import { CorretoresStats } from './components/CorretoresStats';
import { MensagensDiarias } from './components/MensagensDiarias';
import { InadimplentesView } from './components/InadimplentesView';
import { EvolucaoView } from './components/EvolucaoView';
import { RecebimentosView } from './components/RecebimentosView';
import { LoteamentoDashboard } from './components/LoteamentoDashboard';
import { DisponibilidadesView } from './components/DisponibilidadesView';
import { Dashboard } from './components/Dashboard';
import { SobreView } from './components/SobreView';
import { ContratosView } from './components/ContratosView';
import { QuitacaoView } from './components/QuitacaoView';
import { FeedbackView } from './components/FeedbackView';
import { AdminView } from './components/AdminView';
import type { Filters } from './types';

// Lista de empresas disponíveis
export const EMPRESAS_DISPONIVEIS = [
  { empresa: 28, obra: '70100', nome: 'VALLE DO IPITINGA II - TOMÉ-AÇU/PA' },
  { empresa: 29, obra: '70100', nome: 'VALLE DOS IPÊS - TOMÉ-AÇU/PA' },
];

// Mapeamento de views para nomes amigáveis
const VIEW_NAMES: Record<string, string> = {
  'dashboard': 'Dashboard Executivo',
  'boletos': 'Gerenciamento de Boletos',
  'consulta': 'Consultar Venda',
  'corretores': 'Corretores',
  'mensagens': 'Mensagens Diárias',
  'inadimplentes': 'Inadimplência',
  'evolucao': 'Evolução',
  'recebimentos': 'Recebimentos',
  'loteamento': 'Loteamento',
  'disponibilidades': 'Disponibilidades',
  'contratos': 'Contratos',
  'quitacao': 'Termos e Contratos',
  'sobre': 'Sobre',
  'feedbacks': 'Feedbacks',
  'admin': 'Administração'
};

type ViewType = 'dashboard' | 'boletos' | 'consulta' | 'corretores' | 'mensagens' | 'inadimplentes' | 'evolucao' | 'recebimentos' | 'loteamento' | 'disponibilidades' | 'contratos' | 'quitacao' | 'sobre' | 'feedbacks' | 'admin';

function MainApp() {
  const { user, logout } = useAuth();
  const [activeView, setActiveView] = useState<ViewType>('loteamento');
  const [selectedEmpresaIndex, setSelectedEmpresaIndex] = useState(0);
  const [refreshKey, setRefreshKey] = useState(0);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  const empresaAtual = EMPRESAS_DISPONIVEIS[selectedEmpresaIndex];
  const filters: Filters = {
    empresa: empresaAtual.empresa,
    obra: empresaAtual.obra,
    dataVencimento: '2025-12-31',
  };

  // Heartbeat - envia a cada 30 segundos para indicar que o usuário está online
  useEffect(() => {
    if (!user?.id) return;

    const sendHeartbeat = async () => {
      try {
        await fetch('/api/users/heartbeat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: user.id })
        });
      } catch (err) {
        console.error('Erro ao enviar heartbeat:', err);
      }
    };

    // Enviar heartbeat imediatamente ao carregar
    sendHeartbeat();

    // E a cada 30 segundos
    const interval = setInterval(sendHeartbeat, 30000);

    return () => clearInterval(interval);
  }, [user?.id]);

  // Registrar acesso à página quando muda a view
  useEffect(() => {
    if (!user?.id) return;

    const registerPageAccess = async () => {
      try {
        await fetch('/api/users/page-access', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: user.id,
            page: activeView,
            page_name: VIEW_NAMES[activeView] || activeView
          })
        });
      } catch (err) {
        console.error('Erro ao registrar acesso:', err);
      }
    };

    registerPageAccess();
  }, [user?.id, activeView]);

  const handleRefresh = () => {
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div>
      <Sidebar
        activeView={activeView}
        onViewChange={setActiveView}
        onRefresh={handleRefresh}
        empresas={EMPRESAS_DISPONIVEIS}
        selectedEmpresaIndex={selectedEmpresaIndex}
        onEmpresaChange={setSelectedEmpresaIndex}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
        user={user}
        onLogout={logout}
      />
      <main className="main-content" style={{ marginLeft: isSidebarCollapsed ? '72px' : '260px', transition: 'margin-left 0.3s ease' }}>
        {activeView === 'dashboard' ? (
          <DashboardExecutivo filters={filters} refreshKey={refreshKey} />
        ) : activeView === 'boletos' ? (
          <Dashboard filters={filters} refreshKey={refreshKey} />
        ) : activeView === 'consulta' ? (
          <ConsultaVenda empresa={filters.empresa} obra={filters.obra} refreshKey={refreshKey} />
        ) : activeView === 'corretores' ? (
          <CorretoresStats empresa={filters.empresa} obra={filters.obra} refreshKey={refreshKey} />
        ) : activeView === 'mensagens' ? (
          <MensagensDiarias empresa={filters.empresa} obra={filters.obra} refreshKey={refreshKey} />
        ) : activeView === 'inadimplentes' ? (
          <InadimplentesView empresa={filters.empresa} obra={filters.obra} refreshKey={refreshKey} />
        ) : activeView === 'evolucao' ? (
          <EvolucaoView empresa={filters.empresa} obra={filters.obra} refreshKey={refreshKey} />
        ) : activeView === 'recebimentos' ? (
          <RecebimentosView empresa={filters.empresa} obra={filters.obra} refreshKey={refreshKey} />
        ) : activeView === 'loteamento' ? (
          <LoteamentoDashboard empresa={filters.empresa} obra={filters.obra} />
        ) : activeView === 'disponibilidades' ? (
          <DisponibilidadesView empresa={filters.empresa} obra={filters.obra} nomeObra={empresaAtual.nome} />
        ) : activeView === 'sobre' ? (
          <SobreView empresa={filters.empresa} obra={filters.obra} />
        ) : activeView === 'contratos' ? (
          <ContratosView empresa={filters.empresa} obra={filters.obra} refreshKey={refreshKey} />
        ) : activeView === 'quitacao' ? (
          <QuitacaoView empresa={filters.empresa} obra={filters.obra} refreshKey={refreshKey} />
        ) : activeView === 'feedbacks' ? (
          <FeedbackView />
        ) : activeView === 'admin' ? (
          <AdminView />
        ) : null}

        <footer style={{
          marginTop: '40px',
          textAlign: 'center',
          padding: '20px',
          color: '#94A3B8',
          fontSize: '12px',
          borderTop: '1px solid #E2E8F0'
        }}>
          <p>🏘️ VallePrime - Sistema de Controle de Vendas e Boletos</p>
          <p style={{ marginTop: '4px' }}>© 2025 - Todos os direitos reservados</p>
          <p style={{ marginTop: '8px', fontSize: '11px', color: '#A0AEC0', fontStyle: 'italic' }}>
            Desenvolvido por Vinicius Dev
          </p>
        </footer>
      </main>
    </div>
  );
}

function AppContent() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #1e3a5f 0%, #0d1b2a 100%)'
      }}>
        <div style={{
          width: '50px',
          height: '50px',
          border: '4px solid rgba(255,255,255,0.2)',
          borderTopColor: 'white',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }}></div>
      </div>
    );
  }

  return isAuthenticated ? <MainApp /> : <LoginView />;
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;
