import React, { useState, useEffect } from 'react';
import { formatCurrency } from '../utils/format';
import { PageHeader } from './shared';

interface RecebimentosViewProps {
    empresa: number;
    obra: string;
    refreshKey: number;
}

interface Recebimento {
    venda: number;
    codCliente: number;
    nomeCliente: string;
    identificador: string;
    quadra: string;
    lote: string;
    parcela: string;
    tipoParcela: string;
    dataVencimento: string;
    dataDeposito: string;
    dataConciliacao: string;
    dataRecebimento: string;
    valorPago: number;
    valorPrincipal: number;
    correcao: number;
    multa: number;
    juros: number;
    status: 'ADIANTADA' | 'NORMAL' | 'ATRASADA';
    banco: string;
    conta: string;
    descricaoConta: string;
    corretor: string;
}

interface TipoParcela {
    tipo: string;
    qtd: number;
    valor: number;
}

interface Totais {
    totalRecebido: number;
    totalPrincipal: number;
    qtdParcelas: number;
    adiantadas: number;
    normais: number;
    atrasadas: number;
    porTipo?: TipoParcela[];
}

interface ResumoTipo {
    tipoCodigo: string;
    tipoDescricao: string;
    qtdParcelas: number;
    totalValor: number;
    vencidos: number;
    valorVencido: number;
    aVencer: number;
    valorAVencer: number;
}

interface TotaisAReceber {
    totalValor: number;
    qtdParcelas: number;
    vencidos: number;
    valorVencido: number;
    hoje: number;
    aVencer: number;
}

export const RecebimentosView: React.FC<RecebimentosViewProps> = ({ empresa, obra, refreshKey }) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [data, setData] = useState<Recebimento[]>([]);
    const [totais, setTotais] = useState<Totais | null>(null);

    // Estado para A Receber
    const [aReceberData, setAReceberData] = useState<ResumoTipo[]>([]);
    const [aReceberTotais, setAReceberTotais] = useState<TotaisAReceber | null>(null);

    // Tab ativa
    const [activeTab, setActiveTab] = useState<'recebidos' | 'sinais' | 'completo'>('recebidos');

    // PDF options
    const [pdfTipo, setPdfTipo] = useState<'sinais' | 'completo'>('sinais');
    const [showPdfOptions, setShowPdfOptions] = useState(false);

    // Filtros de data - vazios por padrão para buscar todos os períodos
    const [dataInicio, setDataInicio] = useState('');
    const [dataFim, setDataFim] = useState('');
    const [tiposParcelaSelecionados, setTiposParcelaSelecionados] = useState<string[]>([]);

    // Filtro de corretor
    const [corretores, setCorretores] = useState<string[]>([]);
    const [corretorSelecionado, setCorretorSelecionado] = useState<string>('');

    const tiposParcela = [
        { codigo: '0', descricao: 'Seguro' },
        { codigo: '1', descricao: 'Custas' },
        { codigo: '2', descricao: 'Acerto final' },
        { codigo: 'A', descricao: 'Resíduo Agrup.' },
        { codigo: 'B', descricao: 'Balão' },
        { codigo: 'C', descricao: 'Chave' },
        { codigo: 'E', descricao: 'Entrada' },
        { codigo: 'ER', descricao: 'Entrada Renegoc' },
        { codigo: 'I', descricao: 'Intermediação' },
        { codigo: 'IN', descricao: 'Intermediárias' },
        { codigo: 'P', descricao: 'Parcela' },
        { codigo: 'R', descricao: 'Resíduo' },
        { codigo: 'S', descricao: 'C. CORRETAGEM' },
    ];

    const loadData = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(
                `/api/recebimentos?empresa=${empresa}&obra=${obra}&data_inicio=${dataInicio}&data_fim=${dataFim}&corretor=${encodeURIComponent(corretorSelecionado)}`
            );
            if (!response.ok) throw new Error('Erro ao carregar dados');
            const result = await response.json();
            setData(result.data);
            setTotais(result.totais);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erro ao carregar dados');
        } finally {
            setLoading(false);
        }
    };

    const loadAReceber = async (tipo: 'sinais' | 'completo') => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(
                `/api/a-receber?empresa=${empresa}&obra=${obra}&tipo=${tipo}`
            );
            if (!response.ok) throw new Error('Erro ao carregar dados');
            const result = await response.json();
            setAReceberData(result.data);
            setAReceberTotais(result.totais);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erro ao carregar dados');
        } finally {
            setLoading(false);
        }
    };

    const downloadPDF = async () => {
        try {
            const url = `/api/relatorio-pdf?empresa=${empresa}&obra=${obra}&data_inicio=${dataInicio}&data_fim=${dataFim}&tipo_a_receber=${pdfTipo}`;
            const response = await fetch(url);
            if (!response.ok) throw new Error('Erro ao gerar PDF');
            const blob = await response.blob();
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `relatorio_recebimentos_${dataInicio}_${dataFim}.pdf`;
            link.click();
            setShowPdfOptions(false);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erro ao gerar PDF');
        }
    };

    // Carregar lista de corretores
    const loadCorretores = async () => {
        try {
            const response = await fetch(`/api/corretores/lista?empresa=${empresa}&obra=${obra}`);
            if (response.ok) {
                const result = await response.json();
                setCorretores(result.corretores || []);
            }
        } catch (err) {
            console.error('Erro ao carregar corretores:', err);
        }
    };

    useEffect(() => {
        loadCorretores();
    }, [empresa, obra]);

    useEffect(() => {
        if (activeTab === 'recebidos') {
            loadData();
        } else {
            loadAReceber(activeTab);
        }
    }, [empresa, obra, refreshKey, activeTab]);

    const toggleTipoParcela = (codigo: string) => {
        setTiposParcelaSelecionados(prev =>
            prev.includes(codigo) ? prev.filter(c => c !== codigo) : [...prev, codigo]
        );
    };

    // Filtrar dados por tipo de parcela e corretor
    const filteredData = data.filter((rec) => {
        // Filtro por tipo de parcela
        const passaTipo = tiposParcelaSelecionados.length === 0 ||
            tiposParcelaSelecionados.some(tipo => rec.tipoParcela.startsWith(tipo + ' -'));

        // Filtro por corretor - precisa buscar pelo nome do cliente (aproximação)
        // Para filtrar por corretor nos recebimentos, precisaríamos ter essa info no backend
        return passaTipo;
    });

    const filteredTotais = (tiposParcelaSelecionados.length > 0) && totais ? {
        ...totais,
        totalRecebido: filteredData.reduce((sum, r) => sum + (r.valorPago || 0), 0),
        qtdParcelas: filteredData.length,
    } : totais;

    return (
        <div className="animate-fade-in">
            {/* Header */}
            <PageHeader
                title="Recebimentos"
                subtitle="Depósitos, pagamentos e valores a receber"
                style={{ marginBottom: '16px' }}
            />

            {/* Tabs */}
            <div style={{ display: 'flex', gap: '4px', marginBottom: '16px', background: 'var(--surface-color)', padding: '4px', borderRadius: '10px', width: 'fit-content' }}>
                <button onClick={() => setActiveTab('recebidos')} style={{ padding: '10px 20px', border: 'none', borderRadius: '8px', fontSize: '13px', fontWeight: 600, cursor: 'pointer', background: activeTab === 'recebidos' ? 'linear-gradient(135deg, #2563EB, #1D4ED8)' : 'transparent', color: activeTab === 'recebidos' ? 'white' : 'var(--text-secondary)' }}>
                    💰 Recebidos
                </button>
                <button onClick={() => setActiveTab('sinais')} style={{ padding: '10px 20px', border: 'none', borderRadius: '8px', fontSize: '13px', fontWeight: 600, cursor: 'pointer', background: activeTab === 'sinais' ? 'linear-gradient(135deg, #F59E0B, #D97706)' : 'transparent', color: activeTab === 'sinais' ? 'white' : 'var(--text-secondary)' }}>
                    📋 A Receber (Sinais)
                </button>
                <button onClick={() => setActiveTab('completo')} style={{ padding: '10px 20px', border: 'none', borderRadius: '8px', fontSize: '13px', fontWeight: 600, cursor: 'pointer', background: activeTab === 'completo' ? 'linear-gradient(135deg, #10B981, #059669)' : 'transparent', color: activeTab === 'completo' ? 'white' : 'var(--text-secondary)' }}>
                    📊 A Receber (Completo)
                </button>
            </div>

            {/* Filter Section */}
            <div className="card" style={{ marginBottom: '24px', padding: '20px' }}>
                <div style={{ display: 'flex', alignItems: 'flex-end', gap: '16px', marginBottom: activeTab === 'recebidos' ? '16px' : '0', flexWrap: 'wrap' }}>
                    <div className="filter-group">
                        <label className="filter-label">Data Início</label>
                        <input type="date" value={dataInicio} onChange={(e) => setDataInicio(e.target.value)} className="filter-input" style={{ width: '150px' }} />
                    </div>
                    <div className="filter-group">
                        <label className="filter-label">Data Fim</label>
                        <input type="date" value={dataFim} onChange={(e) => setDataFim(e.target.value)} className="filter-input" style={{ width: '150px' }} />
                    </div>
                    <div className="filter-group">
                        <label className="filter-label">Corretor</label>
                        <select
                            value={corretorSelecionado}
                            onChange={(e) => setCorretorSelecionado(e.target.value)}
                            className="filter-input"
                            style={{ width: '200px', height: '42px' }}
                        >
                            <option value="">Todos os Corretores</option>
                            {corretores.map((c, i) => (
                                <option key={i} value={c}>{c}</option>
                            ))}
                        </select>
                    </div>
                    <button onClick={() => activeTab === 'recebidos' ? loadData() : loadAReceber(activeTab)} className="btn btn-primary" disabled={loading} style={{ display: 'flex', alignItems: 'center', gap: '8px', height: '42px' }}>
                        {loading ? '⏳ Carregando...' : '🔍 Buscar'}
                    </button>

                    {/* PDF Button */}
                    <div style={{ position: 'relative' }}>
                        <button onClick={() => setShowPdfOptions(!showPdfOptions)} className="btn" style={{ display: 'flex', alignItems: 'center', gap: '8px', height: '42px', background: 'linear-gradient(135deg, #059669, #047857)', color: 'white', border: 'none' }}>
                            📄 Relatório PDF
                        </button>
                        {showPdfOptions && (
                            <div style={{ position: 'absolute', top: '48px', right: 0, background: 'white', borderRadius: '8px', boxShadow: '0 4px 12px rgba(0,0,0,0.15)', padding: '16px', zIndex: 100, minWidth: '280px' }}>
                                <p style={{ fontWeight: 600, marginBottom: '12px', color: '#374151' }}>Opções do Relatório</p>
                                <div style={{ marginBottom: '12px' }}>
                                    <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer', marginBottom: '8px' }}>
                                        <input type="radio" checked={pdfTipo === 'sinais'} onChange={() => setPdfTipo('sinais')} />
                                        <span style={{ fontSize: '13px' }}>Somente Sinais em Aberto</span>
                                    </label>
                                    <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
                                        <input type="radio" checked={pdfTipo === 'completo'} onChange={() => setPdfTipo('completo')} />
                                        <span style={{ fontSize: '13px' }}>Valor Completo (Sinais + Parcelas)</span>
                                    </label>
                                </div>
                                <div style={{ display: 'flex', gap: '8px' }}>
                                    <button onClick={downloadPDF} style={{ flex: 1, padding: '8px 16px', background: 'linear-gradient(135deg, #2563EB, #1D4ED8)', color: 'white', border: 'none', borderRadius: '6px', fontWeight: 600, cursor: 'pointer' }}>⬇️ Baixar PDF</button>
                                    <button onClick={() => setShowPdfOptions(false)} style={{ padding: '8px 16px', background: '#E5E7EB', color: '#374151', border: 'none', borderRadius: '6px', cursor: 'pointer' }}>Cancelar</button>
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Limpar Filtros Button */}
                    {(dataInicio || dataFim || corretorSelecionado) && (
                        <button
                            onClick={() => {
                                setDataInicio('');
                                setDataFim('');
                                setCorretorSelecionado('');
                            }}
                            className="btn"
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px',
                                height: '42px',
                                background: '#E5E7EB',
                                color: '#374151',
                                border: 'none'
                            }}
                        >
                            🗑️ Limpar Filtros
                        </button>
                    )}
                </div>

                {/* Tipo de Parcela filter - only for Recebidos */}
                {activeTab === 'recebidos' && (
                    <div>
                        <label className="filter-label" style={{ marginBottom: '8px', display: 'block' }}>
                            Tipo de Parcela {tiposParcelaSelecionados.length > 0 && <span style={{ color: '#2563EB', fontWeight: 600 }}>({tiposParcelaSelecionados.length} selecionados)</span>}
                        </label>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                            {tiposParcela.map((tipo) => {
                                const isSelected = tiposParcelaSelecionados.includes(tipo.codigo);
                                return (
                                    <button key={tipo.codigo} type="button" onClick={() => toggleTipoParcela(tipo.codigo)} style={{ padding: '6px 14px', borderRadius: '6px', border: isSelected ? '2px solid #2563EB' : '1px solid #D1D5DB', fontSize: '12px', fontWeight: isSelected ? 600 : 500, cursor: 'pointer', background: isSelected ? 'linear-gradient(135deg, #EBF5FF, #DBEAFE)' : 'white', color: isSelected ? '#1D4ED8' : '#374151' }} title={tipo.descricao}>
                                        <strong>{tipo.codigo}</strong> {tipo.descricao}
                                    </button>
                                );
                            })}
                            {tiposParcelaSelecionados.length > 0 && (
                                <button type="button" onClick={() => setTiposParcelaSelecionados([])} style={{ padding: '6px 14px', borderRadius: '6px', border: 'none', fontSize: '12px', fontWeight: 500, cursor: 'pointer', background: '#FEE2E2', color: '#DC2626' }}>✕ Limpar</button>
                            )}
                        </div>
                    </div>
                )}
            </div>

            {/* Error */}
            {error && (
                <div className="card" style={{ background: '#FEE2E2', borderColor: '#EF4444', marginBottom: '24px' }}>
                    <p style={{ color: '#991B1B' }}>❌ {error}</p>
                </div>
            )}

            {/* Loading */}
            {loading && (
                <div className="loading">
                    <div className="spinner"></div>
                </div>
            )}

            {/* RECEBIDOS TAB */}
            {activeTab === 'recebidos' && filteredTotais && !loading && (
                <>
                    <div className="metric-grid" style={{ gridTemplateColumns: 'repeat(2, 1fr)', marginBottom: '24px', maxWidth: '600px' }}>
                        <div className="metric-card">
                            <div className="metric-card-icon">💰</div>
                            <div className="metric-card-content">
                                <div className="metric-label">TOTAL RECEBIDO</div>
                                <div className="metric-value success" style={{ fontSize: '22px' }}>R$ {formatCurrency(filteredTotais.totalRecebido)}</div>
                            </div>
                        </div>
                        <div className="metric-card">
                            <div className="metric-card-icon">📋</div>
                            <div className="metric-card-content">
                                <div className="metric-label">PARCELAS</div>
                                <div className="metric-value primary" style={{ fontSize: '22px' }}>{filteredTotais.qtdParcelas}</div>
                            </div>
                        </div>
                    </div>

                    {/* Breakdown por Tipo de Parcela */}
                    {filteredTotais.porTipo && filteredTotais.porTipo.length > 0 && (
                        <div className="card" style={{ marginBottom: '24px', padding: '16px' }}>
                            <h4 style={{ fontSize: '14px', fontWeight: 600, color: '#374151', marginBottom: '12px' }}>📊 RECEBIDO POR TIPO</h4>
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '12px' }}>
                                {filteredTotais.porTipo.map((t, i) => (
                                    <div key={i} style={{ background: 'linear-gradient(135deg, #f8fafc, #f1f5f9)', padding: '12px 16px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                                        <div style={{ fontSize: '11px', color: '#64748b', fontWeight: 600, marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>{t.tipo}</div>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                                            <span style={{ fontSize: '18px', fontWeight: 700, color: '#059669' }}>R$ {formatCurrency(t.valor)}</span>
                                            <span style={{ fontSize: '12px', color: '#64748b', fontWeight: 500 }}>{t.qtd} parc.</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                            <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '2px solid #e2e8f0', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ fontSize: '14px', fontWeight: 700, color: '#1e293b' }}>📍 TOTAL GERAL:</span>
                                <span style={{ fontSize: '20px', fontWeight: 700, color: '#059669' }}>R$ {formatCurrency(filteredTotais.totalRecebido)}</span>
                            </div>
                        </div>
                    )}

                    <div className="table-container">
                        <div className="table-header-row">
                            <span className="table-title">📊 Recebimentos do Período</span>
                            <span className="badge badge-primary">{filteredData.length} registros</span>
                        </div>
                        <div style={{ overflowX: 'auto' }}>
                            <table style={{ minWidth: '1100px' }}>
                                <thead>
                                    <tr>
                                        <th style={{ width: '70px' }}>Venda</th>
                                        <th style={{ width: '200px' }}>Cliente</th>
                                        <th style={{ width: '60px', textAlign: 'center' }}>Quadra</th>
                                        <th style={{ width: '60px', textAlign: 'center' }}>Lote</th>
                                        <th style={{ width: '80px', textAlign: 'center' }}>Parcela</th>
                                        <th style={{ width: '150px' }}>Tipo</th>
                                        <th style={{ width: '100px' }}>Vencimento</th>
                                        <th style={{ width: '100px' }}>Depósito</th>
                                        <th style={{ width: '110px', textAlign: 'right' }}>Valor Pago</th>
                                        <th style={{ width: '150px' }}>Conta</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredData.map((rec, index) => (
                                        <tr key={`${rec.venda}-${rec.parcela}-${index}`}>
                                            <td style={{ fontWeight: 600, fontSize: '13px' }}>{rec.venda}</td>
                                            <td style={{ fontSize: '13px', maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={rec.nomeCliente}>{rec.nomeCliente}</td>
                                            <td style={{ textAlign: 'center', fontWeight: 600, color: '#2563EB' }}>{rec.quadra || '-'}</td>
                                            <td style={{ textAlign: 'center', fontWeight: 600, color: '#2563EB' }}>{rec.lote || '-'}</td>
                                            <td style={{ textAlign: 'center', fontWeight: 500, fontSize: '12px' }}>{rec.parcela}</td>
                                            <td style={{ fontSize: '11px', maxWidth: '150px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={rec.tipoParcela}>{rec.tipoParcela}</td>
                                            <td style={{ fontSize: '12px', color: '#64748B' }}>{rec.dataVencimento}</td>
                                            <td style={{ fontSize: '12px', color: '#64748B' }}>{rec.dataDeposito}</td>
                                            <td style={{ textAlign: 'right', fontWeight: 600, color: '#10B981', fontSize: '13px' }}>R$ {formatCurrency(rec.valorPago)}</td>
                                            <td style={{ fontSize: '11px', maxWidth: '150px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={rec.descricaoConta}>{rec.conta}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </>
            )}

            {/* A RECEBER TABS */}
            {(activeTab === 'sinais' || activeTab === 'completo') && aReceberTotais && !loading && (
                <>
                    {/* Totais gerais */}
                    <div className="metric-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)', marginBottom: '24px' }}>
                        <div className="metric-card">
                            <div className="metric-card-icon">💵</div>
                            <div className="metric-card-content">
                                <div className="metric-label">TOTAL A RECEBER</div>
                                <div className="metric-value" style={{ fontSize: '22px', color: '#F59E0B' }}>R$ {formatCurrency(aReceberTotais.totalValor)}</div>
                            </div>
                        </div>
                        <div className="metric-card">
                            <div className="metric-card-icon">📋</div>
                            <div className="metric-card-content">
                                <div className="metric-label">PARCELAS</div>
                                <div className="metric-value primary" style={{ fontSize: '22px' }}>{aReceberTotais.qtdParcelas}</div>
                            </div>
                        </div>
                        <div className="metric-card">
                            <div className="metric-card-icon">⚠️</div>
                            <div className="metric-card-content">
                                <div className="metric-label">VENCIDOS</div>
                                <div className="metric-value danger" style={{ fontSize: '22px' }}>{aReceberTotais.vencidos}</div>
                                <div style={{ fontSize: '12px', color: '#DC2626' }}>R$ {formatCurrency(aReceberTotais.valorVencido)}</div>
                            </div>
                        </div>
                        <div className="metric-card">
                            <div className="metric-card-icon">📅</div>
                            <div className="metric-card-content">
                                <div className="metric-label">A VENCER</div>
                                <div className="metric-value success" style={{ fontSize: '22px' }}>{aReceberTotais.aVencer}</div>
                            </div>
                        </div>
                    </div>

                    {/* Resumo por tipo de parcela */}
                    <div className="table-container">
                        <div className="table-header-row">
                            <span className="table-title">📊 Resumo por Tipo de Parcela</span>
                            <span className="badge badge-warning">{aReceberData.length} tipos</span>
                        </div>
                        <div style={{ overflowX: 'auto' }}>
                            <table style={{ minWidth: '700px' }}>
                                <thead>
                                    <tr>
                                        <th style={{ width: '80px' }}>Código</th>
                                        <th style={{ width: '200px' }}>Tipo</th>
                                        <th style={{ width: '100px', textAlign: 'center' }}>Parcelas</th>
                                        <th style={{ width: '130px', textAlign: 'right' }}>Total</th>
                                        <th style={{ width: '80px', textAlign: 'center' }}>Vencidos</th>
                                        <th style={{ width: '130px', textAlign: 'right' }}>Valor Vencido</th>
                                        <th style={{ width: '80px', textAlign: 'center' }}>A Vencer</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {aReceberData.map((item, index) => (
                                        <tr key={`${item.tipoCodigo}-${index}`}>
                                            <td style={{ fontWeight: 700, fontSize: '14px', color: '#2563EB' }}>{item.tipoCodigo}</td>
                                            <td style={{ fontSize: '13px' }}>{item.tipoDescricao.toUpperCase()}</td>
                                            <td style={{ textAlign: 'center', fontWeight: 600 }}>{item.qtdParcelas}</td>
                                            <td style={{ textAlign: 'right', fontWeight: 600, color: '#F59E0B', fontSize: '14px' }}>R$ {formatCurrency(item.totalValor)}</td>
                                            <td style={{ textAlign: 'center' }}>
                                                <span style={{
                                                    display: 'inline-block',
                                                    padding: '4px 8px',
                                                    borderRadius: '4px',
                                                    fontSize: '12px',
                                                    fontWeight: 600,
                                                    background: item.vencidos > 0 ? '#FEE2E2' : '#F3F4F6',
                                                    color: item.vencidos > 0 ? '#DC2626' : '#6B7280'
                                                }}>
                                                    {item.vencidos}
                                                </span>
                                            </td>
                                            <td style={{ textAlign: 'right', color: '#DC2626', fontWeight: 500 }}>R$ {formatCurrency(item.valorVencido)}</td>
                                            <td style={{ textAlign: 'center' }}>
                                                <span style={{
                                                    display: 'inline-block',
                                                    padding: '4px 8px',
                                                    borderRadius: '4px',
                                                    fontSize: '12px',
                                                    fontWeight: 600,
                                                    background: '#D1FAE5',
                                                    color: '#059669'
                                                }}>
                                                    {item.aVencer}
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </>
            )}

            {/* Empty State */}
            {!loading && !error && activeTab === 'recebidos' && filteredData.length === 0 && totais && (
                <div className="card" style={{ textAlign: 'center', padding: '60px 20px' }}>
                    <div style={{ fontSize: '48px', marginBottom: '16px' }}>📭</div>
                    <h3 style={{ color: '#374151', marginBottom: '8px' }}>Nenhum recebimento encontrado</h3>
                    <p style={{ color: '#6B7280' }}>Não há depósitos conciliados no período selecionado</p>
                </div>
            )}

            {!loading && !error && (activeTab === 'sinais' || activeTab === 'completo') && aReceberData.length === 0 && aReceberTotais && (
                <div className="card" style={{ textAlign: 'center', padding: '60px 20px' }}>
                    <div style={{ fontSize: '48px', marginBottom: '16px' }}>✅</div>
                    <h3 style={{ color: '#374151', marginBottom: '8px' }}>Nenhum valor a receber</h3>
                    <p style={{ color: '#6B7280' }}>Não há {activeTab === 'sinais' ? 'sinais' : 'valores'} em aberto</p>
                </div>
            )}
        </div>
    );
};
