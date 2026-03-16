document.addEventListener('DOMContentLoaded', () => {
    // Elementos da Busca
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    const resultsGrid = document.getElementById('resultsGrid');
    const resultsSection = document.getElementById('resultsSection');
    const resultCount = document.getElementById('resultCount');
    
    // Elementos de Filtro
    const empresaFilter = document.getElementById('empresaFilter');
    const obraFilter = document.getElementById('obraFilter');

    // Elementos do Modal
    const modal = document.getElementById('generateModal');
    const modalClientName = document.getElementById('modalClientName');
    const confirmGenBtn = document.getElementById('confirmGenBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const closeBtn = document.querySelector('.close-btn');
    const templateSelect = document.getElementById('templateSelect');
    const genStatus = document.getElementById('genStatus');

    let selectedSale = null;

    // Carregar Filtros Iniciais
    async function loadFilters() {
        try {
            const response = await fetch('/api/filters');
            const data = await response.json();
            
            if (data.empresas) {
                data.empresas.forEach(emp => {
                    const opt = document.createElement('option');
                    opt.value = emp;
                    opt.textContent = `Empresa ${emp}`;
                    empresaFilter.appendChild(opt);
                });
            }
            if (data.obras) {
                data.obras.forEach(obra => {
                    const opt = document.createElement('option');
                    opt.value = obra;
                    opt.textContent = `Obra ${obra}`;
                    obraFilter.appendChild(opt);
                });
            }
        } catch (error) {
            console.error('Erro ao carregar filtros:', error);
        }
    }

    // Função de Busca
    async function performSearch() {
        const query = searchInput.value.trim();
        const empresa = empresaFilter.value;
        const obra = obraFilter.value;

        if (!query) {
            resultsGrid.innerHTML = '<div class="empty-state">Digite algo para pesquisar...</div>';
            return;
        }

        searchBtn.disabled = true;
        searchBtn.textContent = 'Buscando...';
        resultsGrid.innerHTML = '<div class="empty-state">Consultando banco UAU...</div>';
        resultsSection.classList.add('visible');

        try {
            const params = new URLSearchParams({
                q: query,
                empresa: empresa,
                obra: obra
            });
            
            const response = await fetch(`/api/search_sales?${params.toString()}`);
            const data = await response.json();

            if (data.error) throw new Error(data.error);

            resultsGrid.innerHTML = '';
            resultCount.textContent = data.length;

            if (data.length === 0) {
                resultsGrid.innerHTML = '<div class="empty-state">Nenhuma venda encontrada para os filtros aplicados.</div>';
            } else {
                data.forEach(sale => {
                    const card = document.createElement('div');
                    card.className = 'sale-card';
                    card.innerHTML = `
                        <div class="badge">VENDA #${sale.id}</div>
                        <div class="obra-info">Empresa ${sale.empresa} | Obra ${sale.obra}</div>
                        <h4>${sale.cliente}</h4>
                        <div class="meta">
                            <p><strong>CPF/CNPJ:</strong> ${sale.cpf}</p>
                            <p><strong>Data Venda:</strong> ${sale.data}</p>
                        </div>
                        <button class="btn-generate" 
                                data-id="${sale.id}" 
                                data-name="${sale.cliente}" 
                                data-emp="${sale.empresa}" 
                                data-obr="${sale.obra}"
                                style="margin-top: 15px;">
                            Configurar Documento
                        </button>
                    `;
                    resultsGrid.appendChild(card);
                });
            }
        } catch (error) {
            resultsGrid.innerHTML = `<div class="empty-state status-error">Erro na conexão: ${error.message}</div>`;
        } finally {
            searchBtn.disabled = false;
            searchBtn.textContent = 'Pesquisar';
        }
    }

    // Eventos
    searchBtn.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') performSearch();
    });

    // Abrir Modal
    resultsGrid.addEventListener('click', (e) => {
        if (e.target.classList.contains('btn-generate')) {
            selectedSale = {
                id: e.target.dataset.id,
                name: e.target.dataset.name,
                empresa: e.target.dataset.emp,
                obra: e.target.dataset.obr
            };
            modalClientName.textContent = selectedSale.name;
            genStatus.innerHTML = '';
            templateSelect.value = '';
            modal.style.display = 'block';
        }
    });

    // Fechar Modal
    const closeModal = () => modal.style.display = 'none';
    closeBtn.addEventListener('click', closeModal);
    cancelBtn.addEventListener('click', closeModal);
    window.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    // Gerar Contrato
    confirmGenBtn.addEventListener('click', async () => {
        const template = templateSelect.value;
        if (!template) {
            genStatus.innerHTML = '<span class="status-error">Selecione o modelo .docx!</span>';
            return;
        }

        confirmGenBtn.disabled = true;
        confirmGenBtn.textContent = 'Processando...';
        genStatus.innerHTML = 'Extraindo dados e preenchendo...';

        try {
            const response = await fetch('/api/generate_contract', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sale_id: selectedSale.id,
                    template: template,
                    empresa: selectedSale.empresa,
                    obra: selectedSale.obra
                })
            });

            const result = await response.json();

            if (result.status === 'success') {
                genStatus.innerHTML = `<span class="status-success">${result.message}</span>`;
                window.location.href = result.file_url;
                setTimeout(closeModal, 2000);
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            let msg = error.message;
            if (msg.includes('Package not found')) {
                msg = `ERRO: O arquivo "${template}" não foi encontrado na pasta /templates. Certifique-se de que salvou como .docx!`;
            }
            genStatus.innerHTML = `<span class="status-error">${msg}</span>`;
        } finally {
            confirmGenBtn.disabled = false;
            confirmGenBtn.textContent = 'Gerar e Baixar';
        }
    });

    // Inicialização
    loadFilters();
});
