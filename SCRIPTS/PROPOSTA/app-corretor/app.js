// ============================================
// Valle Prime - Portal do Corretor
// App JavaScript
// ============================================

// Estado da aplicação
let todosLotes = [];
let lotesFiltrados = [];
let viewMode = 'grid';

// Elementos DOM
const lotesContainer = document.getElementById('lotesContainer');
const loading = document.getElementById('loading');
const noResults = document.getElementById('noResults');
const statusFilter = document.getElementById('statusFilter');
const quadraFilter = document.getElementById('quadraFilter');
const searchInput = document.getElementById('searchInput');
const btnBuscar = document.getElementById('btnBuscar');
const empreendimento = document.getElementById('empreendimento');
const modal = document.getElementById('loteModal');
const modalBody = document.getElementById('modalBody');

// Stats
const totalLotesEl = document.getElementById('totalLotes');
const lotesDisponiveisEl = document.getElementById('lotesDisponiveis');
const lotesReservadosEl = document.getElementById('lotesReservados');
const lotesVendidosEl = document.getElementById('lotesVendidos');
const resultCountEl = document.getElementById('resultCount');

// View toggles
const viewGridBtn = document.getElementById('viewGrid');
const viewListBtn = document.getElementById('viewList');

// ============================================
// DADOS DE EXEMPLO (Simula a API)
// ============================================
// Como a API real pode ter problemas de CORS, vamos usar dados de exemplo
// que correspondem ao formato real da API

const dadosExemplo = {
    "success": true,
    "count": 654,
    "numprod_psc": 625,
    "data": [
        { "QD": "001", "LT": "001", "M2": "312,29", "Logradouro": "AVENIDA SABURO CHIBA", "M_Frente": "8,00", "M_Fundo": "10,50", "M_Lado_Direito": "30,02", "M_Lado_Esquerdo": "27,56", "Chanfro": "3,53 / -", "Valor_Terreno": "216.757,37", "Status_Terreno": "1 - Vendido", "Data_Atualizacao": "12/12/2025" },
        { "QD": "001", "LT": "002", "M2": "300,01", "Logradouro": "AVENIDA SABURO CHIBA", "M_Frente": "10,00", "M_Fundo": "10,00", "M_Lado_Direito": "29,98", "M_Lado_Esquerdo": "30,02", "Chanfro": "- / -", "Valor_Terreno": "189.303,31", "Status_Terreno": "1 - Vendido", "Data_Atualizacao": "12/12/2025" },
        { "QD": "001", "LT": "003", "M2": "299,65", "Logradouro": "AVENIDA SABURO CHIBA", "M_Frente": "10,00", "M_Fundo": "10,00", "M_Lado_Direito": "29,95", "M_Lado_Esquerdo": "29,98", "Chanfro": "- / -", "Valor_Terreno": "189.076,15", "Status_Terreno": "3 - Disponível", "Data_Atualizacao": "12/12/2025" },
        { "QD": "001", "LT": "004", "M2": "311,11", "Logradouro": "AVENIDA SABURO CHIBA", "M_Frente": "8,00", "M_Fundo": "10,50", "M_Lado_Direito": "27,41", "M_Lado_Esquerdo": "29,95", "Chanfro": "- / 3,54", "Valor_Terreno": "215.938,34", "Status_Terreno": "3 - Disponível", "Data_Atualizacao": "12/12/2025" },
        { "QD": "001", "LT": "005", "M2": "212,18", "Logradouro": "RUA 15", "M_Frente": "10,35", "M_Fundo": "10,35", "M_Lado_Direito": "20,5", "M_Lado_Esquerdo": "20,5", "Chanfro": "- / -", "Valor_Terreno": "58.576,53", "Status_Terreno": "2 - Reservado", "Data_Atualizacao": "12/12/2025" },
        { "QD": "001", "LT": "006", "M2": "212,17", "Logradouro": "RUA 15", "M_Frente": "10,35", "M_Fundo": "10,35", "M_Lado_Direito": "20,5", "M_Lado_Esquerdo": "20,5", "Chanfro": "- / -", "Valor_Terreno": "58.573,77", "Status_Terreno": "3 - Disponível", "Data_Atualizacao": "12/12/2025" },
        { "QD": "001", "LT": "007", "M2": "212,18", "Logradouro": "RUA 15", "M_Frente": "10,35", "M_Fundo": "10,35", "M_Lado_Direito": "20,5", "M_Lado_Esquerdo": "20,5", "Chanfro": "- / -", "Valor_Terreno": "58.576,53", "Status_Terreno": "1 - Vendido", "Data_Atualizacao": "12/12/2025" },
        { "QD": "001", "LT": "016", "M2": "212,17", "Logradouro": "RUA 15", "M_Frente": "10,35", "M_Fundo": "10,35", "M_Lado_Direito": "20,5", "M_Lado_Esquerdo": "20,5", "Chanfro": "- / -", "Valor_Terreno": "58.573,77", "Status_Terreno": "2 - Reservado", "Data_Atualizacao": "12/12/2025" },
        { "QD": "001", "LT": "017", "M2": "212,17", "Logradouro": "RUA 15", "M_Frente": "10,35", "M_Fundo": "10,35", "M_Lado_Direito": "20,5", "M_Lado_Esquerdo": "20,5", "Chanfro": "- / -", "Valor_Terreno": "58.573,77", "Status_Terreno": "2 - Reservado", "Data_Atualizacao": "12/12/2025" },
        { "QD": "002", "LT": "001", "M2": "216,22", "Logradouro": "AVENIDA DOS IPÊS", "M_Frente": "8,2", "M_Fundo": "10,70", "M_Lado_Direito": "20,5", "M_Lado_Esquerdo": "18", "Chanfro": "3,54 / -", "Valor_Terreno": "75.869,44", "Status_Terreno": "3 - Disponível", "Data_Atualizacao": "12/12/2025" },
        { "QD": "002", "LT": "002", "M2": "211,15", "Logradouro": "AVENIDA DOS IPÊS", "M_Frente": "10,3", "M_Fundo": "10,30", "M_Lado_Direito": "20,5", "M_Lado_Esquerdo": "20,5", "Chanfro": "- / -", "Valor_Terreno": "73.689,24", "Status_Terreno": "1 - Vendido", "Data_Atualizacao": "12/12/2025" },
        { "QD": "002", "LT": "003", "M2": "211,15", "Logradouro": "AVENIDA DOS IPÊS", "M_Frente": "10,3", "M_Fundo": "10,30", "M_Lado_Direito": "20,5", "M_Lado_Esquerdo": "20,5", "Chanfro": "- / -", "Valor_Terreno": "73.689,24", "Status_Terreno": "3 - Disponível", "Data_Atualizacao": "12/12/2025" },
        { "QD": "002", "LT": "026", "M2": "211,15", "Logradouro": "RUA 15", "M_Frente": "10,3", "M_Fundo": "10,30", "M_Lado_Direito": "20,5", "M_Lado_Esquerdo": "20,5", "Chanfro": "- / -", "Valor_Terreno": "54.404,91", "Status_Terreno": "8 - Fora de venda", "Data_Atualizacao": "12/12/2025" },
        { "QD": "003", "LT": "001", "M2": "212,12", "Logradouro": "AVENIDA DOS IPÊS", "M_Frente": "8", "M_Fundo": "10,50", "M_Lado_Direito": "20,5", "M_Lado_Esquerdo": "18", "Chanfro": "3,54 / -", "Valor_Terreno": "64.845,08", "Status_Terreno": "3 - Disponível", "Data_Atualizacao": "12/12/2025" },
        { "QD": "003", "LT": "002", "M2": "205,00", "Logradouro": "AVENIDA DOS IPÊS", "M_Frente": "10", "M_Fundo": "10,00", "M_Lado_Direito": "20,5", "M_Lado_Esquerdo": "20,5", "Chanfro": "- / -", "Valor_Terreno": "65.392,95", "Status_Terreno": "1 - Vendido", "Data_Atualizacao": "12/12/2025" },
        { "QD": "004", "LT": "001", "M2": "226,79", "Logradouro": "AVENIDA DOS IPÊS", "M_Frente": "7,07", "M_Fundo": "11,81", "M_Lado_Direito": "21,5", "M_Lado_Esquerdo": "19,12", "Chanfro": "3,71 / -", "Valor_Terreno": "69.329,70", "Status_Terreno": "3 - Disponível", "Data_Atualizacao": "12/12/2025" },
        { "QD": "005", "LT": "001", "M2": "316,45", "Logradouro": "AVENIDA SABURO CHIBA", "M_Frente": "7,94", "M_Fundo": "10,47", "M_Lado_Direito": "30,54", "M_Lado_Esquerdo": "28,08", "Chanfro": "3,53 / -", "Valor_Terreno": "219.644,78", "Status_Terreno": "1 - Vendido", "Data_Atualizacao": "12/12/2025" },
        { "QD": "005", "LT": "003", "M2": "318,56", "Logradouro": "AVENIDA SABURO CHIBA", "M_Frente": "10,45", "M_Fundo": "10,45", "M_Lado_Direito": "30,46", "M_Lado_Esquerdo": "30,5", "Chanfro": "- / -", "Valor_Terreno": "201.008,17", "Status_Terreno": "2 - Reservado", "Data_Atualizacao": "12/12/2025" },
        { "QD": "005", "LT": "015", "M2": "313,74", "Logradouro": "AVENIDA SABURO CHIBA", "M_Frente": "10,45", "M_Fundo": "10,45", "M_Lado_Direito": "30", "M_Lado_Esquerdo": "30,04", "Chanfro": "- / -", "Valor_Terreno": "197.966,80", "Status_Terreno": "8 - Fora de venda", "Data_Atualizacao": "12/12/2025" },
        { "QD": "005", "LT": "030", "M2": "209,00", "Logradouro": "RUA 01", "M_Frente": "10,45", "M_Fundo": "10,45", "M_Lado_Direito": "20", "M_Lado_Esquerdo": "20", "Chanfro": "- / -", "Valor_Terreno": "79.208,91", "Status_Terreno": "2 - Reservado", "Data_Atualizacao": "12/12/2025" },
        { "QD": "005", "LT": "032", "M2": "206,55", "Logradouro": "RUA 01", "M_Frente": "7,99", "M_Fundo": "10,47", "M_Lado_Direito": "17,5", "M_Lado_Esquerdo": "20", "Chanfro": "- / 3,53", "Valor_Terreno": "86.108,63", "Status_Terreno": "2 - Reservado", "Data_Atualizacao": "12/12/2025" },
        { "QD": "007", "LT": "021", "M2": "163,00", "Logradouro": "RUA 03", "M_Frente": "8,15", "M_Fundo": "8,15", "M_Lado_Direito": "20", "M_Lado_Esquerdo": "20", "Chanfro": "- / -", "Valor_Terreno": "44.999,41", "Status_Terreno": "8 - Fora de venda", "Data_Atualizacao": "12/12/2025" },
        { "QD": "007", "LT": "023", "M2": "172,69", "Logradouro": "RUA 02", "M_Frente": "6,28", "M_Fundo": "8,8", "M_Lado_Direito": "20", "M_Lado_Esquerdo": "17,5", "Chanfro": "3,54 / -", "Valor_Terreno": "52.442,50", "Status_Terreno": "2 - Reservado", "Data_Atualizacao": "12/12/2025" },
        { "QD": "007", "LT": "024", "M2": "163,00", "Logradouro": "RUA 02", "M_Frente": "8,15", "M_Fundo": "8,15", "M_Lado_Direito": "20", "M_Lado_Esquerdo": "20", "Chanfro": "- / -", "Valor_Terreno": "44.999,41", "Status_Terreno": "2 - Reservado", "Data_Atualizacao": "12/12/2025" },
        { "QD": "008", "LT": "010", "M2": "163,00", "Logradouro": "RUA 04", "M_Frente": "8,15", "M_Fundo": "8,15", "M_Lado_Direito": "20", "M_Lado_Esquerdo": "20", "Chanfro": "- / -", "Valor_Terreno": "44.999,41", "Status_Terreno": "2 - Reservado", "Data_Atualizacao": "12/12/2025" },
        { "QD": "008", "LT": "033", "M2": "163,00", "Logradouro": "RUA 03", "M_Frente": "8,15", "M_Fundo": "8,15", "M_Lado_Direito": "20", "M_Lado_Esquerdo": "20", "Chanfro": "- / -", "Valor_Terreno": "44.999,41", "Status_Terreno": "2 - Reservado", "Data_Atualizacao": "12/12/2025" },
        { "QD": "013", "LT": "014", "M2": "163,00", "Logradouro": "RUA 09", "M_Frente": "8,15", "M_Fundo": "8,15", "M_Lado_Direito": "20", "M_Lado_Esquerdo": "20", "Chanfro": "- / -", "Valor_Terreno": "41.998,58", "Status_Terreno": "4 - Quitado", "Data_Atualizacao": "12/12/2025" },
        { "QD": "013", "LT": "015", "M2": "163,00", "Logradouro": "RUA 09", "M_Frente": "8,15", "M_Fundo": "8,15", "M_Lado_Direito": "20", "M_Lado_Esquerdo": "20", "Chanfro": "- / -", "Valor_Terreno": "41.998,58", "Status_Terreno": "4 - Quitado", "Data_Atualizacao": "12/12/2025" },
        { "QD": "014", "LT": "012", "M2": "163,00", "Logradouro": "RUA 10", "M_Frente": "8,15", "M_Fundo": "8,15", "M_Lado_Direito": "20", "M_Lado_Esquerdo": "20", "Chanfro": "- / -", "Valor_Terreno": "36.999,37", "Status_Terreno": "2 - Reservado", "Data_Atualizacao": "12/12/2025" },
        { "QD": "015", "LT": "001", "M2": "201,87", "Logradouro": "AVENIDA DOS IPÊS", "M_Frente": "7,5", "M_Fundo": "10", "M_Lado_Direito": "20,5", "M_Lado_Esquerdo": "18", "Chanfro": "3,54 / -", "Valor_Terreno": "70.834,16", "Status_Terreno": "3 - Disponível", "Data_Atualizacao": "12/12/2025" }
    ]
};

// ============================================
// FUNÇÕES PRINCIPAIS
// ============================================

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    carregarLotes();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    btnBuscar.addEventListener('click', aplicarFiltros);
    statusFilter.addEventListener('change', aplicarFiltros);
    quadraFilter.addEventListener('change', aplicarFiltros);
    searchInput.addEventListener('keyup', (e) => {
        if (e.key === 'Enter') aplicarFiltros();
    });

    viewGridBtn.addEventListener('click', () => setViewMode('grid'));
    viewListBtn.addEventListener('click', () => setViewMode('list'));

    // Fechar modal ao clicar fora
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    // Fechar modal com ESC
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
    });
}

// Carregar lotes da API (ou dados de exemplo)
async function carregarLotes() {
    loading.style.display = 'flex';
    lotesContainer.innerHTML = '';
    noResults.style.display = 'none';

    try {
        // Tenta buscar da API real
        const codEmpreendimento = empreendimento.value;
        const response = await fetch(`http://apiweb.valleprime.com.br:8000/api/consulta/${codEmpreendimento}/`);

        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                todosLotes = data.data;
            } else {
                throw new Error('API retornou erro');
            }
        } else {
            throw new Error('Erro na requisição');
        }
    } catch (error) {
        console.log('Usando dados de exemplo (API indisponível):', error.message);
        // Usa dados de exemplo se a API falhar
        todosLotes = dadosExemplo.data;
    }

    loading.style.display = 'none';

    // Preencher filtro de quadras
    preencherFiltroQuadras();

    // Aplicar filtros iniciais
    aplicarFiltros();

    // Atualizar estatísticas
    atualizarEstatisticas();
}

// Preencher filtro de quadras
function preencherFiltroQuadras() {
    const quadras = [...new Set(todosLotes.map(l => l.QD))].sort();
    quadraFilter.innerHTML = '<option value="">Todas</option>';
    quadras.forEach(qd => {
        quadraFilter.innerHTML += `<option value="${qd}">Quadra ${qd}</option>`;
    });
}

// Aplicar filtros
function aplicarFiltros() {
    const status = statusFilter.value;
    const quadra = quadraFilter.value;
    const busca = searchInput.value.toLowerCase().trim();

    lotesFiltrados = todosLotes.filter(lote => {
        // Filtro de status
        if (status) {
            const statusLote = getStatusKey(lote.Status_Terreno);
            if (statusLote !== status) return false;
        }

        // Filtro de quadra
        if (quadra && lote.QD !== quadra) return false;

        // Filtro de busca
        if (busca) {
            const textoLote = `${lote.QD} ${lote.LT} ${lote.Logradouro}`.toLowerCase();
            if (!textoLote.includes(busca)) return false;
        }

        return true;
    });

    renderizarLotes();
}

// Obter chave de status
function getStatusKey(status) {
    if (status.includes('Disponível')) return 'disponivel';
    if (status.includes('Reservado')) return 'reservado';
    if (status.includes('Vendido')) return 'vendido';
    if (status.includes('Quitado')) return 'quitado';
    if (status.includes('Fora')) return 'fora';
    return 'outro';
}

// Obter classe CSS do status
function getStatusClass(status) {
    const key = getStatusKey(status);
    return `status-${key}`;
}

// Obter label do status
function getStatusLabel(status) {
    if (status.includes('Disponível')) return 'Disponível';
    if (status.includes('Reservado')) return 'Reservado';
    if (status.includes('Vendido')) return 'Vendido';
    if (status.includes('Quitado')) return 'Quitado';
    if (status.includes('Fora')) return 'Fora de Venda';
    return status;
}

// Renderizar lotes
function renderizarLotes() {
    lotesContainer.innerHTML = '';
    resultCountEl.textContent = lotesFiltrados.length;

    if (lotesFiltrados.length === 0) {
        noResults.style.display = 'flex';
        return;
    }

    noResults.style.display = 'none';

    lotesFiltrados.forEach(lote => {
        const card = criarCardLote(lote);
        lotesContainer.innerHTML += card;
    });
}

// Criar card de lote
function criarCardLote(lote) {
    const statusClass = getStatusClass(lote.Status_Terreno);
    const statusLabel = getStatusLabel(lote.Status_Terreno);

    return `
        <div class="lote-card" onclick="abrirModal('${lote.QD}', '${lote.LT}')">
            <div class="lote-header">
                <div class="lote-id">
                    <span class="lote-quadra">Quadra ${lote.QD}</span>
                    <span class="lote-numero">Lote ${lote.LT}</span>
                </div>
                <span class="lote-status ${statusClass}">${statusLabel}</span>
            </div>
            <div class="lote-body">
                <div class="lote-info">
                    <div class="lote-info-item">
                        <span class="lote-info-label">Área</span>
                        <span class="lote-info-value">${lote.M2} m²</span>
                    </div>
                    <div class="lote-info-item">
                        <span class="lote-info-label">Frente</span>
                        <span class="lote-info-value">${lote.M_Frente} m</span>
                    </div>
                    <div class="lote-info-item">
                        <span class="lote-info-label">Fundo</span>
                        <span class="lote-info-value">${lote.M_Fundo} m</span>
                    </div>
                    <div class="lote-info-item">
                        <span class="lote-info-label">Lado Dir.</span>
                        <span class="lote-info-value">${lote.M_Lado_Direito} m</span>
                    </div>
                </div>
                <div class="lote-logradouro">📍 ${lote.Logradouro}</div>
            </div>
            <div class="lote-footer">
                <span class="lote-preco">R$ ${lote.Valor_Terreno}</span>
                <button class="btn-detalhes" onclick="event.stopPropagation(); abrirModal('${lote.QD}', '${lote.LT}')">Ver Detalhes</button>
            </div>
        </div>
    `;
}

// Atualizar estatísticas
function atualizarEstatisticas() {
    const total = todosLotes.length;
    const disponiveis = todosLotes.filter(l => l.Status_Terreno.includes('Disponível')).length;
    const reservados = todosLotes.filter(l => l.Status_Terreno.includes('Reservado')).length;
    const vendidos = todosLotes.filter(l => l.Status_Terreno.includes('Vendido') || l.Status_Terreno.includes('Quitado')).length;

    animateNumber(totalLotesEl, total);
    animateNumber(lotesDisponiveisEl, disponiveis);
    animateNumber(lotesReservadosEl, reservados);
    animateNumber(lotesVendidosEl, vendidos);
}

// Animar número
function animateNumber(element, target) {
    let current = 0;
    const increment = Math.ceil(target / 30);
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        element.textContent = current;
    }, 30);
}

// Mudar modo de visualização
function setViewMode(mode) {
    viewMode = mode;

    if (mode === 'grid') {
        lotesContainer.className = 'lotes-grid';
        viewGridBtn.classList.add('active');
        viewListBtn.classList.remove('active');
    } else {
        lotesContainer.className = 'lotes-list';
        viewListBtn.classList.add('active');
        viewGridBtn.classList.remove('active');
    }
}

// Abrir modal de detalhes
function abrirModal(quadra, lote) {
    const loteData = todosLotes.find(l => l.QD === quadra && l.LT === lote);
    if (!loteData) return;

    const statusClass = getStatusClass(loteData.Status_Terreno);
    const statusLabel = getStatusLabel(loteData.Status_Terreno);
    const isDisponivel = loteData.Status_Terreno.includes('Disponível');

    modalBody.innerHTML = `
        <div class="modal-header">
            <h2 class="modal-title">Quadra ${loteData.QD} - Lote ${loteData.LT}</h2>
            <p class="modal-subtitle">${loteData.Logradouro}</p>
        </div>
        
        <div class="modal-body">
            <div class="modal-section">
                <div class="modal-grid">
                    <div class="modal-item">
                        <span class="modal-label">Status</span>
                        <span class="lote-status ${statusClass}" style="display: inline-block; margin-top: 4px;">${statusLabel}</span>
                    </div>
                    <div class="modal-item">
                        <span class="modal-label">Atualizado em</span>
                        <span class="modal-value">${loteData.Data_Atualizacao}</span>
                    </div>
                </div>
            </div>
            
            <div class="modal-section">
                <h3 class="modal-section-title">Dimensões</h3>
                <div class="modal-grid">
                    <div class="modal-item">
                        <span class="modal-label">Área Total</span>
                        <span class="modal-value">${loteData.M2} m²</span>
                    </div>
                    <div class="modal-item">
                        <span class="modal-label">Frente</span>
                        <span class="modal-value">${loteData.M_Frente} m</span>
                    </div>
                    <div class="modal-item">
                        <span class="modal-label">Fundo</span>
                        <span class="modal-value">${loteData.M_Fundo} m</span>
                    </div>
                    <div class="modal-item">
                        <span class="modal-label">Lado Direito</span>
                        <span class="modal-value">${loteData.M_Lado_Direito} m</span>
                    </div>
                    <div class="modal-item">
                        <span class="modal-label">Lado Esquerdo</span>
                        <span class="modal-value">${loteData.M_Lado_Esquerdo} m</span>
                    </div>
                    <div class="modal-item">
                        <span class="modal-label">Chanfro</span>
                        <span class="modal-value">${loteData.Chanfro}</span>
                    </div>
                </div>
            </div>
            
            <div class="modal-section">
                <h3 class="modal-section-title">Valor</h3>
                <div class="modal-item">
                    <span class="modal-label">Valor do Terreno</span>
                    <span class="modal-value preco">R$ ${loteData.Valor_Terreno}</span>
                </div>
            </div>
        </div>
        
        <div class="modal-footer">
            <button class="btn-secondary" onclick="closeModal()">Fechar</button>
            ${isDisponivel ? `
                <a href="../propostatest.html" target="_blank" class="btn-success">
                    📝 Gerar Proposta
                </a>
            ` : ''}
        </div>
    `;

    modal.classList.add('active');
}

// Fechar modal
function closeModal() {
    modal.classList.remove('active');
}
