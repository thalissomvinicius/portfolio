import React, { useState, useEffect, useMemo } from 'react';

interface DisponibilidadesViewProps {
    empresa: number;
    obra: string;
    nomeObra?: string;
}

interface Lote {
    identificador: string;
    quadra: string;
    lote: string;
    status: number;
    statusLabel: string;
    area: number;
    valor: number;
    numVenda: number | null;
    cliente: string | null;
    codCliente: number | null;
}

interface Resumo {
    total: number;
    disponivel: number;
    vendido: number;
    reservado: number;
    quitado: number;
    suspenso: number;
    foraVenda: number;
    valorDisponivel: number;
    valorVendido: number;
    valorTotal: number;
}

interface SimulacaoResult {
    valorLote: number;
    sinal: { valor: number; percentual: number; parcelas: number; valorParcela: number };
    entrada: number;
    saldoFinanciar: number;
    parcelamento: { parcelas: number; valorParcela: number; plano: string; descricao: string };
    avista: { desconto: number; percentualDesconto: number; valorFinal: number };
    totalFinanciado: number;
}

// Status colors baseados na paleta Prime
const STATUS_CONFIG: Record<number, { label: string; color: string; gradient: string; bgLight: string }> = {
    0: { label: 'Disponível', color: '#8CC63E', gradient: 'linear-gradient(135deg, #8CC63E 0%, #6B9F2E 100%)', bgLight: '#F0FDF4' },
    1: { label: 'Vendido', color: '#0089D6', gradient: 'linear-gradient(135deg, #0089D6 0%, #00528F 100%)', bgLight: '#EBF8FF' },
    2: { label: 'Reservado', color: '#F59E0B', gradient: 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)', bgLight: '#FFFBEB' },
    3: { label: 'Proposta', color: '#8B5CF6', gradient: 'linear-gradient(135deg, #8B5CF6 0%, #6D28D9 100%)', bgLight: '#F5F3FF' },
    4: { label: 'Quitado', color: '#10B981', gradient: 'linear-gradient(135deg, #10B981 0%, #059669 100%)', bgLight: '#ECFDF5' },
    5: { label: 'Escriturado', color: '#0891B2', gradient: 'linear-gradient(135deg, #0891B2 0%, #0E7490 100%)', bgLight: '#ECFEFF' },
    6: { label: 'Em Venda', color: '#6366F1', gradient: 'linear-gradient(135deg, #6366F1 0%, #4F46E5 100%)', bgLight: '#EEF2FF' },
    7: { label: 'Suspenso', color: '#EF4444', gradient: 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)', bgLight: '#FEF2F2' },
    8: { label: 'Fora Venda', color: '#6B7280', gradient: 'linear-gradient(135deg, #6B7280 0%, #4B5563 100%)', bgLight: '#F9FAFB' },
    9: { label: 'Em Acerto', color: '#EC4899', gradient: 'linear-gradient(135deg, #EC4899 0%, #DB2777 100%)', bgLight: '#FDF2F8' },
    10: { label: 'Dação', color: '#78716C', gradient: 'linear-gradient(135deg, #78716C 0%, #57534E 100%)', bgLight: '#FAFAF9' }
};

const formatCurrency = (value: number) => {
    return value.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
};

export const DisponibilidadesView: React.FC<DisponibilidadesViewProps> = ({ empresa, obra, nomeObra }) => {
    const [loading, setLoading] = useState(true);
    const [lotes, setLotes] = useState<Lote[]>([]);
    const [resumo, setResumo] = useState<Resumo | null>(null);
    const [statusFilter, setStatusFilter] = useState<number | 'todos'>('todos');
    const [searchTerm, setSearchTerm] = useState('');

    // Modal de simulação
    const [showSimulacao, setShowSimulacao] = useState(false);
    const [selectedLote, setSelectedLote] = useState<Lote | null>(null);
    const [parcelasSinal, setParcelasSinal] = useState(1);
    const [parcelasMensais, setParcelasMensais] = useState(36);
    const [entrada, setEntrada] = useState(0);
    const [simulacaoResult, setSimulacaoResult] = useState<SimulacaoResult | null>(null);
    const [showMensagem, setShowMensagem] = useState(false);

    useEffect(() => {
        loadData();
    }, [empresa, obra]);

    const loadData = async () => {
        setLoading(true);
        try {
            const response = await fetch(`/api/disponibilidades?empresa=${empresa}&obra=${obra}`);
            const data = await response.json();
            setLotes(data.lotes || []);
            setResumo(data.resumo || null);
        } catch (error) {
            console.error('Erro ao carregar disponibilidades:', error);
        } finally {
            setLoading(false);
        }
    };

    const filteredLotes = useMemo(() => {
        let result = lotes;

        if (statusFilter !== 'todos') {
            result = result.filter(l => l.status === statusFilter);
        }

        if (searchTerm) {
            const term = searchTerm.toLowerCase();
            result = result.filter(l =>
                l.quadra.toLowerCase().includes(term) ||
                l.lote.toLowerCase().includes(term) ||
                l.identificador.toLowerCase().includes(term) ||
                (l.cliente && l.cliente.toLowerCase().includes(term))
            );
        }

        return result;
    }, [lotes, statusFilter, searchTerm]);

    const openSimulacao = (lote: Lote) => {
        console.log('Abrindo simulação para:', lote);
        setSelectedLote(lote);
        setParcelasSinal(1);
        setParcelasMensais(36);
        setEntrada(0);
        setSimulacaoResult(null);
        setShowSimulacao(true);
        setShowMensagem(false);
        console.log('showSimulacao definido como true');
    };

    const calcularSimulacao = async () => {
        if (!selectedLote) return;

        try {
            const response = await fetch(
                `/api/disponibilidades/simulacao?valor_lote=${selectedLote.valor}&parcelas_sinal=${parcelasSinal}&parcelas_mensais=${parcelasMensais}&entrada=${entrada}`
            );
            const data = await response.json();
            setSimulacaoResult(data);
        } catch (error) {
            console.error('Erro ao simular:', error);
        }
    };

    useEffect(() => {
        if (showSimulacao && selectedLote) {
            calcularSimulacao();
        }
    }, [parcelasSinal, parcelasMensais, entrada, selectedLote]);

    const gerarMensagemWhatsApp = () => {
        if (!selectedLote || !simulacaoResult) return '';

        const planoInfo = simulacaoResult.parcelamento.parcelas <= 36
            ? '📌 *Parcelas fixas* (sem correção)'
            : '📌 *Parcelas corrigidas* (correção anual IPCA)';

        let msg = `🏡 *VALLE PRIME - SIMULAÇÃO DE FINANCIAMENTO*\n\n`;
        msg += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
        msg += `🏘️ *Empreendimento:* ${nomeObra || 'N/A'}\n`;
        msg += `📍 *Lote:* Quadra ${selectedLote.quadra} | Lote ${selectedLote.lote}\n`;
        msg += `📐 *Área:* ${selectedLote.area.toFixed(2)} m²\n`;
        msg += `💰 *Valor Total:* R$ ${formatCurrency(selectedLote.valor)}\n`;
        msg += `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n`;

        msg += `💵 *SINAL DE NEGÓCIO (5%)*\n`;
        msg += `   ➤ Valor: R$ ${formatCurrency(simulacaoResult.sinal.valor)}\n`;
        if (parcelasSinal > 1) {
            msg += `   ➤ Em ${parcelasSinal}x de R$ ${formatCurrency(simulacaoResult.sinal.valorParcela)}\n`;
        }

        if (entrada > 0) {
            msg += `\n💳 *ENTRADA ADICIONAL*\n`;
            msg += `   ➤ Valor: R$ ${formatCurrency(entrada)}\n`;
        }

        msg += `\n📋 *PARCELAMENTO*\n`;
        msg += `   ➤ Saldo: R$ ${formatCurrency(simulacaoResult.saldoFinanciar)}\n`;
        msg += `   ➤ ${parcelasMensais}x de R$ ${formatCurrency(simulacaoResult.parcelamento.valorParcela)}\n`;
        msg += `   ${planoInfo}\n`;

        msg += `\n✨ *OPÇÃO À VISTA*\n`;
        msg += `   ➤ Desconto de 20%: -R$ ${formatCurrency(simulacaoResult.avista.desconto)}\n`;
        msg += `   ➤ *Valor Final: R$ ${formatCurrency(simulacaoResult.avista.valorFinal)}*\n`;

        msg += `\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n`;
        msg += `_Simulação válida para esta data._\n`;
        msg += `_Condições sujeitas a aprovação._\n`;
        msg += `\n🏢 *Valle Prime*`;

        return msg;
    };

    const copiarMensagem = async () => {
        const msg = gerarMensagemWhatsApp();
        if (!msg) {
            alert('Nenhuma mensagem para copiar. Faça uma simulação primeiro.');
            return;
        }

        try {
            // Tenta usar a API moderna primeiro (funciona em HTTPS)
            if (navigator.clipboard && window.isSecureContext) {
                await navigator.clipboard.writeText(msg);
                alert('✅ Mensagem copiada para a área de transferência!');
                return;
            }
        } catch (err) {
            console.log('Clipboard API falhou, usando fallback');
        }

        // Fallback para HTTP e navegadores antigos
        const textarea = document.createElement('textarea');
        textarea.value = msg;
        textarea.style.position = 'fixed';
        textarea.style.left = '-9999px';
        textarea.style.top = '0';
        document.body.appendChild(textarea);
        textarea.focus();
        textarea.select();

        try {
            const success = document.execCommand('copy');
            if (success) {
                alert('✅ Mensagem copiada para a área de transferência!');
            } else {
                alert('❌ Erro ao copiar. Selecione o texto manualmente.');
            }
        } catch (err) {
            alert('❌ Erro ao copiar. Selecione o texto manualmente.');
        }

        document.body.removeChild(textarea);
    };

    const enviarWhatsApp = () => {
        const msg = encodeURIComponent(gerarMensagemWhatsApp());
        window.open(`https://wa.me/?text=${msg}`, '_blank');
    };

    if (loading) {
        return (
            <div className="loading">
                <div className="spinner"></div>
            </div>
        );
    }

    return (
        <div className="animate-fade-in">
            {/* Header */}
            <div style={{
                background: 'linear-gradient(135deg, #00528F 0%, #0089D6 50%, #00A5FF 100%)',
                borderRadius: '20px',
                padding: '32px',
                marginBottom: '24px',
                position: 'relative',
                overflow: 'hidden'
            }}>
                <div style={{
                    position: 'absolute',
                    top: '-50px',
                    right: '-50px',
                    width: '200px',
                    height: '200px',
                    borderRadius: '50%',
                    background: 'radial-gradient(circle, rgba(140, 198, 62, 0.2) 0%, transparent 70%)',
                    filter: 'blur(40px)'
                }} />

                <div style={{ position: 'relative', zIndex: 1, display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <div style={{
                        width: '56px',
                        height: '56px',
                        borderRadius: '16px',
                        background: 'rgba(255,255,255,0.15)',
                        backdropFilter: 'blur(10px)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        border: '1px solid rgba(255,255,255,0.2)'
                    }}>
                        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" style={{ color: 'white' }}>
                            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                            <polyline points="9 22 9 12 15 12 15 22" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                    </div>
                    <div>
                        <h1 style={{ fontSize: '32px', fontWeight: 800, color: 'white', margin: 0, letterSpacing: '-0.5px' }}>
                            Disponibilidades
                        </h1>
                        <p style={{ fontSize: '15px', color: 'rgba(255,255,255,0.8)', margin: 0 }}>
                            Lista de lotes e simulação de financiamento
                        </p>
                    </div>
                </div>
            </div>

            {/* Cards de Resumo */}
            {resumo && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '16px', marginBottom: '24px' }}>
                    <div className="card" style={{ textAlign: 'center', borderLeft: '4px solid #8CC63E' }}>
                        <div style={{ fontSize: '12px', color: '#6B7280', marginBottom: '4px' }}>DISPONÍVEIS</div>
                        <div style={{ fontSize: '28px', fontWeight: 700, color: '#8CC63E' }}>{resumo.disponivel}</div>
                        <div style={{ fontSize: '11px', color: '#6B7280' }}>R$ {formatCurrency(resumo.valorDisponivel)}</div>
                    </div>
                    <div className="card" style={{ textAlign: 'center', borderLeft: '4px solid #0089D6' }}>
                        <div style={{ fontSize: '12px', color: '#6B7280', marginBottom: '4px' }}>VENDIDOS</div>
                        <div style={{ fontSize: '28px', fontWeight: 700, color: '#0089D6' }}>{resumo.vendido}</div>
                        <div style={{ fontSize: '11px', color: '#6B7280' }}>R$ {formatCurrency(resumo.valorVendido)}</div>
                    </div>
                    <div className="card" style={{ textAlign: 'center', borderLeft: '4px solid #10B981' }}>
                        <div style={{ fontSize: '12px', color: '#6B7280', marginBottom: '4px' }}>QUITADOS</div>
                        <div style={{ fontSize: '28px', fontWeight: 700, color: '#10B981' }}>{resumo.quitado}</div>
                    </div>
                    <div className="card" style={{ textAlign: 'center', borderLeft: '4px solid #F59E0B' }}>
                        <div style={{ fontSize: '12px', color: '#6B7280', marginBottom: '4px' }}>RESERVADOS</div>
                        <div style={{ fontSize: '28px', fontWeight: 700, color: '#F59E0B' }}>{resumo.reservado}</div>
                    </div>
                    <div className="card" style={{ textAlign: 'center', borderLeft: '4px solid #6B7280' }}>
                        <div style={{ fontSize: '12px', color: '#6B7280', marginBottom: '4px' }}>TOTAL</div>
                        <div style={{ fontSize: '28px', fontWeight: 700, color: '#1F2A33' }}>{resumo.total}</div>
                        <div style={{ fontSize: '11px', color: '#6B7280' }}>R$ {formatCurrency(resumo.valorTotal)}</div>
                    </div>
                </div>
            )}

            {/* Filtros */}
            <div className="filter-bar" style={{ marginBottom: '24px' }}>
                <div className="filter-group">
                    <label className="filter-label">Status</label>
                    <select
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value === 'todos' ? 'todos' : parseInt(e.target.value))}
                        className="filter-input"
                        style={{ width: '180px' }}
                    >
                        <option value="todos">Todos</option>
                        {Object.entries(STATUS_CONFIG).map(([code, config]) => (
                            <option key={code} value={code}>{config.label}</option>
                        ))}
                    </select>
                </div>
                <div className="filter-group">
                    <label className="filter-label">Buscar</label>
                    <input
                        type="text"
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        placeholder="Quadra, lote ou cliente..."
                        className="filter-input"
                        style={{ width: '250px' }}
                    />
                </div>
                <button onClick={loadData} className="btn btn-primary" style={{ padding: '10px 16px' }}>
                    🔄 Atualizar
                </button>
                <button
                    onClick={() => {
                        const statusParam = statusFilter !== 'todos' ? `&status=${statusFilter}` : '';
                        const usuarioParam = `&usuario=${encodeURIComponent('Sistema Valle')}`;
                        window.open(`/api/disponibilidades/pdf?empresa=${empresa}&obra=${obra}${statusParam}${usuarioParam}`, '_blank');
                    }}
                    style={{
                        padding: '10px 16px',
                        background: 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        fontSize: '14px',
                        fontWeight: 600,
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px'
                    }}
                >
                    📄 Exportar PDF
                </button>
            </div>

            {/* Tabela de Lotes */}
            <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
                <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                        <thead>
                            <tr style={{ background: 'linear-gradient(135deg, #00528F 0%, #0089D6 100%)' }}>
                                <th style={{ padding: '14px 12px', color: 'white', fontWeight: 600, textAlign: 'left' }}>Quadra</th>
                                <th style={{ padding: '14px 12px', color: 'white', fontWeight: 600, textAlign: 'left' }}>Lote</th>
                                <th style={{ padding: '14px 12px', color: 'white', fontWeight: 600, textAlign: 'left' }}>Identificador</th>
                                <th style={{ padding: '14px 12px', color: 'white', fontWeight: 600, textAlign: 'center' }}>Status</th>
                                <th style={{ padding: '14px 12px', color: 'white', fontWeight: 600, textAlign: 'right' }}>Área (m²)</th>
                                <th style={{ padding: '14px 12px', color: 'white', fontWeight: 600, textAlign: 'right' }}>Valor</th>
                                <th style={{ padding: '14px 12px', color: 'white', fontWeight: 600, textAlign: 'left' }}>Cliente</th>
                                <th style={{ padding: '14px 12px', color: 'white', fontWeight: 600, textAlign: 'center' }}>Venda</th>
                                <th style={{ padding: '14px 12px', color: 'white', fontWeight: 600, textAlign: 'center' }}>Ação</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredLotes.map((lote, index) => {
                                const config = STATUS_CONFIG[lote.status] || STATUS_CONFIG[8];
                                return (
                                    <tr key={index} style={{
                                        background: index % 2 === 0 ? 'white' : '#F8FAFC',
                                        borderBottom: '1px solid #E2E8F0',
                                        transition: 'background 0.15s'
                                    }}
                                        onMouseEnter={(e) => e.currentTarget.style.background = '#EBF8FF'}
                                        onMouseLeave={(e) => e.currentTarget.style.background = index % 2 === 0 ? 'white' : '#F8FAFC'}
                                    >
                                        <td style={{ padding: '12px', fontWeight: 600, color: '#1F2A33' }}>{lote.quadra}</td>
                                        <td style={{ padding: '12px', fontWeight: 600, color: '#1F2A33' }}>{lote.lote}</td>
                                        <td style={{ padding: '12px', color: '#6B7280', fontSize: '12px' }}>{lote.identificador}</td>
                                        <td style={{ padding: '12px', textAlign: 'center' }}>
                                            <span style={{
                                                background: config.gradient,
                                                color: 'white',
                                                padding: '4px 10px',
                                                borderRadius: '12px',
                                                fontSize: '11px',
                                                fontWeight: 600
                                            }}>
                                                {config.label}
                                            </span>
                                        </td>
                                        <td style={{ padding: '12px', textAlign: 'right', color: '#1F2A33' }}>{lote.area.toFixed(2)}</td>
                                        <td style={{ padding: '12px', textAlign: 'right', fontWeight: 700, color: '#0089D6' }}>R$ {formatCurrency(lote.valor)}</td>
                                        <td style={{ padding: '12px', color: '#1F2A33', fontSize: '12px', maxWidth: '200px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                            {lote.cliente || '-'}
                                        </td>
                                        <td style={{ padding: '12px', textAlign: 'center', color: '#6B7280' }}>{lote.numVenda || '-'}</td>
                                        <td style={{ padding: '12px', textAlign: 'center' }}>
                                            {lote.status === 0 && (
                                                <button
                                                    type="button"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        e.preventDefault();
                                                        openSimulacao(lote);
                                                    }}
                                                    style={{
                                                        padding: '6px 12px',
                                                        background: 'linear-gradient(135deg, #8CC63E 0%, #6B9F2E 100%)',
                                                        color: 'white',
                                                        border: 'none',
                                                        borderRadius: '6px',
                                                        fontSize: '11px',
                                                        fontWeight: 600,
                                                        cursor: 'pointer'
                                                    }}
                                                >
                                                    Simular
                                                </button>
                                            )}
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                        {/* Footer com totais */}
                        <tfoot>
                            <tr style={{ background: '#F0FDF4', fontWeight: 700 }}>
                                <td colSpan={4} style={{ padding: '14px 12px', textAlign: 'right', color: '#1F2A33' }}>
                                    TOTAL: {filteredLotes.length} lotes
                                </td>
                                <td style={{ padding: '14px 12px', textAlign: 'right', color: '#1F2A33' }}>
                                    {filteredLotes.reduce((sum, l) => sum + l.area, 0).toFixed(2)}
                                </td>
                                <td style={{ padding: '14px 12px', textAlign: 'right', color: '#0089D6' }}>
                                    R$ {formatCurrency(filteredLotes.reduce((sum, l) => sum + l.valor, 0))}
                                </td>
                                <td colSpan={3}></td>
                            </tr>
                        </tfoot>
                    </table>
                </div>
            </div>

            {filteredLotes.length === 0 && (
                <div className="empty-state">
                    <div className="empty-state-icon">🏠</div>
                    <p>Nenhum lote encontrado com os filtros selecionados</p>
                </div>
            )}

            {/* Modal de Simulação */}
            {showSimulacao && selectedLote && (
                <div
                    onClick={() => setShowSimulacao(false)}
                    style={{
                        position: 'fixed',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        background: 'rgba(0,0,0,0.6)',
                        display: 'flex',
                        alignItems: 'flex-start',
                        justifyContent: 'center',
                        zIndex: 9999,
                        padding: '40px 20px',
                        overflow: 'auto'
                    }}
                >
                    <div
                        onClick={(e) => e.stopPropagation()}
                        style={{
                            background: 'white',
                            borderRadius: '24px',
                            padding: '32px',
                            maxWidth: '600px',
                            width: '100%',
                            maxHeight: '90vh',
                            overflowY: 'auto',
                            boxShadow: '0 25px 50px rgba(0,0,0,0.25)',
                            position: 'relative'
                        }}
                    >
                        {/* Header Modal */}
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px' }}>
                            <div>
                                <h2 style={{ margin: 0, fontSize: '24px', fontWeight: 700, color: '#1F2A33' }}>
                                    Simulação de Financiamento
                                </h2>
                                <p style={{ margin: '4px 0 0', fontSize: '14px', color: '#6B7280' }}>
                                    Quadra {selectedLote.quadra} | Lote {selectedLote.lote}
                                </p>
                            </div>
                            <button
                                onClick={() => setShowSimulacao(false)}
                                style={{ background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer', color: '#6B7280' }}
                            >
                                ✕
                            </button>
                        </div>

                        {/* Info do Lote */}
                        <div style={{
                            background: 'linear-gradient(135deg, #00528F 0%, #0089D6 100%)',
                            borderRadius: '16px',
                            padding: '20px',
                            color: 'white',
                            marginBottom: '24px'
                        }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <div>
                                    <div style={{ fontSize: '12px', opacity: 0.8 }}>VALOR DO LOTE</div>
                                    <div style={{ fontSize: '28px', fontWeight: 700 }}>R$ {formatCurrency(selectedLote.valor)}</div>
                                </div>
                                <div style={{ textAlign: 'right' }}>
                                    <div style={{ fontSize: '12px', opacity: 0.8 }}>ÁREA</div>
                                    <div style={{ fontSize: '18px', fontWeight: 600 }}>{selectedLote.area.toFixed(2)} m²</div>
                                </div>
                            </div>
                        </div>

                        {/* Campos de entrada */}
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px', marginBottom: '24px' }}>
                            <div>
                                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#6B7280', marginBottom: '6px' }}>
                                    PARCELAS DO SINAL
                                </label>
                                <input
                                    type="number"
                                    min="1"
                                    max="24"
                                    value={parcelasSinal}
                                    onChange={(e) => setParcelasSinal(Math.max(1, Math.min(24, parseInt(e.target.value) || 1)))}
                                    className="form-input"
                                />
                            </div>
                            <div>
                                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#6B7280', marginBottom: '6px' }}>
                                    PARCELAS MENSAIS
                                </label>
                                <input
                                    type="number"
                                    min="2"
                                    max="200"
                                    value={parcelasMensais}
                                    onChange={(e) => setParcelasMensais(Math.max(2, Math.min(200, parseInt(e.target.value) || 36)))}
                                    className="form-input"
                                />
                            </div>
                            <div>
                                <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: '#6B7280', marginBottom: '6px' }}>
                                    ENTRADA (OPCIONAL)
                                </label>
                                <input
                                    type="number"
                                    min="0"
                                    value={entrada}
                                    onChange={(e) => setEntrada(Math.max(0, parseFloat(e.target.value) || 0))}
                                    className="form-input"
                                    placeholder="R$ 0,00"
                                />
                            </div>
                        </div>

                        {/* Resultado da Simulação */}
                        {simulacaoResult && (
                            <>
                                <div style={{
                                    background: '#F8FAFC',
                                    borderRadius: '16px',
                                    padding: '20px',
                                    marginBottom: '16px'
                                }}>
                                    {/* Sinal */}
                                    <div style={{ marginBottom: '16px', paddingBottom: '16px', borderBottom: '1px solid #E2E8F0' }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                            <div>
                                                <span style={{ fontSize: '14px', fontWeight: 600, color: '#1F2A33' }}>💵 Sinal (5%)</span>
                                                {parcelasSinal > 1 && (
                                                    <span style={{ fontSize: '12px', color: '#6B7280', marginLeft: '8px' }}>
                                                        em {parcelasSinal}x
                                                    </span>
                                                )}
                                            </div>
                                            <div style={{ textAlign: 'right' }}>
                                                <div style={{ fontSize: '18px', fontWeight: 700, color: '#8CC63E' }}>
                                                    R$ {formatCurrency(simulacaoResult.sinal.valor)}
                                                </div>
                                                {parcelasSinal > 1 && (
                                                    <div style={{ fontSize: '12px', color: '#6B7280' }}>
                                                        {parcelasSinal}x de R$ {formatCurrency(simulacaoResult.sinal.valorParcela)}
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Entrada */}
                                    {entrada > 0 && (
                                        <div style={{ marginBottom: '16px', paddingBottom: '16px', borderBottom: '1px solid #E2E8F0' }}>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                                <span style={{ fontSize: '14px', fontWeight: 600, color: '#1F2A33' }}>💳 Entrada</span>
                                                <span style={{ fontSize: '18px', fontWeight: 700, color: '#6366F1' }}>
                                                    R$ {formatCurrency(entrada)}
                                                </span>
                                            </div>
                                        </div>
                                    )}

                                    {/* Parcelamento */}
                                    <div style={{ marginBottom: '16px', paddingBottom: '16px', borderBottom: '1px solid #E2E8F0' }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                            <div>
                                                <span style={{ fontSize: '14px', fontWeight: 600, color: '#1F2A33' }}>📋 Parcelas</span>
                                                <div style={{ fontSize: '12px', color: '#6B7280', marginTop: '2px' }}>
                                                    {simulacaoResult.parcelamento.plano}
                                                </div>
                                            </div>
                                            <div style={{ textAlign: 'right' }}>
                                                <div style={{ fontSize: '18px', fontWeight: 700, color: '#0089D6' }}>
                                                    {parcelasMensais}x de R$ {formatCurrency(simulacaoResult.parcelamento.valorParcela)}
                                                </div>
                                                <div style={{ fontSize: '12px', color: '#6B7280' }}>
                                                    Saldo: R$ {formatCurrency(simulacaoResult.saldoFinanciar)}
                                                </div>
                                            </div>
                                        </div>
                                        {parcelasMensais > 36 && (
                                            <div style={{
                                                marginTop: '8px',
                                                background: '#FEF3C7',
                                                padding: '8px 12px',
                                                borderRadius: '8px',
                                                fontSize: '12px',
                                                color: '#92400E'
                                            }}>
                                                ⚠️ {simulacaoResult.parcelamento.descricao}
                                            </div>
                                        )}
                                    </div>

                                    {/* À Vista */}
                                    <div style={{
                                        background: 'linear-gradient(135deg, #10B981 0%, #059669 100%)',
                                        borderRadius: '12px',
                                        padding: '16px',
                                        color: 'white'
                                    }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                            <div>
                                                <span style={{ fontSize: '14px', fontWeight: 600 }}>✨ À Vista (20% desc.)</span>
                                                <div style={{ fontSize: '12px', opacity: 0.9 }}>
                                                    Economia: R$ {formatCurrency(simulacaoResult.avista.desconto)}
                                                </div>
                                            </div>
                                            <div style={{ fontSize: '24px', fontWeight: 800 }}>
                                                R$ {formatCurrency(simulacaoResult.avista.valorFinal)}
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Botões de ação */}
                                <div style={{ display: 'flex', gap: '12px' }}>
                                    <button
                                        onClick={() => setShowMensagem(!showMensagem)}
                                        style={{
                                            flex: 1,
                                            padding: '14px',
                                            background: 'linear-gradient(135deg, #00528F 0%, #0089D6 100%)',
                                            color: 'white',
                                            border: 'none',
                                            borderRadius: '12px',
                                            fontSize: '14px',
                                            fontWeight: 600,
                                            cursor: 'pointer',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            gap: '8px'
                                        }}
                                    >
                                        📱 {showMensagem ? 'Ocultar' : 'Ver'} Mensagem
                                    </button>
                                    <button
                                        onClick={copiarMensagem}
                                        style={{
                                            padding: '14px 20px',
                                            background: '#F1F5F9',
                                            color: '#475569',
                                            border: 'none',
                                            borderRadius: '12px',
                                            fontSize: '14px',
                                            fontWeight: 600,
                                            cursor: 'pointer'
                                        }}
                                    >
                                        📋 Copiar
                                    </button>
                                    <button
                                        onClick={enviarWhatsApp}
                                        style={{
                                            padding: '14px 20px',
                                            background: 'linear-gradient(135deg, #25D366 0%, #128C7E 100%)',
                                            color: 'white',
                                            border: 'none',
                                            borderRadius: '12px',
                                            fontSize: '14px',
                                            fontWeight: 600,
                                            cursor: 'pointer'
                                        }}
                                    >
                                        WhatsApp
                                    </button>
                                </div>

                                {/* Preview da mensagem */}
                                {showMensagem && (
                                    <div style={{
                                        marginTop: '16px',
                                        background: '#075E54',
                                        borderRadius: '12px',
                                        padding: '16px',
                                        color: 'white',
                                        fontFamily: 'monospace',
                                        fontSize: '12px',
                                        whiteSpace: 'pre-wrap',
                                        maxHeight: '300px',
                                        overflowY: 'auto'
                                    }}>
                                        {gerarMensagemWhatsApp()}
                                    </div>
                                )}
                            </>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};
