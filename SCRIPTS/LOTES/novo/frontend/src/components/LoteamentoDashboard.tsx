import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import { formatCurrency } from '../utils/format';

interface LoteamentoDashboardProps {
    empresa: number;
    obra: string;
}

interface StatusUnidade {
    status: number;
    label: string;
    color: string;
    quantidade: number;
    valor: number;
    percentual: number;
    percentualValor: number;
}

interface VendaDiaria {
    data: string;
    vendas: number;
    cancelamentos: number;
    valorTotal: number;
    valorCancelamentos: number;
    valorMedio: number;
}

interface ResumoData {
    obra: string;
    totalUnidades: number;
    totalValor: number;
    statusUnidades: StatusUnidade[];
}

interface VendasData {
    totalVendas: number;
    totalValor: number;
    valorMedio: number;
    vendasDiarias: VendaDiaria[];
}

// Cores para cada status
const STATUS_COLORS: Record<number, { bg: string; gradient: string }> = {
    0: { bg: '#10B981', gradient: 'linear-gradient(135deg, #059669 0%, #10B981 100%)' },  // Disponivel
    1: { bg: '#3B82F6', gradient: 'linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%)' },  // Vendido
    2: { bg: '#F59E0B', gradient: 'linear-gradient(135deg, #D97706 0%, #FBBF24 100%)' },  // Reservado
    3: { bg: '#8B5CF6', gradient: 'linear-gradient(135deg, #6D28D9 0%, #A78BFA 100%)' },  // Proposta
    4: { bg: '#14B8A6', gradient: 'linear-gradient(135deg, #0D9488 0%, #2DD4BF 100%)' },  // Quitado
    5: { bg: '#0891B2', gradient: 'linear-gradient(135deg, #0E7490 0%, #22D3EE 100%)' },  // Escriturado
    6: { bg: '#6366F1', gradient: 'linear-gradient(135deg, #4338CA 0%, #818CF8 100%)' },  // Em Venda
    7: { bg: '#EF4444', gradient: 'linear-gradient(135deg, #DC2626 0%, #F87171 100%)' },  // Suspenso
    8: { bg: '#6B7280', gradient: 'linear-gradient(135deg, #4B5563 0%, #9CA3AF 100%)' },  // Fora de Venda
    9: { bg: '#EC4899', gradient: 'linear-gradient(135deg, #DB2777 0%, #F472B6 100%)' },  // Em Acerto
    10: { bg: '#78716C', gradient: 'linear-gradient(135deg, #57534E 0%, #A8A29E 100%)' }, // Dacao
};

export const LoteamentoDashboard: React.FC<LoteamentoDashboardProps> = ({ empresa, obra }) => {
    const [loading, setLoading] = useState(true);
    const [resumo, setResumo] = useState<ResumoData | null>(null);
    const [vendas, setVendas] = useState<VendasData | null>(null);
    const [error, setError] = useState<string | null>(null);

    // Estado para modal de PDF
    const [showPdfModal, setShowPdfModal] = useState(false);
    const [pdfDtInicio, setPdfDtInicio] = useState(() => {
        const d = new Date();
        d.setDate(d.getDate() - 30);
        return d.toISOString().split('T')[0];
    });
    const [pdfDtFim, setPdfDtFim] = useState(() => new Date().toISOString().split('T')[0]);

    const gerarPdf = () => {
        const url = `/api/relatorio-executivo/pdf?empresa=${empresa}&obra=${obra}&data_inicio=${pdfDtInicio}&data_fim=${pdfDtFim}`;
        window.open(url, '_blank');
        setShowPdfModal(false);
    };

    const loadData = async () => {
        setLoading(true);
        setError(null);

        try {
            const [resumoRes, vendasRes] = await Promise.all([
                fetch(`/api/loteamento/resumo?empresa=${empresa}&obra=${obra}`),
                fetch(`/api/loteamento/vendas-diarias?empresa=${empresa}&obra=${obra}&dias=30`)
            ]);

            if (!resumoRes.ok || !vendasRes.ok) {
                throw new Error('Erro ao carregar dados');
            }

            const resumoData = await resumoRes.json();
            const vendasData = await vendasRes.json();

            setResumo(resumoData);
            setVendas(vendasData);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erro ao carregar dados');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (empresa && obra) {
            loadData();
        }
    }, [empresa, obra]);

    // Calcular altura maxima para barras
    const maxVendas = vendas?.vendasDiarias?.length
        ? Math.max(...vendas.vendasDiarias.map(v => v.vendas))
        : 1;

    if (loading) {
        return (
            <div className="loading">
                <div className="spinner"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="card" style={{ background: '#FEE2E2', borderColor: '#EF4444' }}>
                <p style={{ color: '#991B1B' }}>Erro: {error}</p>
                <button onClick={loadData} className="btn btn-primary" style={{ marginTop: '12px' }}>
                    Tentar Novamente
                </button>
            </div>
        );
    }

    // Ordenar status por quantidade
    const statusOrdenados = [...(resumo?.statusUnidades || [])].sort((a, b) => b.quantidade - a.quantidade);

    return (
        <div className="animate-fade-in">
            {/* Modal de Período para PDF - usando Portal para cobrir tela inteira */}
            {showPdfModal && ReactDOM.createPortal(
                <div style={{
                    position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh',
                    background: 'rgba(0,0,0,0.6)', display: 'flex', alignItems: 'flex-start', justifyContent: 'center',
                    zIndex: 99999, paddingTop: '80px', overflowY: 'auto'
                }}>
                    <div style={{
                        background: 'white', borderRadius: '16px', padding: '32px', width: '420px',
                        boxShadow: '0 25px 50px rgba(0,0,0,0.25)', marginBottom: '40px'
                    }}>
                        <h2 style={{ margin: 0, marginBottom: '8px', color: '#1E3A8A', fontSize: '20px' }}>
                            📊 Gerar Relatório Executivo
                        </h2>
                        <p style={{ color: '#64748B', fontSize: '14px', marginBottom: '24px' }}>
                            Selecione o período para o relatório
                        </p>

                        <div style={{ display: 'flex', gap: '16px', marginBottom: '24px' }}>
                            <div style={{ flex: 1 }}>
                                <label style={{ display: 'block', marginBottom: '6px', fontSize: '13px', fontWeight: 600, color: '#374151' }}>
                                    Data Início
                                </label>
                                <input
                                    type="date"
                                    value={pdfDtInicio}
                                    onChange={e => setPdfDtInicio(e.target.value)}
                                    style={{
                                        width: '100%', padding: '10px 12px', border: '2px solid #E5E7EB',
                                        borderRadius: '8px', fontSize: '14px'
                                    }}
                                />
                            </div>
                            <div style={{ flex: 1 }}>
                                <label style={{ display: 'block', marginBottom: '6px', fontSize: '13px', fontWeight: 600, color: '#374151' }}>
                                    Data Fim
                                </label>
                                <input
                                    type="date"
                                    value={pdfDtFim}
                                    onChange={e => setPdfDtFim(e.target.value)}
                                    style={{
                                        width: '100%', padding: '10px 12px', border: '2px solid #E5E7EB',
                                        borderRadius: '8px', fontSize: '14px'
                                    }}
                                />
                            </div>
                        </div>

                        <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                            <button
                                onClick={() => setShowPdfModal(false)}
                                style={{
                                    padding: '10px 20px', border: '2px solid #E5E7EB', background: 'white',
                                    borderRadius: '8px', cursor: 'pointer', fontWeight: 600, color: '#6B7280'
                                }}
                            >
                                Cancelar
                            </button>
                            <button
                                onClick={gerarPdf}
                                style={{
                                    padding: '10px 24px', border: 'none',
                                    background: 'linear-gradient(135deg, #DC2626 0%, #EF4444 100%)',
                                    color: 'white', borderRadius: '8px', cursor: 'pointer', fontWeight: 600,
                                    boxShadow: '0 4px 12px rgba(220, 38, 38, 0.3)'
                                }}
                            >
                                📄 Gerar PDF
                            </button>
                        </div>
                    </div>
                </div>,
                document.body
            )}

            {/* Header */}
            <div className="page-header" style={{ marginBottom: '24px' }}>
                <div>
                    <h1 className="page-title" style={{
                        background: 'linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        fontSize: '28px'
                    }}>
                        Dashboard Executivo
                    </h1>
                    <p className="page-subtitle" style={{ fontSize: '16px', color: '#64748B' }}>
                        {resumo?.obra || 'Loteamento'}
                    </p>
                </div>
                <div style={{ display: 'flex', gap: '12px' }}>
                    <button
                        onClick={() => setShowPdfModal(true)}
                        className="btn"
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            background: 'linear-gradient(135deg, #DC2626 0%, #EF4444 100%)',
                            color: 'white',
                            border: 'none',
                            padding: '10px 20px',
                            borderRadius: '8px',
                            fontWeight: 600,
                            cursor: 'pointer',
                            boxShadow: '0 4px 12px rgba(220, 38, 38, 0.3)'
                        }}
                    >
                        📄 Gerar PDF
                    </button>
                    <button onClick={loadData} className="btn btn-outline" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        Atualizar
                    </button>
                </div>
            </div>

            {/* Card Principal - Total */}
            <div style={{
                background: 'linear-gradient(135deg, #00528F 0%, #0089D6 50%, #00A5FF 100%)',
                borderRadius: '20px',
                padding: '32px',
                color: 'white',
                marginBottom: '24px',
                boxShadow: '0 20px 60px rgba(0, 82, 143, 0.4)'
            }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '20px' }}>
                    <div>
                        <div style={{ fontSize: '14px', opacity: 0.7, marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '1px' }}>
                            Total do Empreendimento
                        </div>
                        <div style={{ fontSize: '48px', fontWeight: 800 }}>{resumo?.totalUnidades || 0}</div>
                        <div style={{ fontSize: '14px', opacity: 0.7 }}>unidades</div>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: '14px', opacity: 0.7, marginBottom: '8px' }}>Valor Geral de Vendas (VGV)</div>
                        <div style={{ fontSize: '32px', fontWeight: 700, color: '#22D3EE' }}>
                            R$ {formatCurrency(resumo?.totalValor || 0)}
                        </div>
                    </div>
                </div>
            </div>

            {/* Cards de Todos os Status */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
                gap: '16px',
                marginBottom: '28px'
            }}>
                {statusOrdenados.map((item, index) => (
                    <div key={index} style={{
                        background: STATUS_COLORS[item.status]?.gradient || 'linear-gradient(135deg, #6B7280 0%, #9CA3AF 100%)',
                        borderRadius: '16px',
                        padding: '20px',
                        color: 'white',
                        boxShadow: `0 8px 32px ${STATUS_COLORS[item.status]?.bg || '#6B7280'}40`,
                        transition: 'transform 0.2s ease',
                    }}>
                        <div style={{ fontSize: '11px', opacity: 0.9, marginBottom: '6px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                            {item.label}
                        </div>
                        <div style={{ fontSize: '28px', fontWeight: 700 }}>{item.quantidade}</div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '6px', fontSize: '12px', opacity: 0.85 }}>
                            <span>{item.percentual?.toFixed(1)}%</span>
                            <span>R$ {formatCurrency(item.valor)}</span>
                        </div>
                    </div>
                ))}
            </div>

            {/* Graficos */}
            <div style={{ display: 'grid', gridTemplateColumns: '400px 1fr', gap: '24px', marginBottom: '28px' }}>

                {/* Grafico Pizza - Status com Valores */}
                <div className="card" style={{ padding: '24px' }}>
                    <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#1E293B', marginBottom: '20px' }}>
                        Distribuicao por Status
                    </h3>

                    {/* SVG Pie Chart */}
                    <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '20px' }}>
                        <svg width="220" height="220" viewBox="0 0 220 220">
                            {(() => {
                                const data = statusOrdenados.filter(s => s.quantidade > 0);
                                const total = data.reduce((sum, d) => sum + d.quantidade, 0);
                                let currentAngle = 0;

                                return data.map((item, index) => {
                                    const percentage = item.quantidade / total;
                                    const angle = percentage * 360;
                                    const startAngle = currentAngle;
                                    const endAngle = currentAngle + angle;

                                    const x1 = 110 + 85 * Math.cos((startAngle - 90) * Math.PI / 180);
                                    const y1 = 110 + 85 * Math.sin((startAngle - 90) * Math.PI / 180);
                                    const x2 = 110 + 85 * Math.cos((endAngle - 90) * Math.PI / 180);
                                    const y2 = 110 + 85 * Math.sin((endAngle - 90) * Math.PI / 180);

                                    const largeArc = angle > 180 ? 1 : 0;

                                    currentAngle += angle;

                                    const fillColor = STATUS_COLORS[item.status]?.bg || item.color || '#6B7280';
                                    return (
                                        <path
                                            key={index}
                                            d={`M 110 110 L ${x1} ${y1} A 85 85 0 ${largeArc} 1 ${x2} ${y2} Z`}
                                            fill={fillColor}
                                            stroke="white"
                                            strokeWidth="3"
                                            style={{ cursor: 'pointer' }}
                                        />
                                    );
                                });
                            })()}
                            <circle cx="110" cy="110" r="50" fill="white" />
                            <text x="110" y="105" textAnchor="middle" fontSize="28" fontWeight="800" fill="#1E293B">
                                {resumo?.totalUnidades || 0}
                            </text>
                            <text x="110" y="125" textAnchor="middle" fontSize="12" fill="#64748B">
                                unidades
                            </text>
                        </svg>
                    </div>

                    {/* Legenda com Valores - TODOS os status */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', maxHeight: '250px', overflowY: 'auto' }}>
                        {statusOrdenados.map((item, index) => (
                            <div key={index} style={{
                                display: 'grid',
                                gridTemplateColumns: '16px 1fr auto auto',
                                alignItems: 'center',
                                gap: '10px',
                                padding: '8px 10px',
                                background: '#F8FAFC',
                                borderRadius: '8px',
                                borderLeft: `4px solid ${STATUS_COLORS[item.status]?.bg || item.color}`
                            }}>
                                <div style={{
                                    width: '12px',
                                    height: '12px',
                                    borderRadius: '3px',
                                    background: STATUS_COLORS[item.status]?.bg || item.color
                                }} />
                                <span style={{ fontSize: '12px', color: '#374151', fontWeight: 500 }}>{item.label}</span>
                                <span style={{ fontSize: '13px', fontWeight: 700, color: '#1E293B' }}>
                                    {item.quantidade}
                                </span>
                                <span style={{ fontSize: '11px', color: '#059669', fontWeight: 500, textAlign: 'right', minWidth: '80px' }}>
                                    R$ {formatCurrency(item.valor)}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Grafico Barras - Vendas Diarias MELHORADO */}
                <div className="card" style={{ padding: '24px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                        <div>
                            <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#1E293B', marginBottom: '4px' }}>
                                Vendas Diarias
                            </h3>
                            <p style={{ fontSize: '12px', color: '#64748B' }}>Ultimos 30 dias</p>
                        </div>
                        <div style={{ display: 'flex', gap: '12px' }}>
                            <div style={{
                                background: 'linear-gradient(135deg, #059669 0%, #10B981 100%)',
                                color: 'white',
                                padding: '10px 18px',
                                borderRadius: '24px',
                                fontSize: '14px',
                                fontWeight: 700
                            }}>
                                {vendas?.totalVendas || 0} vendas
                            </div>
                            <div style={{
                                background: 'linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%)',
                                color: 'white',
                                padding: '10px 18px',
                                borderRadius: '24px',
                                fontSize: '14px',
                                fontWeight: 700
                            }}>
                                R$ {formatCurrency(vendas?.totalValor || 0)}
                            </div>
                        </div>
                    </div>

                    {/* Improved Bar Chart */}
                    <div style={{
                        position: 'relative',
                        height: '250px',
                        background: '#F8FAFC',
                        borderRadius: '12px',
                        padding: '20px 20px 50px 50px'
                    }}>
                        {/* Grid Lines */}
                        <div style={{ position: 'absolute', left: '50px', right: '20px', top: '20px', bottom: '50px' }}>
                            {[0, 1, 2, 3, 4].map((i) => (
                                <div key={i} style={{
                                    position: 'absolute',
                                    left: 0,
                                    right: 0,
                                    top: `${i * 25}%`,
                                    borderTop: '1px dashed #E2E8F0',
                                    display: 'flex',
                                    alignItems: 'center'
                                }}>
                                    <span style={{
                                        position: 'absolute',
                                        left: '-45px',
                                        fontSize: '10px',
                                        color: '#94A3B8',
                                        width: '40px',
                                        textAlign: 'right'
                                    }}>
                                        {Math.round(maxVendas * (1 - i / 4))}
                                    </span>
                                </div>
                            ))}
                        </div>

                        {/* Bars */}
                        <div style={{
                            display: 'flex',
                            alignItems: 'flex-end',
                            justifyContent: 'space-around',
                            height: 'calc(100% - 30px)',
                            paddingTop: '10px',
                            position: 'relative'
                        }}>
                            {vendas?.vendasDiarias?.slice(0, 10).reverse().map((venda, index) => {
                                const barMaxHeight = 150; // altura maxima das barras em px
                                const heightPx = Math.max(8, (venda.vendas / maxVendas) * barMaxHeight);
                                return (
                                    <div
                                        key={index}
                                        style={{
                                            display: 'flex',
                                            flexDirection: 'column',
                                            alignItems: 'center',
                                            flex: 1,
                                            maxWidth: '60px'
                                        }}
                                    >
                                        {/* Value on top */}
                                        <span style={{
                                            fontSize: '11px',
                                            fontWeight: 600,
                                            color: '#1E3A8A',
                                            marginBottom: '4px'
                                        }}>
                                            {venda.vendas}
                                        </span>

                                        {/* Bar */}
                                        <div
                                            style={{
                                                width: '36px',
                                                height: `${heightPx}px`,
                                                minHeight: '8px',
                                                background: 'linear-gradient(180deg, #3B82F6 0%, #1E40AF 100%)',
                                                borderRadius: '8px 8px 0 0',
                                                transition: 'all 0.3s ease',
                                                cursor: 'pointer',
                                                boxShadow: '0 4px 12px rgba(59, 130, 246, 0.3)'
                                            }}
                                            title={`${venda.data}: ${venda.vendas} vendas\nR$ ${formatCurrency(venda.valorTotal)}`}
                                        />

                                        {/* Date label */}
                                        <span style={{
                                            marginTop: '8px',
                                            fontSize: '11px',
                                            color: '#64748B',
                                            fontWeight: 500
                                        }}>
                                            {venda.data?.split('/').slice(0, 2).join('/')}
                                        </span>
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    {/* Resumo Cards */}
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(3, 1fr)',
                        gap: '16px',
                        marginTop: '20px'
                    }}>
                        <div style={{ background: '#F0FDF4', padding: '16px', borderRadius: '12px', textAlign: 'center' }}>
                            <div style={{ fontSize: '11px', color: '#059669', marginBottom: '4px', fontWeight: 500, textTransform: 'uppercase' }}>Total Vendas</div>
                            <div style={{ fontSize: '24px', fontWeight: 800, color: '#059669' }}>{vendas?.totalVendas || 0}</div>
                        </div>
                        <div style={{ background: '#EFF6FF', padding: '16px', borderRadius: '12px', textAlign: 'center' }}>
                            <div style={{ fontSize: '11px', color: '#1D4ED8', marginBottom: '4px', fontWeight: 500, textTransform: 'uppercase' }}>Valor Total</div>
                            <div style={{ fontSize: '24px', fontWeight: 800, color: '#1D4ED8' }}>
                                R$ {formatCurrency(vendas?.totalValor || 0)}
                            </div>
                        </div>
                        <div style={{ background: '#FEF3C7', padding: '16px', borderRadius: '12px', textAlign: 'center' }}>
                            <div style={{ fontSize: '11px', color: '#D97706', marginBottom: '4px', fontWeight: 500, textTransform: 'uppercase' }}>Valor Medio</div>
                            <div style={{ fontSize: '24px', fontWeight: 800, color: '#D97706' }}>
                                R$ {formatCurrency(vendas?.valorMedio || 0)}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Tabela Vendas Diarias */}
            <div className="table-container">
                <div className="table-header-row">
                    <span className="table-title">Detalhamento Vendas Diarias</span>
                    <span className="badge badge-primary">{vendas?.vendasDiarias?.length || 0} dias</span>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th style={{ textAlign: 'center' }}>Data</th>
                            <th style={{ textAlign: 'center' }}>Vendas</th>
                            <th style={{ textAlign: 'right' }}>Valor Vendas</th>
                            <th style={{ textAlign: 'center' }}>Cancelamentos</th>
                            <th style={{ textAlign: 'right' }}>Valor Cancelado</th>
                            <th style={{ textAlign: 'right' }}>Valor Medio</th>
                        </tr>
                    </thead>
                    <tbody>
                        {vendas?.vendasDiarias?.slice(0, 15).map((venda, index) => (
                            <tr key={index}>
                                <td style={{ textAlign: 'center', fontWeight: 500 }}>{venda.data}</td>
                                <td style={{ textAlign: 'center' }}>
                                    <span style={{
                                        display: 'inline-block',
                                        padding: '4px 14px',
                                        background: 'linear-gradient(135deg, #059669 0%, #10B981 100%)',
                                        color: 'white',
                                        borderRadius: '16px',
                                        fontSize: '13px',
                                        fontWeight: 700
                                    }}>
                                        {venda.vendas}
                                    </span>
                                </td>
                                <td style={{ textAlign: 'right', fontWeight: 600, color: '#059669' }}>
                                    R$ {formatCurrency(venda.valorTotal)}
                                </td>
                                <td style={{ textAlign: 'center' }}>
                                    {venda.cancelamentos > 0 ? (
                                        <span style={{
                                            display: 'inline-block',
                                            padding: '4px 14px',
                                            background: 'linear-gradient(135deg, #DC2626 0%, #EF4444 100%)',
                                            color: 'white',
                                            borderRadius: '16px',
                                            fontSize: '13px',
                                            fontWeight: 700
                                        }}>
                                            {venda.cancelamentos}
                                        </span>
                                    ) : (
                                        <span style={{ color: '#9CA3AF' }}>-</span>
                                    )}
                                </td>
                                <td style={{ textAlign: 'right', color: venda.cancelamentos > 0 ? '#DC2626' : '#9CA3AF' }}>
                                    {venda.cancelamentos > 0 ? `R$ ${formatCurrency(venda.valorCancelamentos || 0)}` : '-'}
                                </td>
                                <td style={{ textAlign: 'right', color: '#64748B' }}>
                                    R$ {formatCurrency(venda.valorMedio)}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};
