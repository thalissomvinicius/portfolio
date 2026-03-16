import type { ApiResponse, Empreendimento } from '../types';

const API_BASE_URL = '/api';

// Lista de empreendimentos disponíveis
export const empreendimentos: Empreendimento[] = [
    { id: 600, nome: 'Residencial Jardim do Valle', cidade: 'Dom Eliseu', estado: 'PA' },
    { id: 601, nome: 'Residencial Jardim América', cidade: 'Capanema', estado: 'PA' },
    { id: 602, nome: 'Residencial Salles Jardim', cidade: 'Castanhal', estado: 'PA' },
    { id: 603, nome: 'Residencial Jardim Castanhal', cidade: 'Castanhal', estado: 'PA' },
    { id: 604, nome: 'Residencial Ipitinga', cidade: 'Tomé-Açu', estado: 'PA' },
    { id: 605, nome: 'Residencial Valle do Ipitinga', cidade: 'Tomé-Açu', estado: 'PA' },
    { id: 610, nome: 'Residencial Jardim do Valle', cidade: 'Tailândia', estado: 'PA' },
    { id: 616, nome: 'Residencial Jardim do Valle', cidade: 'Barcarena', estado: 'PA' },
    { id: 617, nome: 'Residencial Jardim América II', cidade: 'Capanema', estado: 'PA' },
    { id: 618, nome: 'Residencial Jardim do Valle II', cidade: 'Tailândia', estado: 'PA' },
    { id: 620, nome: 'Residencial Jardim Valle do Uraim', cidade: 'Paragominas', estado: 'PA' },
    { id: 621, nome: 'Residencial Parque do Valle', cidade: 'Rondon do Pará', estado: 'PA' },
    { id: 622, nome: 'Residencial Jardim Valle do Uraim II', cidade: 'Rondon do Pará', estado: 'PA' },
    { id: 623, nome: 'Residencial Jardim Castanhal III', cidade: 'Castanhal', estado: 'PA' },
    { id: 624, nome: 'Residencial Valle do Ipitinga II', cidade: 'Tomé-Açu', estado: 'PA' },
    { id: 625, nome: 'Residencial Valle dos Ipês', cidade: 'Tomé-Açu', estado: 'PA' },
    { id: 626, nome: 'Residencial Jardim do Valle II', cidade: 'Dom Eliseu', estado: 'PA' }
];

// Buscar lotes de um empreendimento
export const buscarLotes = async (codEmpreendimento: number): Promise<ApiResponse> => {
    const url = `${API_BASE_URL}/consulta/${codEmpreendimento}/`;

    try {
        console.log('🔍 Buscando lotes da API:', url);

        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            },
            mode: 'cors',
        });

        console.log('📡 Resposta da API:', response.status, response.statusText);

        if (!response.ok) {
            throw new Error(`Erro HTTP ${response.status}: ${response.statusText}`);
        }

        const data: ApiResponse = await response.json();
        console.log('✅ Dados recebidos:', data.count, 'lotes');

        return data;
    } catch (error) {
        console.error('❌ Erro ao buscar lotes:', error);
        console.error('URL tentada:', url);

        if (error instanceof TypeError && error.message.includes('fetch')) {
            throw new Error('Não foi possível conectar à API. Verifique se o servidor está acessível.');
        }

        throw error;
    }
};

// Utilitários para status
export const getStatusKey = (status: string): string => {
    if (status.includes('Disponível')) return 'disponivel';
    if (status.includes('Reservado')) return 'reservado';
    if (status.includes('Vendido')) return 'vendido';
    if (status.includes('Quitado')) return 'quitado';
    if (status.includes('Fora')) return 'fora';
    return 'outro';
};

export const getStatusLabel = (status: string): string => {
    if (status.includes('Disponível')) return 'Disponível';
    if (status.includes('Reservado')) return 'Reservado';
    if (status.includes('Vendido')) return 'Vendido';
    if (status.includes('Quitado')) return 'Quitado';
    if (status.includes('Fora')) return 'Fora de Venda';
    return status;
};

export const getStatusClass = (status: string): string => {
    const key = getStatusKey(status);
    return `status-${key}`;
};
