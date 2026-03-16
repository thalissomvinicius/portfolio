// API Client for VallePrime Dashboard

import type {
    ResumoResponse,
    SinaisResponse,
    BoletosResponse,
    SinalPago,
    Venda,
} from '../types';

const API_BASE = '/api';

async function fetchApi<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${API_BASE}${endpoint}`);
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erro na API');
    }
    return response.json();
}

export const api = {
    // Vendas
    getVendas: (empresa: number, obra: string) =>
        fetchApi<{ data: Venda[]; total: number }>(`/vendas?empresa=${empresa}&obra=${obra}`),

    // Resumo
    getResumo: (empresa: number, obra: string) =>
        fetchApi<ResumoResponse>(`/resumo?empresa=${empresa}&obra=${obra}`),

    // Sinais
    getSinais: (empresa: number, obra: string, dataVencimento: string) =>
        fetchApi<SinaisResponse>(
            `/sinais?empresa=${empresa}&obra=${obra}&data_vencimento=${dataVencimento}`
        ),

    getSinaisAbertos: (empresa: number, obra: string) =>
        fetchApi<{ data: { venda: number; qtdSinaisAberto: number }[]; total: number }>(
            `/sinais/abertos?empresa=${empresa}&obra=${obra}`
        ),

    getSinaisPagos: (venda: number, empresa: number, obra: string) =>
        fetchApi<{ data: SinalPago[]; total: number }>(
            `/sinais/pagos/${venda}?empresa=${empresa}&obra=${obra}`
        ),

    // Boletos
    getBoletos: (empresa: number, venda?: number) => {
        let url = `/boletos?empresa=${empresa}`;
        if (venda) url += `&venda=${venda}`;
        return fetchApi<BoletosResponse>(url);
    },

    // Relatório PDF
    downloadPdf: async (empresa: number, obra: string) => {
        const response = await fetch(
            `${API_BASE}/relatorio/pdf?empresa=${empresa}&obra=${obra}`
        );
        if (!response.ok) {
            throw new Error('Erro ao gerar PDF');
        }
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `relatorio_vendas_${new Date().toISOString().slice(0, 10)}.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
    },

    // Mensagens Diárias
    getResumoDiario: (empresa: number, obra: string) =>
        fetchApi<{
            nomeObra: string;
            data: string;
            vendas: {
                qtdDia: number;
                valorDia: number;
                qtdMes: number;
                valorMes: number;
                qtdTotal: number;
                valorTotal: number;
                valorTotalProdutos?: number;
            };
            distratos: {
                qtdDia: number;
                qtdMes: number;
            };
            estoque: {
                disponivel: number;
                reservado: number;
                suspenso: number;
                foraVenda: number;
                vendido: number;
                quitado: number;
                total: number;
            };
        }>(`/mensagens/resumo-diario?empresa=${empresa}&obra=${obra}`),

    // Inadimplentes
    getInadimplentes: (empresa: number, obra: string, diasMinimo: number = 1, estrutura?: string | number) => {
        let url = `/inadimplentes?empresa=${empresa}&obra=${obra}&dias_minimo=${diasMinimo}`;
        if (estrutura) {
            url += `&estrutura=${estrutura}`;
        }
        return fetchApi<{
            data: Array<{
                venda: number;
                cliente: string;
                corretor: string;
                identificador: string;
                quadra: string;
                lote: string;
                tipoParcela: string;
                parcelaNumero: string;
                dataVencimento: string;
                diasAtraso: number;
                valor: number;
                email: string;
                telefone: string;
                dataProrrogacao: string | null;
                foiProrrogado: number;
                prorrogacaoVencida: number;
            }>;
            total: number;
            metrics: {
                totalBoletos: number;
                valorTotal: number;
                ate30Dias: number;
                de31a60Dias: number;
                de61a90Dias: number;
                mais90Dias: number;
            };
        }>(url);
    },
};
