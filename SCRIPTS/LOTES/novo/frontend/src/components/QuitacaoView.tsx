import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { formatCurrency } from '../utils/format';

interface QuitacaoViewProps {
    empresa: number;
    obra: string;
    refreshKey: number;
}

interface LoteQuitado {
    identificador: string;
    quadra: string;
    lote: string;
    area: number;
    logradouro: string;
    numVenda: number | null;
    valor: number;
    cliente: string;
    cpf: string;
    codCliente: number | null;
    nomeObra: string;
}

interface ModalConfig {
    lote: LoteQuitado | null;
    tipo: 'carta' | 'termo' | null;
}
// Tipos de parcela disponíveis para seleção
const TIPOS_PARCELA = [
    { codigo: '0', nome: 'Seguro', default: false },
    { codigo: '1', nome: 'Custas', default: false },
    { codigo: '2', nome: 'Acerto Final', default: false },
    { codigo: 'A', nome: 'Resíduo Agrup.', default: false },
    { codigo: 'B', nome: 'Balão', default: false },
    { codigo: 'C', nome: 'Chave', default: false },
    { codigo: 'E', nome: 'Entrada', default: true },
    { codigo: 'ER', nome: 'Entrada Reneg.', default: false },
    { codigo: 'I', nome: 'Intermediação', default: false },
    { codigo: 'IN', nome: 'Intermediárias', default: false },
    { codigo: 'P', nome: 'Parcela', default: true },
    { codigo: 'R', nome: 'Resíduo', default: false },
    { codigo: 'S', nome: 'Corretagem', default: true },
];

interface Empresa {
    codigo: number;
    nome: string;
}

interface Obra {
    codigo: string;
    nome: string;
}

export const QuitacaoView: React.FC<QuitacaoViewProps> = ({ empresa: empresaInicial, obra: obraInicial, refreshKey }) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [lotes, setLotes] = useState<LoteQuitado[]>([]);
    const [gerandoPdf, setGerandoPdf] = useState<string | null>(null);

    // Filtro de empresa/obra local
    const [empresas, setEmpresas] = useState<Empresa[]>([]);
    const [obras, setObras] = useState<Obra[]>([]);
    const [empresaSelecionada, setEmpresaSelecionada] = useState<number>(empresaInicial);
    const [obraSelecionada, setObraSelecionada] = useState<string>(obraInicial);

    // Modal de configuração
    const [modalConfig, setModalConfig] = useState<ModalConfig>({ lote: null, tipo: null });
    const [dataDocumento, setDataDocumento] = useState(() => {
        const today = new Date();
        return today.toISOString().split('T')[0]; // Format: YYYY-MM-DD
    });
    const [matricula, setMatricula] = useState('');
    const [folha, setFolha] = useState('');
    const [livro, setLivro] = useState('');

    // Tipos de parcela selecionados (para o Termo)
    const [tiposSelecionados, setTiposSelecionados] = useState<string[]>(
        TIPOS_PARCELA.filter(t => t.default).map(t => t.codigo)
    );

    // Carregar empresas
    const loadEmpresas = async () => {
        try {
            const response = await fetch('/api/empresas');
            if (response.ok) {
                const data = await response.json();
                setEmpresas(data.empresas || []);
            }
        } catch (err) {
            console.error('Erro ao carregar empresas:', err);
        }
    };

    // Carregar obras da empresa selecionada
    const loadObras = async (emp: number) => {
        try {
            const response = await fetch(`/api/obras?empresa=${emp}`);
            if (response.ok) {
                const data = await response.json();
                setObras(data.obras || []);
            }
        } catch (err) {
            console.error('Erro ao carregar obras:', err);
        }
    };

    // Inicializar filtros
    useEffect(() => {
        loadEmpresas();
    }, []);

    useEffect(() => {
        if (empresaSelecionada) {
            loadObras(empresaSelecionada);
        }
    }, [empresaSelecionada]);

    const loadLotes = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`/api/quitacao/lotes?empresa=${empresaSelecionada}&obra=${obraSelecionada}`);
            if (response.ok) {
                const result = await response.json();
                setLotes(result.lotes || []);
            } else {
                throw new Error('Erro ao carregar lotes quitados');
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erro desconhecido');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadLotes();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [empresaSelecionada, obraSelecionada, refreshKey]);

    const abrirModal = (lote: LoteQuitado, tipo: 'carta' | 'termo') => {
        setModalConfig({ lote, tipo });
        const today = new Date();
        setDataDocumento(today.toISOString().split('T')[0]);
        // Travar scroll do body
        document.body.style.overflow = 'hidden';
    };

    const fecharModal = () => {
        setModalConfig({ lote: null, tipo: null });
        // Restaurar scroll
        document.body.style.overflow = 'auto';
    };

    const gerarDocumento = async (formato = 'pdf') => {
        if (!modalConfig.lote || !modalConfig.tipo) return;

        const loteData = modalConfig.lote;
        const tipo = modalConfig.tipo;
        const key = `${tipo}-${loteData.quadra}-${loteData.lote}`;

        setGerandoPdf(key);
        fecharModal();

        try {
            // Montar parâmetros base
            let params = loteData.numVenda
                ? `empresa=${empresaSelecionada}&obra=${obraSelecionada}&venda=${loteData.numVenda}`
                : `empresa=${empresaSelecionada}&obra=${obraSelecionada}&quadra=${loteData.quadra}&lote=${loteData.lote}`;

            // Adicionar apenas data - cidade vem do banco automaticamente
            params += `&data=${dataDocumento}`;

            // Adicionar dados de registro se fornecidos (apenas para termo)
            if (tipo === 'termo') {
                if (matricula) params += `&matricula=${encodeURIComponent(matricula)}`;
                if (folha) params += `&folha=${encodeURIComponent(folha)}`;
                if (livro) params += `&livro=${encodeURIComponent(livro)}`;
            }

            // Para Termo, adicionar tipos de parcela selecionados
            if (tipo === 'termo' && tiposSelecionados.length > 0) {
                params += `&tipos=${tiposSelecionados.join(',')}`;
            }

            // Adicionar formato (pdf ou docx)
            params += `&formato=${formato}`;

            const endpoint = tipo === 'carta' ? 'carta' : 'termo';
            const response = await fetch(`/api/quitacao/${endpoint}?${params}`);

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `Erro ao gerar ${tipo}`);
            }

            const blob = await response.blob();
            const url = URL.createObjectURL(blob);

            window.open(url, '_blank'); // Abre em nova aba
        } catch (err) {
            alert(err instanceof Error ? err.message : `Erro ao gerar ${tipo}`);
        } finally {
            setGerandoPdf(null);
        }
    };

    const gerarExtrato = async () => {
        if (!modalConfig.lote) return;

        const loteData = modalConfig.lote;
        const key = `extrato-${loteData.quadra}-${loteData.lote}`;

        setGerandoPdf(key);
        fecharModal();

        try {
            let params = loteData.numVenda
                ? `empresa=${empresaSelecionada}&obra=${obraSelecionada}&venda=${loteData.numVenda}`
                : `empresa=${empresaSelecionada}&obra=${obraSelecionada}&quadra=${loteData.quadra}&lote=${loteData.lote}`;

            if (tiposSelecionados.length > 0) {
                params += `&tipos=${tiposSelecionados.join(',')}`;
            }

            const response = await fetch(`/api/quitacao/extrato?${params}`);

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Erro ao gerar extrato');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            window.open(url, '_blank');
        } catch (err: unknown) {
            alert(err instanceof Error ? err.message : 'Erro ao gerar extrato');
        } finally {
            setGerandoPdf(null);
        }
    };



    const [searchTerm, setSearchTerm] = useState('');

    const filteredLotes = lotes.filter(lote => {
        const search = searchTerm.toLowerCase();
        return (
            lote.quadra.toLowerCase().includes(search) ||
            lote.lote.toLowerCase().includes(search) ||
            (lote.cliente || '').toLowerCase().includes(search) ||
            (lote.cpf || '').includes(search) ||
            String(lote.numVenda || '').includes(search)
        );
    });

    return (
        <div className="animate-fade-in">
            {/* Modal de Configuração - Usando Portal */}
            {modalConfig.lote && createPortal(
                <div
                    style={{
                        position: 'fixed',
                        inset: 0,
                        backgroundColor: 'rgba(0,0,0,0.6)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        zIndex: 99999
                    }}
                    onClick={(e) => {
                        if (e.target === e.currentTarget) fecharModal();
                    }}
                >
                    <div
                        style={{
                            position: 'relative',
                            background: 'white',
                            borderRadius: '12px',
                            padding: '24px',
                            width: '90%',
                            maxWidth: '580px',
                            maxHeight: '85vh',
                            overflowY: 'auto',
                            boxShadow: '0 25px 70px rgba(0,0,0,0.35)'
                        }}
                        onClick={(e) => e.stopPropagation()}
                    >
                        <h3 style={{ margin: '0 0 20px 0', color: '#1F2937', fontSize: '18px' }}>
                            📝 Configurar {modalConfig.tipo === 'carta' ? 'Carta' : 'Termo'} de Quitação
                        </h3>

                        <div style={{ marginBottom: '16px' }}>
                            <p style={{ fontSize: '14px', color: '#6B7280', margin: '0 0 16px 0' }}>
                                Lote: <strong>Q{modalConfig.lote.quadra} L{modalConfig.lote.lote}</strong> - {modalConfig.lote.cliente || 'Cliente não informado'}
                            </p>
                        </div>

                        {/* Dados de Registro (Apenas Termo) */}
                        {modalConfig.tipo === 'termo' && (
                            <div style={{ marginBottom: '20px', display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
                                <div>
                                    <label style={{ display: 'block', marginBottom: '6px', fontWeight: 500, fontSize: '13px', color: '#374151' }}>
                                        Matrícula
                                    </label>
                                    <input
                                        type="text"
                                        value={matricula}
                                        onChange={(e) => setMatricula(e.target.value)}
                                        placeholder="Nº"
                                        style={{ width: '100%', padding: '8px', border: '1px solid #D1D5DB', borderRadius: '6px', fontSize: '14px' }}
                                    />
                                </div>
                                <div>
                                    <label style={{ display: 'block', marginBottom: '6px', fontWeight: 500, fontSize: '13px', color: '#374151' }}>
                                        Folha
                                    </label>
                                    <input
                                        type="text"
                                        value={folha}
                                        onChange={(e) => setFolha(e.target.value)}
                                        placeholder="Nº"
                                        style={{ width: '100%', padding: '8px', border: '1px solid #D1D5DB', borderRadius: '6px', fontSize: '14px' }}
                                    />
                                </div>
                                <div>
                                    <label style={{ display: 'block', marginBottom: '6px', fontWeight: 500, fontSize: '13px', color: '#374151' }}>
                                        Livro
                                    </label>
                                    <input
                                        type="text"
                                        value={livro}
                                        onChange={(e) => setLivro(e.target.value)}
                                        placeholder="Nº"
                                        style={{ width: '100%', padding: '8px', border: '1px solid #D1D5DB', borderRadius: '6px', fontSize: '14px' }}
                                    />
                                </div>
                            </div>
                        )}

                        {/* Data do Documento */}
                        <div style={{ marginBottom: '24px' }}>
                            <label style={{ display: 'block', marginBottom: '6px', fontWeight: 500, fontSize: '14px', color: '#374151' }}>
                                Data do Documento
                            </label>
                            <input
                                type="date"
                                title="Data do Documento"
                                value={dataDocumento}
                                onChange={(e) => setDataDocumento(e.target.value)}
                                style={{
                                    width: '100%',
                                    padding: '10px 12px',
                                    border: '1px solid #D1D5DB',
                                    borderRadius: '8px',
                                    fontSize: '14px',
                                    boxSizing: 'border-box'
                                }}
                            />
                            <p style={{ fontSize: '12px', color: '#9CA3AF', marginTop: '6px', margin: '6px 0 0 0' }}>
                                A cidade do loteamento será usada automaticamente
                            </p>
                        </div>

                        {/* Tipos de Parcela - apenas para Termo */}
                        {modalConfig.tipo === 'termo' && (
                            <div style={{ marginBottom: '24px' }}>
                                <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500, fontSize: '14px', color: '#374151' }}>
                                    Tipos de Parcela a Considerar
                                </label>
                                <div style={{
                                    display: 'grid',
                                    gridTemplateColumns: 'repeat(4, 1fr)',
                                    gap: '4px 8px',
                                    padding: '10px',
                                    background: '#F9FAFB',
                                    borderRadius: '8px',
                                    border: '1px solid #E5E7EB'
                                }}>
                                    {TIPOS_PARCELA.map(tipo => (
                                        <label
                                            key={tipo.codigo}
                                            style={{
                                                display: 'flex',
                                                alignItems: 'center',
                                                gap: '4px',
                                                fontSize: '11px',
                                                cursor: 'pointer',
                                                whiteSpace: 'nowrap',
                                                padding: '2px 0',
                                                color: tiposSelecionados.includes(tipo.codigo) ? '#059669' : '#6B7280'
                                            }}
                                        >
                                            <input
                                                type="checkbox"
                                                checked={tiposSelecionados.includes(tipo.codigo)}
                                                onChange={(e) => {
                                                    if (e.target.checked) {
                                                        setTiposSelecionados([...tiposSelecionados, tipo.codigo]);
                                                    } else {
                                                        setTiposSelecionados(tiposSelecionados.filter(t => t !== tipo.codigo));
                                                    }
                                                }}
                                                style={{ accentColor: '#10B981', width: '14px', height: '14px' }}
                                            />
                                            <span><b>{tipo.codigo}</b>-{tipo.nome}</span>
                                        </label>
                                    ))}
                                </div>
                                <p style={{ fontSize: '11px', color: '#9CA3AF', marginTop: '6px' }}>
                                    O valor será calculado com base nas parcelas selecionadas
                                </p>
                            </div>
                        )}

                        {/* Botões */}
                        <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                            <button
                                onClick={fecharModal}
                                style={{
                                    padding: '10px 20px',
                                    border: '1px solid #D1D5DB',
                                    borderRadius: '8px',
                                    background: 'white',
                                    color: '#374151',
                                    fontSize: '14px',
                                    fontWeight: 500,
                                    cursor: 'pointer'
                                }}
                            >
                                Cancelar
                            </button>
                            <button
                                onClick={() => gerarDocumento('pdf')}
                                style={{
                                    padding: '10px 20px',
                                    border: 'none',
                                    borderRadius: '8px',
                                    background: modalConfig.tipo === 'carta'
                                        ? 'linear-gradient(135deg, #3B82F6, #2563EB)'
                                        : 'linear-gradient(135deg, #10B981, #059669)',
                                    color: 'white',
                                    fontSize: '14px',
                                    fontWeight: 600,
                                    cursor: 'pointer'
                                }}
                            >
                                📄 Gerar {modalConfig.tipo === 'carta' ? 'Carta' : 'PDF'}
                            </button>

                            {modalConfig.tipo === 'termo' && (
                                <button
                                    onClick={() => gerarDocumento('docx')}
                                    style={{
                                        padding: '10px 20px',
                                        border: '1px solid #10B981',
                                        borderRadius: '8px',
                                        background: 'white',
                                        color: '#059669',
                                        fontSize: '14px',
                                        fontWeight: 600,
                                        cursor: 'pointer'
                                    }}
                                >
                                    📝 Gerar Word
                                </button>
                            )}

                            {modalConfig.tipo === 'termo' && (
                                <button
                                    onClick={gerarExtrato}
                                    style={{
                                        padding: '10px 20px',
                                        border: 'none',
                                        borderRadius: '8px',
                                        background: 'linear-gradient(135deg, #8B5CF6, #6D28D9)',
                                        color: 'white',
                                        fontSize: '14px',
                                        fontWeight: 600,
                                        cursor: 'pointer'
                                    }}
                                >
                                    📊 Gerar Extrato
                                </button>
                            )}
                        </div>
                    </div>
                </div>,
                document.body
            )}

            {/* Header */}
            <div className="page-header" style={{ marginBottom: '16px' }}>
                <div>
                    <h1 className="page-title">📋 Termos e Contratos</h1>
                    <p className="page-subtitle">Gere documentos de quitação (Carta e Termo) para lotes quitados</p>
                </div>
            </div>

            {/* Filtro de Empresa/Obra */}
            <div className="card" style={{ marginBottom: '16px', padding: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <label style={{ fontSize: '14px', fontWeight: 500, color: '#374151', whiteSpace: 'nowrap' }}>
                            🏢 Empresa:
                        </label>
                        <select
                            title="Selecionar Empresa"
                            value={empresaSelecionada}
                            onChange={(e) => {
                                const novaEmpresa = Number(e.target.value);
                                setEmpresaSelecionada(novaEmpresa);
                                setLotes([]);
                            }}
                            style={{
                                padding: '8px 12px',
                                border: '1px solid #D1D5DB',
                                borderRadius: '8px',
                                fontSize: '14px',
                                minWidth: '200px',
                                background: 'white'
                            }}
                        >
                            {empresas.length === 0 && (
                                <option value={empresaSelecionada}>Carregando...</option>
                            )}
                            {empresas.map(emp => (
                                <option key={emp.codigo} value={emp.codigo}>
                                    {emp.codigo} - {emp.nome}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <label style={{ fontSize: '14px', fontWeight: 500, color: '#374151', whiteSpace: 'nowrap' }}>
                            🏗️ Obra:
                        </label>
                        <select
                            title="Selecionar Obra"
                            value={obraSelecionada}
                            onChange={(e) => {
                                setObraSelecionada(e.target.value);
                                setLotes([]);
                            }}
                            style={{
                                padding: '8px 12px',
                                border: '1px solid #D1D5DB',
                                borderRadius: '8px',
                                fontSize: '14px',
                                minWidth: '250px',
                                background: 'white'
                            }}
                        >
                            {obras.length === 0 && (
                                <option value={obraSelecionada}>Carregando...</option>
                            )}
                            {obras.map(ob => (
                                <option key={ob.codigo} value={ob.codigo}>
                                    {ob.codigo} - {ob.nome}
                                </option>
                            ))}
                        </select>
                    </div>

                    <button
                        onClick={() => loadLotes()}
                        className="btn btn-primary"
                        disabled={loading}
                        style={{ display: 'flex', alignItems: 'center', gap: '6px' }}
                    >
                        {loading ? '⏳ Carregando...' : '🔍 Buscar Lotes'}
                    </button>
                </div>
            </div>

            {/* Ações e Busca */}
            <div className="card" style={{ marginBottom: '24px', padding: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1 }}>
                        <span style={{ fontSize: '14px', color: '#6B7280', whiteSpace: 'nowrap' }}>
                            Total de lotes quitados: <strong style={{ color: '#10B981' }}>{filteredLotes.length}</strong>
                            {searchTerm && <span style={{ fontWeight: 'normal', fontSize: '12px' }}> (de {lotes.length})</span>}
                        </span>

                        <div style={{ position: 'relative', maxWidth: '300px', width: '100%' }}>
                            <input
                                type="text"
                                placeholder="🔍 Buscar por lote, cliente, CPF ou venda..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                style={{
                                    width: '100%',
                                    padding: '8px 12px 8px 36px',
                                    border: '1px solid #E5E7EB',
                                    borderRadius: '8px',
                                    fontSize: '14px',
                                    outline: 'none',
                                    transition: 'border-color 0.2s'
                                }}
                            />
                            <span style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', fontSize: '14px' }}>
                                🔍
                            </span>
                        </div>
                    </div>

                    <button
                        onClick={() => loadLotes()}
                        className="btn btn-primary"
                        disabled={loading}
                        style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
                    >
                        {loading ? '⏳ Carregando...' : '🔄 Atualizar'}
                    </button>
                </div>
            </div>

            {/* Error */}
            {error && (
                <div className="card" style={{ background: '#FEE2E2', borderColor: '#EF4444', marginBottom: '24px', padding: '16px' }}>
                    <p style={{ color: '#991B1B', margin: 0 }}>❌ {error}</p>
                </div>
            )}

            {/* Loading */}
            {loading && (
                <div className="loading">
                    <div className="spinner"></div>
                </div>
            )}

            {/* Cards informativos */}
            {!loading && (
                <div className="metric-grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)', marginBottom: '24px' }}>
                    <div className="metric-card">
                        <div className="metric-card-icon">✅</div>
                        <div className="metric-card-content">
                            <div className="metric-label">LOTES QUITADOS</div>
                            <div className="metric-value success" style={{ fontSize: '28px' }}>{filteredLotes.length}</div>
                        </div>
                    </div>
                    <div className="metric-card">
                        <div className="metric-card-icon">📄</div>
                        <div className="metric-card-content">
                            <div className="metric-label">CARTA DE QUITAÇÃO</div>
                            <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
                                Declaração simples de quitação
                            </div>
                        </div>
                    </div>
                    <div className="metric-card">
                        <div className="metric-card-icon">📋</div>
                        <div className="metric-card-content">
                            <div className="metric-label">TERMO DE QUITAÇÃO</div>
                            <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '4px' }}>
                                Documento para escrituração em cartório
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Tabela */}
            {!loading && filteredLotes.length > 0 && (
                <div className="table-container">
                    <div className="table-header-row">
                        <span className="table-title">🏠 Lotes Quitados</span>
                        <span className="badge badge-success">{filteredLotes.length} lotes</span>
                    </div>
                    <div style={{ overflowX: 'auto' }}>
                        <table style={{ minWidth: '900px' }}>
                            <thead>
                                <tr>
                                    <th style={{ width: '60px', textAlign: 'center' }}>Quadra</th>
                                    <th style={{ width: '60px', textAlign: 'center' }}>Lote</th>
                                    <th style={{ width: '200px' }}>Cliente</th>
                                    <th style={{ width: '130px' }}>CPF/CNPJ</th>
                                    <th style={{ width: '80px', textAlign: 'right' }}>Área (m²)</th>
                                    <th style={{ width: '120px', textAlign: 'right' }}>Valor</th>
                                    <th style={{ width: '80px', textAlign: 'center' }}>Venda</th>
                                    <th style={{ width: '180px', textAlign: 'center' }}>Ações</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredLotes.map((lote, index) => (
                                    <tr key={index}>
                                        <td style={{ textAlign: 'center', fontWeight: 600 }}>{lote.quadra}</td>
                                        <td style={{ textAlign: 'center', fontWeight: 600 }}>{lote.lote}</td>
                                        <td style={{ fontSize: '13px' }}>{lote.cliente || '-'}</td>
                                        <td style={{ fontSize: '12px', fontFamily: 'monospace' }}>{lote.cpf || '-'}</td>
                                        <td style={{ textAlign: 'right' }}>{lote.area?.toFixed(2) || '-'}</td>
                                        <td style={{ textAlign: 'right', fontWeight: 500, color: '#10B981' }}>
                                            R$ {formatCurrency(lote.valor)}
                                        </td>
                                        <td style={{ textAlign: 'center' }}>
                                            <span className="badge badge-primary">{lote.numVenda || '-'}</span>
                                        </td>
                                        <td style={{ textAlign: 'center' }}>
                                            <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
                                                <button
                                                    onClick={() => abrirModal(lote, 'carta')}
                                                    disabled={gerandoPdf === `carta-${lote.quadra}-${lote.lote}`}
                                                    style={{
                                                        padding: '6px 12px',
                                                        borderRadius: '6px',
                                                        border: 'none',
                                                        background: 'linear-gradient(135deg, #3B82F6, #2563EB)',
                                                        color: 'white',
                                                        fontSize: '11px',
                                                        fontWeight: 600,
                                                        cursor: 'pointer',
                                                        display: 'flex',
                                                        alignItems: 'center',
                                                        gap: '4px'
                                                    }}
                                                    title="Gerar Carta de Quitação"
                                                >
                                                    {gerandoPdf === `carta-${lote.quadra}-${lote.lote}` ? '⏳' : '📄'} Carta
                                                </button>
                                                <button
                                                    onClick={() => abrirModal(lote, 'termo')}
                                                    disabled={gerandoPdf === `termo-${lote.quadra}-${lote.lote}`}
                                                    style={{
                                                        padding: '6px 12px',
                                                        borderRadius: '6px',
                                                        border: 'none',
                                                        background: 'linear-gradient(135deg, #10B981, #059669)',
                                                        color: 'white',
                                                        fontSize: '11px',
                                                        fontWeight: 600,
                                                        cursor: 'pointer',
                                                        display: 'flex',
                                                        alignItems: 'center',
                                                        gap: '4px'
                                                    }}
                                                    title="Gerar Termo de Quitação"
                                                >
                                                    {gerandoPdf === `termo-${lote.quadra}-${lote.lote}` ? '⏳' : '📋'} Termo
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Empty state */}
            {!loading && lotes.length === 0 && (
                <div className="card" style={{ textAlign: 'center', padding: '60px 20px' }}>
                    <div style={{ fontSize: '48px', marginBottom: '16px' }}>📭</div>
                    <h3 style={{ color: '#374151', marginBottom: '8px' }}>Nenhum lote quitado encontrado</h3>
                    <p style={{ color: '#6B7280' }}>Não há lotes com status "Quitado" para esta obra</p>
                </div>
            )}
        </div>
    );
};
