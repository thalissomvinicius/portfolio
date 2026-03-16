import React, { useState, useEffect, useMemo } from 'react';
import {
    BarChart3,
    TrendingUp,
    Calendar,
    DollarSign,
    Filter,
    ArrowUpRight,
    Share2,
    Check,
    Building,
    Download
} from 'lucide-react';
import {
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer,
    AreaChart,
    Area
} from 'recharts';
import axios from 'axios';

// Types
interface Stats {
    total: number;
    average: number;
    count: number;
    max: number;
}

interface ReceiptRecord {
    Empreendimento: string;
    Venda: string;
    Quadra_Lote: string;
    Tipo: string;
    Parcela: string;
    DtConciliacao: string;
    ValorPago: number;
    Conta: string;
}

interface ChartData {
    date: string;
    value: number;
}

interface Company {
    id: string;
    nome_curto: string;
    cor: string;
    codigo?: number;
    obra?: string;
}

interface DailyTotal {
    date: string;
    total: number;
    count: number;
}

interface PropertySummary {
    name: string;
    total: number;
    count: number;
    percentage: number;
}

const formatDateSafe = (dateStr: string) => {
    if (!dateStr) return '';
    const [year, month, day] = dateStr.split('T')[0].split('-');
    return `${day}/${month}/${year}`;
};

const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL',
    }).format(value);
};

const Dashboard = () => {
    const [companies, setCompanies] = useState<Company[]>([]);
    const [selectedCompany, setSelectedCompany] = useState<string>('ML');
    const [startDate, setStartDate] = useState<string>(
        new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split('T')[0]
    );
    const [endDate, setEndDate] = useState<string>(new Date().toISOString().split('T')[0]);
    const [data, setData] = useState<{ chart_data: ChartData[], stats: Stats, records: ReceiptRecord[] } | null>(null);
    const [loading, setLoading] = useState(false);
    const [copySuccess, setCopySuccess] = useState(false);
    const [filterMode, setFilterMode] = useState<'custom' | 'month'>('custom');
    const [selectedYear, setSelectedYear] = useState<number>(2026);
    const [selectedMonthIdx, setSelectedMonthIdx] = useState<number>(new Date().getMonth());

    const months = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ];

    const years = [2024, 2025, 2026];

    useEffect(() => {
        fetchCompanies();
    }, []);

    useEffect(() => {
        if (selectedCompany) {
            fetchData();
        }
    }, [selectedCompany, startDate, endDate]);

    const fetchCompanies = async () => {
        try {
            const response = await axios.get('/api/companies');
            setCompanies([
                { id: 'CONSOLIDADO', nome_curto: '📊 CONSOLIDADO (TODAS)', cor: '#64748b' },
                ...response.data
            ]);
        } catch (error) {
            console.error("Error fetching companies:", error);
        }
    };

    const fetchData = async () => {
        setLoading(true);
        try {
            const response = await axios.get('/api/receipts', {
                params: {
                    start_date: startDate,
                    end_date: endDate,
                    company_id: selectedCompany
                }
            });
            setData(response.data);
        } catch (error) {
            console.error("Error fetching data:", error);
        } finally {
            setLoading(false);
        }
    };

    const updateMonthRange = (month: number, year: number) => {
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);

        const fY = firstDay.getFullYear();
        const fM = String(firstDay.getMonth() + 1).padStart(2, '0');
        const fD = String(firstDay.getDate()).padStart(2, '0');

        const lY = lastDay.getFullYear();
        const lM = String(lastDay.getMonth() + 1).padStart(2, '0');
        const lD = String(lastDay.getDate()).padStart(2, '0');

        setStartDate(`${fY}-${fM}-${fD}`);
        setEndDate(`${lY}-${lM}-${lD}`);
    };

    // Derived State: Group by Day
    const dailySummary = useMemo(() => {
        if (!data) return [];
        const groups: { [key: string]: { total: number, count: number } } = {};

        data.records.forEach(record => {
            const date = record.DtConciliacao.split('T')[0];
            if (!groups[date]) {
                groups[date] = { total: 0, count: 0 };
            }
            groups[date].total += record.ValorPago;
            groups[date].count += 1;
        });

        return Object.entries(groups)
            .map(([date, stats]): DailyTotal => ({
                date,
                total: stats.total,
                count: stats.count
            }))
            .sort((a, b) => a.date.localeCompare(b.date));
    }, [data]);

    // Derived State: Group by Property
    const propertySummary = useMemo((): PropertySummary[] => {
        if (!data) return [];
        const groups: { [key: string]: { total: number, count: number } } = {};

        data.records.forEach(record => {
            const name = record.Empreendimento;
            if (!groups[name]) {
                groups[name] = { total: 0, count: 0 };
            }
            groups[name].total += record.ValorPago;
            groups[name].count += 1;
        });

        const totalValue = data.stats.total;

        return Object.entries(groups)
            .map(([name, stats]) => ({
                name,
                total: stats.total,
                count: stats.count,
                percentage: totalValue > 0 ? (stats.total / totalValue) * 100 : 0
            }))
            .sort((a, b) => b.total - a.total);
    }, [data]);

    const handleCopyMessage = () => {
        if (!data || !dailySummary.length) return;

        const company = companies.find(c => c.id === selectedCompany);
        const companyLabel = `${company?.nome_curto || selectedCompany} (${company?.codigo || '---'} - ${company?.obra || '---'})`;

        let message = `📊 *RELATÓRIO DE RECEBIMENTOS DIÁRIOS*\n`;
        message += `*${companyLabel}*\n`;
        message += `Período: ${formatDateSafe(startDate)} a ${formatDateSafe(endDate)}\n\n`;
        message += `==================================================\n\n`;
        message += `📅 *RECEBIMENTOS POR DIA:*\n`;

        dailySummary.forEach(day => {
            const dateFmt = formatDateSafe(day.date);
            const valueFmt = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(day.total);
            // Manual padding simulation for WhatsApp alignment
            message += `${dateFmt}  |  ${valueFmt.padStart(15, ' ')}\n`;
        });

        message += `\n==================================================\n`;
        message += `💰 *RESUMO DO PERÍODO:*\n`;
        message += `* Total Recebido:   ${formatCurrency(data.stats.total)}\n`;
        message += `* Média Diária:      ${formatCurrency(data.stats.average)}\n`;
        message += `* Dias c/ Recebimento:          ${dailySummary.length}\n\n`;
        message += `==================================================\n`;

        navigator.clipboard.writeText(message);
        setCopySuccess(true);
        setTimeout(() => setCopySuccess(false), 2000);
    };

    return (
        <div className="min-h-screen p-4 md:p-8 bg-slate-50">
            {/* Header */}
            <header className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4 px-2">
                <div>
                    <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
                        Analytics de Recebimentos
                    </h1>
                    <p className="text-slate-500 mt-1 font-medium">Gestão Financeira Modernizada • Valle/ML</p>
                </div>

                <div className="flex gap-3">
                    <button
                        onClick={handleCopyMessage}
                        className={`flex items-center gap-2 px-5 py-2.5 rounded-xl transition-all font-semibold shadow-sm border ${copySuccess
                            ? 'bg-emerald-50 border-emerald-200 text-emerald-600'
                            : 'bg-white border-slate-200 text-slate-700 hover:bg-slate-50'
                            }`}
                    >
                        {copySuccess ? <Check size={18} /> : <Share2 size={18} className="text-blue-500" />}
                        {copySuccess ? 'Copiado!' : 'Relatório p/ WhatsApp'}
                    </button>
                    <button className="flex items-center gap-2 px-5 py-2.5 bg-slate-900 text-white rounded-xl hover:bg-slate-800 transition-all font-semibold shadow-lg shadow-slate-200">
                        <Download size={18} />
                        Excel
                    </button>
                </div>
            </header>

            {/* Main Layout */}
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">

                {/* Sidebar Filters */}
                <div className="lg:col-span-1 space-y-6">
                    <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
                        <div className="flex items-center gap-2 mb-6 text-slate-900 font-bold">
                            <Filter size={20} className="text-blue-500" />
                            Parâmetros
                        </div>

                        {/* Filter Tabs */}
                        <div className="flex p-1 bg-slate-100 rounded-xl mb-6">
                            <button
                                onClick={() => setFilterMode('custom')}
                                className={`flex-1 py-1.5 text-xs font-black rounded-lg transition-all ${filterMode === 'custom' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-400 hover:text-slate-600'}`}
                            >
                                PERÍODO
                            </button>
                            <button
                                onClick={() => setFilterMode('month')}
                                className={`flex-1 py-1.5 text-xs font-black rounded-lg transition-all ${filterMode === 'month' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-400 hover:text-slate-600'}`}
                            >
                                MÊS
                            </button>
                        </div>

                        <div className="space-y-4">
                            <div>
                                <label id="company-label" className="block text-[10px] uppercase tracking-widest text-slate-400 mb-1 font-black">Empresa</label>
                                <select
                                    id="company-select"
                                    value={selectedCompany}
                                    onChange={(e) => setSelectedCompany(e.target.value)}
                                    title="Selecionar Empresa"
                                    className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all font-medium text-slate-700"
                                >
                                    {companies.map(company => (
                                        <option key={company.id} value={company.id}>{company.nome_curto}</option>
                                    ))}
                                </select>
                            </div>

                            {filterMode === 'custom' ? (
                                <div className="grid grid-cols-1 gap-4 animate-in fade-in duration-300">
                                    <div>
                                        <label className="block text-[10px] uppercase tracking-widest text-slate-400 mb-1 font-black">Início</label>
                                        <input
                                            type="date"
                                            title="Data de Início"
                                            value={startDate}
                                            onChange={(e) => setStartDate(e.target.value)}
                                            className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all font-medium text-slate-700"
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-[10px] uppercase tracking-widest text-slate-400 mb-1 font-black">Fim</label>
                                        <input
                                            type="date"
                                            title="Data de Fim"
                                            value={endDate}
                                            onChange={(e) => setEndDate(e.target.value)}
                                            className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all font-medium text-slate-700"
                                        />
                                    </div>
                                </div>
                            ) : (
                                <div className="space-y-4 animate-in slide-in-from-top-2 duration-300">
                                    <div className="grid grid-cols-2 gap-3">
                                        <div>
                                            <label className="block text-[10px] uppercase tracking-widest text-slate-400 mb-1 font-black">Ano</label>
                                            <select
                                                title="Selecionar Ano"
                                                value={selectedYear}
                                                onChange={(e) => {
                                                    const year = Number(e.target.value);
                                                    setSelectedYear(year);
                                                    updateMonthRange(selectedMonthIdx, year);
                                                }}
                                                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all font-medium text-slate-700"
                                            >
                                                {years.map(year => (
                                                    <option key={year} value={year}>{year}</option>
                                                ))}
                                            </select>
                                        </div>
                                        <div>
                                            <label className="block text-[10px] uppercase tracking-widest text-slate-400 mb-1 font-black">Mês</label>
                                            <select
                                                title="Selecionar Mês"
                                                value={selectedMonthIdx}
                                                onChange={(e) => {
                                                    const month = Number(e.target.value);
                                                    setSelectedMonthIdx(month);
                                                    updateMonthRange(month, selectedYear);
                                                }}
                                                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all font-medium text-slate-700"
                                            >
                                                {months.map((month, idx) => (
                                                    <option key={idx} value={idx}>{month}</option>
                                                ))}
                                            </select>
                                        </div>
                                    </div>
                                    <p className="text-[10px] text-slate-400 italic font-medium">
                                        Filtra do dia 1 ao último dia do mês escolhido.
                                    </p>
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="bg-emerald-50 rounded-2xl p-6 border border-emerald-100 shadow-sm">
                        <div className="flex items-center gap-2 mb-2 text-emerald-700 font-bold uppercase text-[10px] tracking-widest">
                            <TrendingUp size={16} />
                            Foco em Resultados
                        </div>
                        <p className="text-xs text-emerald-800/80 leading-relaxed font-medium">
                            Os dados são atualizados em tempo real conforme a conciliação bancária do ERP.
                        </p>
                    </div>
                </div>

                {/* Dashboard Content */}
                <div className="lg:col-span-3 space-y-8">

                    {/* KPI Row */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="bg-white rounded-3xl p-7 shadow-sm border border-slate-100 relative overflow-hidden">
                            <div className="flex justify-between items-start mb-4">
                                <div className="p-3 bg-blue-50 text-blue-600 rounded-2xl">
                                    <DollarSign size={24} />
                                </div>
                                <div className="flex items-center gap-1 text-emerald-600 text-xs font-black bg-emerald-50 px-2 py-1 rounded-lg">
                                    <ArrowUpRight size={14} />
                                    <span>+ Ativo</span>
                                </div>
                            </div>
                            <p className="text-slate-500 text-[10px] uppercase tracking-widest font-black">Volume Total</p>
                            <h3 className="text-3xl font-black mt-2 text-slate-900">
                                {data ? formatCurrency(data.stats.total) : 'R$ 0,00'}
                            </h3>
                        </div>

                        <div className="bg-white rounded-3xl p-7 shadow-sm border border-slate-100">
                            <div className="p-3 bg-indigo-50 text-indigo-600 rounded-2xl w-fit mb-4">
                                <BarChart3 size={24} />
                            </div>
                            <p className="text-slate-500 text-[10px] uppercase tracking-widest font-black">Média Diária</p>
                            <h3 className="text-3xl font-black mt-2 text-slate-900">
                                {data ? formatCurrency(data.stats.average) : 'R$ 0,00'}
                            </h3>
                        </div>

                        <div className="bg-white rounded-3xl p-7 shadow-sm border border-slate-100">
                            <div className="p-3 bg-amber-50 text-amber-600 rounded-2xl w-fit mb-4">
                                <Calendar size={24} />
                            </div>
                            <p className="text-slate-500 text-[10px] uppercase tracking-widest font-black">Duras c/ Receita</p>
                            <h3 className="text-3xl font-black mt-2 text-slate-900">
                                {dailySummary.length}
                            </h3>
                        </div>
                    </div>

                    {/* Chart Area */}
                    <div className="bg-white rounded-3xl p-7 shadow-sm border border-slate-100">
                        <h3 className="text-lg font-black text-slate-900 flex items-center gap-2 mb-10">
                            <TrendingUp size={20} className="text-emerald-500" />
                            Curva de Performance
                        </h3>

                        <div className="h-[280px] w-full">
                            {loading ? (
                                <div className="h-full w-full flex items-center justify-center">
                                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-slate-900"></div>
                                </div>
                            ) : data && data.chart_data.length > 0 ? (
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={data.chart_data}>
                                        <defs>
                                            <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.1} />
                                                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                                        <XAxis
                                            dataKey="date"
                                            stroke="#94a3b8"
                                            fontSize={10}
                                            axisLine={false}
                                            tickLine={false}
                                            tickFormatter={(val: string) => formatDateSafe(val).slice(0, 5)}
                                        />
                                        <YAxis
                                            stroke="#94a3b8"
                                            fontSize={10}
                                            axisLine={false}
                                            tickLine={false}
                                            tickFormatter={(val: number) => `R$ ${val / 1000}k`}
                                        />
                                        <Tooltip
                                            labelFormatter={(label: string) => formatDateSafe(label)}
                                            formatter={(value: number) => [formatCurrency(value), 'Valor']}
                                        />
                                        <Area type="monotone" dataKey="value" stroke="#3b82f6" strokeWidth={3} fillOpacity={1} fill="url(#colorValue)" />
                                    </AreaChart>
                                </ResponsiveContainer>
                            ) : (
                                <div className="h-full w-full flex items-center justify-center text-slate-400 text-sm italic">
                                    Selecione um período para visualizar a curva.
                                </div>
                            )}
                        </div>
                    </div>

                    <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
                        {/* Daily Summary Table */}
                        <div className="bg-white rounded-3xl p-7 shadow-sm border border-slate-100">
                            <h3 className="text-lg font-black text-slate-900 mb-6 flex items-center gap-2">
                                <Calendar size={20} className="text-blue-500" />
                                Resumo por Dia
                            </h3>
                            <div className="space-y-2 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                                <div className="grid grid-cols-3 px-4 py-2 text-[10px] font-black text-slate-400 uppercase tracking-widest border-b border-slate-50">
                                    <span>Data</span>
                                    <span className="text-center">Tickets</span>
                                    <span className="text-right">Total</span>
                                </div>
                                {dailySummary.length > 0 ? dailySummary.slice().reverse().map((day, i) => (
                                    <div key={i} className="grid grid-cols-3 items-center px-4 py-3 hover:bg-slate-50 rounded-xl transition-colors border-b border-slate-50 last:border-0">
                                        <div className="font-bold text-slate-700 text-sm">
                                            {formatDateSafe(day.date)}
                                        </div>
                                        <div className="text-center font-medium text-slate-400 text-xs text-mono">
                                            {day.count}
                                        </div>
                                        <div className="text-sm font-black text-slate-900 text-right">
                                            {new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 2 }).format(day.total)}
                                        </div>
                                    </div>
                                )) : (
                                    <div className="text-center py-12 text-slate-400 text-sm italic">
                                        Nenhum dado no período.
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Property Summary Section */}
                        <div className="bg-white rounded-3xl p-7 shadow-sm border border-slate-100">
                            <h3 className="text-lg font-black text-slate-900 mb-6 flex items-center gap-2">
                                <Building size={20} className="text-emerald-500" />
                                Visão por Empreendimento
                            </h3>
                            <div className="space-y-6 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                                {propertySummary.length > 0 ? propertySummary.map((prop, i) => (
                                    <div key={i} className="group">
                                        <div className="flex justify-between items-end mb-2">
                                            <div className="max-w-[70%]">
                                                <div className="text-xs font-black text-slate-800 uppercase truncate" title={prop.name}>{prop.name}</div>
                                                <div className="text-[10px] font-bold text-slate-400">{prop.count} recebimentos</div>
                                            </div>
                                            <div className="text-right">
                                                <div className="text-sm font-black text-slate-900">{formatCurrency(prop.total)}</div>
                                            </div>
                                        </div>
                                        <div className="h-1.5 w-full bg-slate-50 rounded-full overflow-hidden border border-slate-100">
                                            <svg width="100%" height="100%" aria-label={`Progresso: ${prop.percentage.toFixed(1)}%`}>
                                                <title>Progresso: {prop.percentage.toFixed(1)}%</title>
                                                <rect
                                                    width={`${prop.percentage}%`}
                                                    height="100%"
                                                    className="fill-emerald-500 transition-all duration-1000 group-hover:fill-blue-500"
                                                />
                                            </svg>
                                        </div>
                                    </div>
                                )) : (
                                    <div className="text-center py-12 text-slate-400 text-sm italic">
                                        Carregue os dados para ver a performance.
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <footer className="mt-16 text-center border-t border-slate-200 pt-8 pb-12">
                <p className="text-slate-500 text-xs font-black uppercase tracking-widest mb-2">Desenvolvido por Vinicius Dev</p>
                <p className="text-slate-400 text-[10px] font-black uppercase tracking-[0.2em]">Valle & ML Analytics Portal • v2.4.0 Final</p>
                <div className="mt-4 flex justify-center items-center gap-6">
                    <div className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
                    <span className="text-xs font-bold text-slate-500">Conexão Segura Ativa</span>
                </div>
            </footer>
        </div>
    );
};

export default Dashboard;
