import { useState, useEffect } from 'react';
import Header from './components/Header/Header';
import Filters from './components/Filters/Filters';
import Stats from './components/Stats/Stats';
import LoteTable from './components/LoteTable/LoteTable';
import LoteModal from './components/LoteModal/LoteModal';
import type { Lote, Filtros, Estatisticas } from './types';
import { buscarLotes, getStatusKey, empreendimentos } from './services/api';
import './App.css';

function App() {
  const [todosLotes, setTodosLotes] = useState<Lote[]>([]);
  const [lotesFiltrados, setLotesFiltrados] = useState<Lote[]>([]);
  const [quadras, setQuadras] = useState<string[]>([]);
  const [filtros, setFiltros] = useState<Filtros>({ status: '', quadra: '', busca: '' });
  const [stats, setStats] = useState<Estatisticas>({ total: 0, disponiveis: 0, reservados: 0, vendidos: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedLote, setSelectedLote] = useState<Lote | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [empreendimentoAtual, setEmpreendimentoAtual] = useState(600);

  // Carregar lotes ao montar o componente
  useEffect(() => {
    carregarLotes();
  }, [empreendimentoAtual]);

  // Aplicar filtros quando mudarem
  useEffect(() => {
    aplicarFiltros();
  }, [filtros, todosLotes]);

  const carregarLotes = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await buscarLotes(empreendimentoAtual);

      if (response.success) {
        setTodosLotes(response.data);

        // Extrair quadras únicas
        const quadrasUnicas = [...new Set(response.data.map(l => l.QD))].sort();
        setQuadras(quadrasUnicas);

        // Calcular estatísticas
        calcularEstatisticas(response.data);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Erro ao carregar lotes. Verifique sua conexão.';
      setError(errorMessage);
      console.error('Erro detalhado:', err);
    } finally {
      setLoading(false);
    }
  };

  const calcularEstatisticas = (lotes: Lote[]) => {
    const total = lotes.length;
    const disponiveis = lotes.filter(l => l.Status_Terreno.includes('Disponível')).length;
    const reservados = lotes.filter(l => l.Status_Terreno.includes('Reservado')).length;
    const vendidos = lotes.filter(l =>
      l.Status_Terreno.includes('Vendido') || l.Status_Terreno.includes('Quitado')
    ).length;

    setStats({ total, disponiveis, reservados, vendidos });
  };

  const aplicarFiltros = () => {
    let resultado = [...todosLotes];

    // Filtro de status
    if (filtros.status) {
      resultado = resultado.filter(lote => {
        const statusLote = getStatusKey(lote.Status_Terreno);
        return statusLote === filtros.status;
      });
    }

    // Filtro de quadra
    if (filtros.quadra) {
      resultado = resultado.filter(lote => lote.QD === filtros.quadra);
    }

    // Filtro de busca
    if (filtros.busca) {
      const busca = filtros.busca.toLowerCase().trim();
      resultado = resultado.filter(lote => {
        const textoLote = `${lote.QD} ${lote.LT} ${lote.Logradouro}`.toLowerCase();
        return textoLote.includes(busca);
      });
    }

    setLotesFiltrados(resultado);
  };

  const abrirModal = (lote: Lote) => {
    setSelectedLote(lote);
    setModalOpen(true);
  };

  const fecharModal = () => {
    setModalOpen(false);
    setSelectedLote(null);
  };

  const abrirNovaProposta = (lote?: Lote) => {
    if (lote) {
      // Buscar dados do empreendimento atual
      const empreendimento = empreendimentos.find(e => e.id === empreendimentoAtual);

      // Salvar dados no localStorage
      const dadosProposta = {
        empreendimento: empreendimento,
        lote: lote
      };

      localStorage.setItem('dadosProposta', JSON.stringify(dadosProposta));
      console.log('📝 Dados salvos para proposta:', dadosProposta);
    }

    window.open('/propostatest.html', '_blank');
  };

  return (
    <div className="app">
      <Header onNovaPropostaClick={abrirNovaProposta} />

      <main className="main">
        <Filters
          filtros={filtros}
          quadras={quadras}
          onFiltrosChange={setFiltros}
          onBuscar={aplicarFiltros}
          onEmpreendimentoChange={setEmpreendimentoAtual}
        />

        <Stats stats={stats} />

        <section className="results-section">
          <div className="results-header">
            <h2 className="results-title">
              Lotes Encontrados: <span>{lotesFiltrados.length}</span>
            </h2>
          </div>

          {loading && (
            <div className="loading">
              <div className="spinner"></div>
              <p>Carregando lotes...</p>
            </div>
          )}

          {error && (
            <div className="error">
              <p>{error}</p>
              <button onClick={carregarLotes} className="btn-retry">Tentar Novamente</button>
            </div>
          )}

          {!loading && !error && lotesFiltrados.length === 0 && (
            <div className="no-results">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#999" strokeWidth="1.5">
                <circle cx="11" cy="11" r="8"></circle>
                <path d="m21 21-4.35-4.35"></path>
              </svg>
              <p>Nenhum lote encontrado com os filtros selecionados.</p>
            </div>
          )}

          {!loading && !error && lotesFiltrados.length > 0 && (
            <LoteTable
              lotes={lotesFiltrados}
              empreendimento={empreendimentos.find(e => e.id === empreendimentoAtual) || null}
              onLoteClick={abrirModal}
            />
          )}
        </section>
      </main>

      <LoteModal
        lote={selectedLote}
        isOpen={modalOpen}
        onClose={fecharModal}
        onNovaPropostaClick={abrirNovaProposta}
      />
    </div>
  );
}

export default App;
