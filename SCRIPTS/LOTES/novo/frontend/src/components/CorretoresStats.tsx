import React, { useState, useEffect, useMemo } from 'react';
import type { ResumoVenda } from '../types';

interface CorretoresStatsProps {
    empresa: number;
    obra: string;
    refreshKey: number;
}

interface CorretorStats {
    nome: string;
    totalVendas: number;
    valorTotal: number;
    comBoleto: number;
    semBoleto: number;
    sinaisAbertos: number;
    valorSinaisAberto: number;
    sinaisPagos: number;
    valorSinaisPagos: number;
    sinaisVencidos: number;
    valorSinaisVencidos: number;
}

// Interface for detailed sales data
interface VendaDetalhe {
    venda: number;
    cliente: string;
    identificador: string;
    dataVenda: string;
    valorTotal: number;
    boletoGerado: boolean;
    sinaisAberto: number;
    sinaisPagos: number;
    sinaisTotal: number;
    primeiroVencimento?: string;
}

export const CorretoresStats: React.FC<CorretoresStatsProps> = ({ empresa, obra, refreshKey }) => {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [data, setData] = useState<ResumoVenda[]>([]);
    const [sortBy, setSortBy] = useState<'vendas' | 'valor'>('vendas');
    const [generatingPdf, setGeneratingPdf] = useState<string | null>(null);
    const [startDate, setStartDate] = useState<string>('');
    const [endDate, setEndDate] = useState<string>('');
    const [searchTerm, setSearchTerm] = useState('');
    const [estruturas, setEstruturas] = useState<{ codigo: number, nome: string }[]>([]);
    const [selectedEstrutura, setSelectedEstrutura] = useState<string>('');

    // Drawer state for master-detail view
    const [drawerOpen, setDrawerOpen] = useState(false);
    const [selectedCorretor, setSelectedCorretor] = useState<CorretorStats | null>(null);
    const [corretorVendas, setCorretorVendas] = useState<VendaDetalhe[]>([]);
    const [loadingVendas, setLoadingVendas] = useState(false);

    // Auto-load when empresa/obra change or refreshKey settings change
    useEffect(() => {
        loadData();
    }, [empresa, obra, refreshKey, selectedEstrutura]);

    // Fetch structures when context changes
    useEffect(() => {
        fetchEstruturas();
    }, [empresa, obra, startDate, endDate]);

    const fetchEstruturas = async () => {
        try {
            let url = `/api/corretores/estruturas?empresa=${empresa}&obra=${obra}`;
            if (startDate) url += `&data_inicio=${startDate}`;
            if (endDate) url += `&data_fim=${endDate}`;

            const response = await fetch(url);
            if (response.ok) {
                const data = await response.json();
                setEstruturas(data);

                // Reset selected structure if it's not in the new list
                if (selectedEstrutura && !data.find((e: any) => e.codigo.toString() === selectedEstrutura)) {
                    setSelectedEstrutura('');
                }
            }
        } catch (err) {
            console.error('Erro ao buscar estruturas:', err);
        }
    };

    const loadData = async () => {
        setLoading(true);
        setError(null);
        try {
            // Usar endpoint otimizado que faz agregação no SQL
            // Passar datas se definidas
            let url = `/api/corretores/stats?empresa=${empresa}&obra=${obra}`;
            if (startDate) {
                url += `&data_inicio=${startDate}`;
            }
            if (endDate) {
                url += `&data_fim=${endDate}`;
            }
            if (selectedEstrutura) {
                url += `&estrutura=${selectedEstrutura}`;
            }
            const response = await fetch(url);
            if (!response.ok) throw new Error('Erro ao carregar dados');
            const result = await response.json();

            // Converter dados agregados para o formato esperado pelo componente
            setData(result.corretores.map((c: any) => ({
                corretor: c.corretor,
                valorTotal: c.totalVendas,
                _aggregated: true,
                _totalVendas: c.totalVendas,
                _valorTotal: c.valorTotal,
                _comBoleto: c.comBoleto || 0,
                _sinaisAbertos: c.sinaisAbertos || 0,
                _valorSinaisAberto: c.valorSinaisAberto || 0,
                _sinaisPagos: c.sinaisPagos || 0,
                _valorSinaisPagos: c.valorSinaisPagos || 0,
                _sinaisVencidos: c.sinaisVencidos || 0,
                _valorSinaisVencidos: c.valorSinaisVencidos || 0
            })));
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erro ao carregar dados');
        } finally {
            setLoading(false);
        }
    };

    // Open drawer with corretor details
    const openCorretorDrawer = async (corretor: CorretorStats, rank: number) => {
        setSelectedCorretor({ ...corretor, rank } as any);
        setDrawerOpen(true);
        setLoadingVendas(true);

        try {
            // Load detailed sales data for this corretor
            let url = `/api/resumo?empresa=${empresa}&obra=${obra}`;
            if (selectedEstrutura) {
                url += `&estrutura=${selectedEstrutura}`;
            }
            if (startDate) {
                url += `&data_inicio=${startDate}`;
            }
            if (endDate) {
                url += `&data_fim=${endDate}`;
            }
            const response = await fetch(url);
            if (!response.ok) throw new Error('Erro ao carregar vendas');
            const result = await response.json();

            // Filter vendasfor this corretor
            let vendas = (result.data || []).filter((v: any) =>
                (v.corretor || 'Não informado') === corretor.nome
            );

            // Apply date filter if set
            if (startDate || endDate) {
                vendas = vendas.filter((v: any) => {
                    const dateStr = v.dataVenda || v.dataCadastro;
                    if (!dateStr) return false;
                    const parts = dateStr.split('/');
                    if (parts.length !== 3) return false;
                    const vendaDate = new Date(parseInt(parts[2]), parseInt(parts[1]) - 1, parseInt(parts[0]));

                    if (startDate) {
                        const start = new Date(startDate);
                        if (vendaDate < start) return false;
                    }
                    if (endDate) {
                        const end = new Date(endDate);
                        end.setHours(23, 59, 59, 999);
                        if (vendaDate > end) return false;
                    }
                    return true;
                });
            }

            setCorretorVendas(vendas);
        } catch (err) {
            console.error('Erro ao carregar vendas:', err);
            setCorretorVendas([]);
        } finally {
            setLoadingVendas(false);
        }
    };

    // Close drawer
    const closeDrawer = () => {
        setDrawerOpen(false);
        setSelectedCorretor(null);
        setCorretorVendas([]);
    };

    const parseQuadraLote = (identificador: string) => {
        if (!identificador) return { quadra: '-', lote: '-' };
        const parts = identificador.split(' - ');
        const quadraLote = parts[1] || '';
        const quadraMatch = quadraLote.match(/Q(\d+)/);
        const loteMatch = quadraLote.match(/L(\d+)/);
        return {
            quadra: quadraMatch ? quadraMatch[1].padStart(3, '0') : '-',
            lote: loteMatch ? loteMatch[1].padStart(3, '0') : '-'
        };
    };

    const generateCorretorPdf = async (corretorNome: string, corretorData?: CorretorStats) => {
        setGeneratingPdf(corretorNome);

        try {
            let url = `/api/resumo?empresa=${empresa}&obra=${obra}`;
            if (selectedEstrutura) {
                url += `&estrutura=${selectedEstrutura}`;
            }
            if (startDate) {
                url += `&data_inicio=${startDate}`;
            }
            if (endDate) {
                url += `&data_fim=${endDate}`;
            }

            const response = await fetch(url);
            if (!response.ok) throw new Error('Erro ao carregar dados');
            const result = await response.json();
            if (!result?.data) throw new Error('Dados não encontrados');

            let vendasCorretor = result.data.filter((v: any) => (v.corretor || 'Não informado') === corretorNome);

            if (vendasCorretor.length === 0) {
                alert(`Nenhuma venda encontrada para ${corretorNome}`);
                return;
            }

            const { jsPDF } = await import('jspdf');
            const autoTable = (await import('jspdf-autotable')).default;

            // Usar nome da obra que vem do endpoint
            const obraNome = result.obraNome || `${empresa} - ${obra}`;

            // RETRATO - A4
            const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
            const pageWidth = 210;
            const pageHeight = 297;

            // Cores
            const blue = [0, 137, 214];
            const green = [34, 197, 94];
            const red = [220, 38, 38];
            const orange = [245, 158, 11];
            const gray = [100, 100, 100];
            const darkGray = [40, 40, 40];

            // Se há filtro de data, sempre usar dados filtrados (vendasCorretor)
            // Senão, usar dados do corretor da tela principal
            const hasDateFilter = startDate || endDate;
            const totalVendas = hasDateFilter ? vendasCorretor.length : (corretorData ? corretorData.totalVendas : vendasCorretor.length);
            const valorTotalVendas = hasDateFilter
                ? vendasCorretor.reduce((s: number, v: any) => s + (v.valorTotal || 0), 0)
                : (corretorData ? corretorData.valorTotal : vendasCorretor.reduce((s: number, v: any) => s + (v.valorTotal || 0), 0));
            const sinaisPagos = hasDateFilter
                ? vendasCorretor.reduce((s: number, v: any) => s + (v.sinaisPagos || 0), 0)
                : (corretorData ? corretorData.sinaisPagos : vendasCorretor.reduce((s: number, v: any) => s + (v.sinaisPagos || 0), 0));
            const valorRecebido = hasDateFilter
                ? vendasCorretor.reduce((s: number, v: any) => s + (v.valorSinaisPagos || 0), 0)
                : (corretorData ? corretorData.valorSinaisPagos : vendasCorretor.reduce((s: number, v: any) => s + (v.valorSinaisPagos || 0), 0));
            const sinaisAbertos = hasDateFilter
                ? vendasCorretor.reduce((s: number, v: any) => s + (v.sinaisAberto || 0), 0)
                : (corretorData ? corretorData.sinaisAbertos : vendasCorretor.reduce((s: number, v: any) => s + (v.sinaisAberto || 0), 0));
            const valorPendente = hasDateFilter
                ? vendasCorretor.reduce((s: number, v: any) => s + (v.valorSinaisAberto || 0), 0)
                : (corretorData ? corretorData.valorSinaisAberto : vendasCorretor.reduce((s: number, v: any) => s + (v.valorSinaisAberto || 0), 0));
            const sinaisVencidos = hasDateFilter
                ? vendasCorretor.reduce((s: number, v: any) => s + (v.sinaisVencidos || 0), 0)
                : (corretorData ? corretorData.sinaisVencidos : vendasCorretor.reduce((s: number, v: any) => s + (v.sinaisVencidos || 0), 0));
            const valorVencido = hasDateFilter
                ? vendasCorretor.reduce((s: number, v: any) => s + (v.valorSinaisVencidos || 0), 0)
                : (corretorData ? corretorData.valorSinaisVencidos : vendasCorretor.reduce((s: number, v: any) => s + (v.valorSinaisVencidos || 0), 0));
            const sinaisTotal = sinaisPagos + sinaisAbertos;
            const taxaConversao = sinaisTotal > 0 ? ((sinaisPagos / sinaisTotal) * 100) : 0;

            const fmt = (v: number) => `R$ ${v.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`;
            const fmtDate = (d: string) => d ? d.split('-').reverse().join('/') : '';

            // ========== HEADER ==========
            // Fundo branco para logo
            doc.setFillColor(255, 255, 255);
            doc.rect(0, 0, pageWidth, 40, 'F');

            // Barra azul no topo
            doc.setFillColor(blue[0], blue[1], blue[2]);
            doc.rect(0, 0, pageWidth, 3, 'F');

            // Logo VallePrime (imagem proporcional)
            try {
                const logoImg = new Image();
                logoImg.src = '/logoprime.png';
                await new Promise((resolve) => {
                    logoImg.onload = resolve;
                    logoImg.onerror = resolve;
                });
                if (logoImg.complete && logoImg.naturalWidth > 0) {
                    // Manter proporcao original
                    const logoHeight = 28;
                    const aspectRatio = logoImg.naturalWidth / logoImg.naturalHeight;
                    const logoWidth = logoHeight * aspectRatio;
                    doc.addImage(logoImg, 'PNG', 10, 7, logoWidth, logoHeight);
                }
            } catch (e) {
                // Se logo falhar, usar texto
                doc.setTextColor(blue[0], blue[1], blue[2]);
                doc.setFontSize(14);
                doc.setFont('helvetica', 'bold');
                doc.text('VALLEPRIME', 10, 25);
            }

            // Nome do empreendimento (destaque) - usando obraNome buscado da API
            doc.setTextColor(blue[0], blue[1], blue[2]);
            doc.setFontSize(11);
            doc.setFont('helvetica', 'bold');
            // Mostrar nome completo do empreendimento
            doc.text(obraNome, 70, 10);

            // Subtitulo
            doc.setTextColor(darkGray[0], darkGray[1], darkGray[2]);
            doc.setFontSize(9);
            doc.setFont('helvetica', 'normal');
            doc.text('Relatorio de Performance do Corretor', 70, 18);

            // Nome do corretor
            doc.setFontSize(12);
            doc.setFont('helvetica', 'bold');
            doc.text(corretorNome, 70, 27);

            // Periodo se houver
            if (startDate || endDate) {
                doc.setFontSize(8);
                doc.setFont('helvetica', 'normal');
                doc.setTextColor(gray[0], gray[1], gray[2]);
                doc.text(`Periodo: ${fmtDate(startDate) || 'Inicio'} a ${fmtDate(endDate) || 'Hoje'}`, 70, 34);
            }

            // Data a direita
            doc.setTextColor(darkGray[0], darkGray[1], darkGray[2]);
            doc.setFontSize(9);
            doc.text(new Date().toLocaleDateString('pt-BR', { day: '2-digit', month: 'long', year: 'numeric' }), pageWidth - 15, 10, { align: 'right' });
            if (startDate || endDate) {
                doc.text(`Periodo: ${fmtDate(startDate) || 'Inicio'} a ${fmtDate(endDate) || 'Hoje'}`, pageWidth - 15, 18, { align: 'right' });
            }

            // Estrutura info
            const estruturaNome = estruturas.find(e => e.codigo.toString() === selectedEstrutura)?.nome;
            if (estruturaNome) {
                doc.setFontSize(8);
                doc.setTextColor(blue[0], blue[1], blue[2]);
                doc.text(`Estrutura: ${estruturaNome} | Empresa: ${empresa}`, 70, 40);
            }

            // Linha separadora
            doc.setDrawColor(220, 220, 220);
            doc.line(10, 42, pageWidth - 10, 42);

            // ========== RESUMO DE PERFORMANCE ==========
            let y = 50;

            doc.setTextColor(darkGray[0], darkGray[1], darkGray[2]);
            doc.setFontSize(11);
            doc.setFont('helvetica', 'bold');
            doc.text('RESUMO DE PERFORMANCE', 15, y);
            y += 8;

            // Grid 2x2 de métricas principais
            const boxW = 88;
            const boxH = 28;
            const gap = 4;

            const drawMetricBox = (x: number, yPos: number, label: string, value: string, subLabel: string, color: number[]) => {
                // Fundo
                doc.setFillColor(250, 250, 250);
                doc.roundedRect(x, yPos, boxW, boxH, 3, 3, 'F');

                // Barra lateral colorida
                doc.setFillColor(color[0], color[1], color[2]);
                doc.rect(x, yPos, 3, boxH, 'F');

                // Label
                doc.setTextColor(gray[0], gray[1], gray[2]);
                doc.setFontSize(8);
                doc.setFont('helvetica', 'normal');
                doc.text(label, x + 8, yPos + 8);

                // Valor
                doc.setTextColor(darkGray[0], darkGray[1], darkGray[2]);
                doc.setFontSize(14);
                doc.setFont('helvetica', 'bold');
                doc.text(value, x + 8, yPos + 18);

                // SubLabel
                doc.setTextColor(color[0], color[1], color[2]);
                doc.setFontSize(8);
                doc.setFont('helvetica', 'normal');
                doc.text(subLabel, x + 8, yPos + 24);
            };

            // Linha 1
            drawMetricBox(15, y, 'TOTAL DE VENDAS', totalVendas.toString(), fmt(valorTotalVendas), blue as number[]);
            drawMetricBox(15 + boxW + gap, y, 'VALOR RECEBIDO', fmt(valorRecebido), `${sinaisPagos} sinais pagos`, green as number[]);

            y += boxH + gap;

            // Linha 2
            drawMetricBox(15, y, 'VALOR PENDENTE', fmt(valorPendente), `${sinaisAbertos} sinais abertos`, orange as number[]);
            drawMetricBox(15 + boxW + gap, y, 'VENCIDOS', fmt(valorVencido), sinaisVencidos > 0 ? `${sinaisVencidos} sinais vencidos` : 'Nenhum vencido', red as number[]);

            y += boxH + 12;

            // Taxa de conversão (barra de progresso)
            doc.setTextColor(darkGray[0], darkGray[1], darkGray[2]);
            doc.setFontSize(9);
            doc.setFont('helvetica', 'bold');
            doc.text(`Taxa de Recebimento: ${taxaConversao.toFixed(1)}%`, 15, y);

            // Barra de fundo
            doc.setFillColor(230, 230, 230);
            doc.roundedRect(15, y + 2, pageWidth - 30, 4, 2, 2, 'F');

            // Barra de progresso
            const progressWidth = Math.min(((pageWidth - 30) * taxaConversao) / 100, pageWidth - 30);
            if (progressWidth > 0) {
                doc.setFillColor(green[0], green[1], green[2]);
                doc.roundedRect(15, y + 2, progressWidth, 4, 2, 2, 'F');
            }

            y += 15;

            // ========== LISTA DE VENDAS ==========
            doc.setDrawColor(220, 220, 220);
            doc.line(15, y, pageWidth - 15, y);
            y += 6;

            doc.setTextColor(darkGray[0], darkGray[1], darkGray[2]);
            doc.setFontSize(11);
            doc.setFont('helvetica', 'bold');
            doc.text(`DETALHAMENTO DAS VENDAS (${totalVendas})`, 15, y);
            y += 6;

            // Tabela compacta
            const tableData = vendasCorretor.map((v: any) => {
                const { quadra, lote } = parseQuadraLote(v.identificador);
                return {
                    venda: v.venda || '-',
                    cliente: (v.cliente || '-').substring(0, 20),
                    ql: `${quadra}/${lote}`,
                    dataVenda: v.dataVenda || '-',
                    valorTotal: v.valorTotal || 0,
                    sTotal: v.sinaisTotal || 0,
                    sPagos: v.sinaisPagos || 0,
                    sVenc: v.sinaisVencidos || 0,
                    sPend: v.sinaisAberto || 0,
                    valorRec: v.valorSinaisPagos || 0
                };
            });

            // Body rows  
            const bodyRows = tableData.map((r: any) => [
                r.venda,
                r.cliente,
                r.ql,
                r.dataVenda,
                fmt(r.valorTotal),
                r.sTotal,
                r.sPagos,
                r.sVenc,
                r.sPend,
                fmt(r.valorRec)
            ]);

            // Calcular totais dos dados FILTRADOS (vendasCorretor)
            const tValorVendas = tableData.reduce((s: number, r: any) => s + r.valorTotal, 0);
            const tSinaisTotal = tableData.reduce((s: number, r: any) => s + r.sTotal, 0);
            const tSinaisPagos = tableData.reduce((s: number, r: any) => s + r.sPagos, 0);
            const tSinaisVenc = tableData.reduce((s: number, r: any) => s + r.sVenc, 0);
            const tSinaisPend = tableData.reduce((s: number, r: any) => s + r.sPend, 0);
            const tValorRec = tableData.reduce((s: number, r: any) => s + r.valorRec, 0);

            // Linha de totais como ultima linha
            const totalsRow = [
                'TOTAL',
                `${tableData.length} vendas`,
                '',
                '',
                fmt(tValorVendas),
                tSinaisTotal,
                tSinaisPagos,
                tSinaisVenc,
                tSinaisPend,
                fmt(tValorRec)
            ];

            // Adicionar linha de totais ao final
            bodyRows.push(totalsRow);
            const totalsRowIndex = bodyRows.length - 1;

            autoTable(doc, {
                startY: y,
                margin: { left: 10, right: 10, bottom: 20 },
                tableWidth: 'auto',
                head: [['#', 'Cliente', 'Q/L', 'Data', 'Valor Venda', 'Total', 'Pagos', 'Venc.', 'Pend.', 'Valor Recebido']],
                body: bodyRows,
                theme: 'striped',
                headStyles: {
                    fillColor: [0, 137, 214],
                    textColor: [255, 255, 255],
                    fontStyle: 'bold',
                    fontSize: 6.5,
                    cellPadding: 1.5,
                    halign: 'center'
                },
                bodyStyles: {
                    fontSize: 6.5,
                    cellPadding: 1.5,
                    textColor: darkGray as any
                },
                alternateRowStyles: {
                    fillColor: [248, 248, 248]
                },
                columnStyles: {
                    0: { halign: 'center', cellWidth: 12 },
                    1: { cellWidth: 'auto' },  // Cliente - expande
                    2: { halign: 'center', cellWidth: 14 },
                    3: { halign: 'center', cellWidth: 20 },  // Data
                    4: { halign: 'right', cellWidth: 24 },
                    5: { halign: 'center', cellWidth: 10 },
                    6: { halign: 'center', cellWidth: 10 },
                    7: { halign: 'center', cellWidth: 10 },
                    8: { halign: 'center', cellWidth: 10 },
                    9: { halign: 'right', cellWidth: 24 }
                },
                didParseCell: (data: any) => {
                    if (data.section === 'body') {
                        // Linha de totais - estilo especial
                        if (data.row.index === totalsRowIndex) {
                            data.cell.styles.fillColor = [0, 137, 214];
                            data.cell.styles.textColor = [255, 255, 255];
                            data.cell.styles.fontStyle = 'bold';
                            data.cell.styles.fontSize = 7;
                            return;
                        }

                        const row = tableData[data.row.index];
                        if (!row) return;

                        // Pagos em verde (index 6)
                        if (data.column.index === 6 && row.sPagos > 0) {
                            data.cell.styles.textColor = green;
                            data.cell.styles.fontStyle = 'bold';
                        }
                        // Vencidos em vermelho (index 7)
                        if (data.column.index === 7 && row.sVenc > 0) {
                            data.cell.styles.textColor = red;
                            data.cell.styles.fontStyle = 'bold';
                        }
                        // Pendentes em laranja (index 8)
                        if (data.column.index === 8 && row.sPend > 0) {
                            data.cell.styles.textColor = orange;
                            data.cell.styles.fontStyle = 'bold';
                        }
                        // Valor recebido em verde (index 9)
                        if (data.column.index === 9 && row.valorRec > 0) {
                            data.cell.styles.textColor = green;
                        }
                    }
                },
                didDrawPage: (data: any) => {
                    const pageCount = doc.internal.pages.length - 1;
                    // Footer da pagina
                    doc.setDrawColor(220, 220, 220);
                    doc.line(10, pageHeight - 12, pageWidth - 10, pageHeight - 12);
                    doc.setFontSize(7);
                    doc.setTextColor(gray[0], gray[1], gray[2]);
                    doc.text('VallePrime - Sistema de Gestao de Vendas', 10, pageHeight - 6);
                    doc.text(`Pagina ${data.pageNumber}/${pageCount}`, pageWidth / 2, pageHeight - 6, { align: 'center' });
                    doc.text('Desenvolvido por Vinicius Dev', pageWidth - 10, pageHeight - 6, { align: 'right' });
                }
            });

            // ========== LEGENDA ==========
            const finalY = (doc as any).lastAutoTable.finalY + 3;

            // Verifica se há espaço
            if (finalY > pageHeight - 20) {
                doc.addPage();
            }

            const legendY = finalY > pageHeight - 20 ? 15 : finalY;

            // Legenda simples usando autoTable
            autoTable(doc, {
                startY: legendY,
                margin: { left: 10, right: 10 },
                tableWidth: 'auto',
                head: [['LEGENDA: Significado das Colunas de Sinais']],
                body: [[
                    'Total = Qtd. sinais  |  Pagos = Recebidos (verde)  |  Venc. = Atrasados (vermelho)  |  Pend. = A vencer (laranja)  |  Valor Rec. = Total recebido'
                ]],
                theme: 'plain',
                headStyles: {
                    fillColor: [240, 240, 240],
                    textColor: [60, 60, 60],
                    fontStyle: 'bold',
                    fontSize: 7,
                    cellPadding: 2,
                    halign: 'left'
                },
                bodyStyles: {
                    fontSize: 6,
                    cellPadding: 2,
                    textColor: [100, 100, 100]
                },
                columnStyles: {
                    0: { cellWidth: pageWidth - 20 }
                }
            });

            window.open(URL.createObjectURL(doc.output('blob')), '_blank');

        } catch (err) {
            console.error('PDF Error:', err);
            alert('Erro ao gerar PDF');
        } finally {
            setGeneratingPdf(null);
        }
    };

    const generateEstruturaPdf = async () => {
        const estruturaCod = selectedEstrutura || '';
        const estruturaObj = estruturas.find(e => e.codigo.toString() === estruturaCod);
        const estruturaNome = estruturaObj?.nome || 'TODAS AS ESTRUTURAS';
        const pdfTitle = 'Relatorio de Performance da Estrutura';

        setGeneratingPdf('ESTRUTURA');

        try {
            let url = `/api/resumo?empresa=${empresa}&obra=${obra}`;
            if (estruturaCod) {
                url += `&estrutura=${estruturaCod}`;
            }
            if (startDate) {
                url += `&data_inicio=${startDate}`;
            }
            if (endDate) {
                url += `&data_fim=${endDate}`;
            }

            const response = await fetch(url);
            if (!response.ok) throw new Error('Erro ao carregar dados');
            const result = await response.json();
            if (!result?.data || result.data.length === 0) {
                alert('Nenhuma venda encontrada para os filtros selecionados');
                return;
            }

            const vendasEstrutura = result.data;

            const { jsPDF } = await import('jspdf');
            const autoTable = (await import('jspdf-autotable')).default;

            const obraNome = result.obraNome || `${empresa} - ${obra}`;

            // Cores
            const blue = [0, 137, 214];
            const green = [34, 197, 94];
            const red = [220, 38, 38];
            const orange = [245, 158, 11];
            const gray = [100, 100, 100];
            const darkGray = [40, 40, 40];

            // Helper formatters
            const fmt = (n: number) => n.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
            const fmtDate = (d: string) => {
                if (!d) return '';
                const parts = d.split('-');
                if (parts.length === 3) return `${parts[2]}/${parts[1]}/${parts[0]}`;
                return d;
            };

            // Totais
            const totalVendas = vendasEstrutura.length;
            const valorTotalVendas = vendasEstrutura.reduce((sum: number, v: any) => sum + (v.valorTotal || 0), 0);
            const sinaisAbertos = vendasEstrutura.reduce((sum: number, v: any) => sum + (v.sinaisAberto || 0), 0);
            const valorPendente = vendasEstrutura.reduce((sum: number, v: any) => sum + (v.valorSinaisAberto || 0), 0);
            const sinaisPagos = vendasEstrutura.reduce((sum: number, v: any) => sum + (v.sinaisPagos || 0), 0);
            const valorRecebido = vendasEstrutura.reduce((sum: number, v: any) => sum + (v.valorSinaisPagos || 0), 0);
            const sinaisVencidos = vendasEstrutura.reduce((sum: number, v: any) => sum + (v.sinaisVencidos || 0), 0);
            const valorVencido = vendasEstrutura.reduce((sum: number, v: any) => sum + (v.valorSinaisVencidos || 0), 0);


            // PDF Setup
            const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });
            const pageWidth = 210;
            const pageHeight = 297;

            // ========== HEADER ==========
            // Fundo branco para logo
            doc.setFillColor(255, 255, 255);
            doc.rect(0, 0, pageWidth, 40, 'F');

            // Barra azul no topo
            doc.setFillColor(blue[0], blue[1], blue[2]);
            doc.rect(0, 0, pageWidth, 3, 'F');

            // Header (Logo e Títulos)
            try {
                const logoImg = new Image();
                logoImg.src = '/logoprime.png';
                await new Promise((resolve) => {
                    logoImg.onload = resolve;
                    logoImg.onerror = resolve;
                });
                if (logoImg.complete && logoImg.naturalWidth > 0) {
                    const logoHeight = 28;
                    const aspectRatio = logoImg.naturalWidth / logoImg.naturalHeight;
                    const logoWidth = logoHeight * aspectRatio;
                    doc.addImage(logoImg, 'PNG', 10, 7, logoWidth, logoHeight);
                }
            } catch (e) {
                doc.setTextColor(blue[0], blue[1], blue[2]);
                doc.setFontSize(14);
                doc.setFont('helvetica', 'bold');
                doc.text('VALLEPRIME', 10, 25);
            }

            // Nome Obra
            doc.setTextColor(blue[0], blue[1], blue[2]);
            doc.setFontSize(11);
            doc.setFont('helvetica', 'bold');
            doc.text(obraNome, 70, 10);

            // Subtitulo
            doc.setTextColor(darkGray[0], darkGray[1], darkGray[2]);
            doc.setFontSize(9);
            doc.setFont('helvetica', 'normal');
            doc.text(pdfTitle, 70, 18);

            // Nome Estrutura (Destaque)
            doc.setFontSize(12);
            doc.setFont('helvetica', 'bold');
            doc.text(estruturaNome, 70, 27);

            // Data emissão a direita
            doc.setTextColor(darkGray[0], darkGray[1], darkGray[2]);
            doc.setFontSize(9);
            doc.text(new Date().toLocaleDateString('pt-BR', { day: '2-digit', month: 'long', year: 'numeric' }), pageWidth - 15, 10, { align: 'right' });

            // Periodo
            if (startDate || endDate) {
                doc.setFontSize(8);
                doc.setFont('helvetica', 'normal');
                doc.setTextColor(gray[0], gray[1], gray[2]);
                doc.text(`Periodo: ${fmtDate(startDate) || 'Inicio'} a ${fmtDate(endDate) || 'Hoje'}`, pageWidth - 15, 18, { align: 'right' });
            }

            // Estrutura info rodape do header
            if (estruturaObj) {
                doc.setFontSize(8);
                doc.setTextColor(blue[0], blue[1], blue[2]);
                doc.text(`Estrutura: ${estruturaNome} | Empresa: ${empresa}`, 70, 40);
            }

            // Linha separadora
            doc.setDrawColor(220, 220, 220);
            doc.line(10, 42, pageWidth - 10, 42);

            // ========== RESUMO DE PERFORMANCE ==========
            let y = 50;
            doc.setTextColor(darkGray[0], darkGray[1], darkGray[2]);
            doc.setFontSize(11);
            doc.setFont('helvetica', 'bold');
            doc.text('RESUMO GERAL', 15, y);
            y += 8;

            const boxW = 88;
            const boxH = 28;
            const gap = 4;

            const drawMetricBox = (x: number, yPos: number, label: string, value: string, subLabel: string, color: number[]) => {
                doc.setFillColor(250, 250, 250);
                doc.roundedRect(x, yPos, boxW, boxH, 3, 3, 'F');
                doc.setFillColor(color[0], color[1], color[2]);
                doc.rect(x, yPos, 3, boxH, 'F');
                doc.setTextColor(gray[0], gray[1], gray[2]);
                doc.setFontSize(8);
                doc.setFont('helvetica', 'normal');
                doc.text(label, x + 8, yPos + 8);
                doc.setTextColor(darkGray[0], darkGray[1], darkGray[2]);
                doc.setFontSize(14);
                doc.setFont('helvetica', 'bold');
                doc.text(value, x + 8, yPos + 18);
                doc.setTextColor(color[0], color[1], color[2]);
                doc.setFontSize(8);
                doc.setFont('helvetica', 'normal');
                doc.text(subLabel, x + 8, yPos + 24);
            };

            // Linha 1
            drawMetricBox(15, y, 'TOTAL DE VENDAS', totalVendas.toString(), fmt(valorTotalVendas), blue);
            drawMetricBox(15 + boxW + gap, y, 'VALOR RECEBIDO', fmt(valorRecebido), `${sinaisPagos} sinais pagos`, green);
            y += boxH + gap;
            // Linha 2
            drawMetricBox(15, y, 'VALOR PENDENTE', fmt(valorPendente), `${sinaisAbertos} sinais abertos`, orange);
            drawMetricBox(15 + boxW + gap, y, 'VENCIDOS', fmt(valorVencido), sinaisVencidos > 0 ? `${sinaisVencidos} sinais vencidos` : 'Nenhum vencido', red);
            y += boxH + 12;

            // ========== RESUMO POR CORRETOR ==========
            doc.setDrawColor(220, 220, 220);
            doc.line(15, y, pageWidth - 15, y);
            y += 6;
            doc.setTextColor(darkGray[0], darkGray[1], darkGray[2]);
            doc.setFontSize(11);
            doc.setFont('helvetica', 'bold');
            doc.text(`RESUMO POR CORRETOR`, 15, y);
            y += 6;

            // Agrupar dados por corretor para o resumo
            const resumoCorretores: any = {};
            vendasEstrutura.forEach((v: any) => {
                const fullName = (v.corretor || 'Não informado').trim();
                const parts = fullName.split(/\s+/);
                const nome = parts.length > 1 ? `${parts[0]} ${parts[parts.length - 1]}` : parts[0];

                if (!resumoCorretores[nome]) {
                    resumoCorretores[nome] = {
                        nome,
                        vendas: 0,
                        valorTotal: 0,
                        recebido: 0,
                        pendente: 0
                    };
                }
                resumoCorretores[nome].vendas += 1;
                resumoCorretores[nome].valorTotal += (v.valorTotal || 0);
                resumoCorretores[nome].recebido += (v.valorSinaisPagos || 0);
                resumoCorretores[nome].pendente += (v.valorSinaisAberto || 0);
            });

            const resumoRows = Object.values(resumoCorretores)
                .sort((a: any, b: any) => b.valorTotal - a.valorTotal)
                .map((r: any) => [
                    r.nome,
                    r.vendas,
                    fmt(r.valorTotal),
                    fmt(r.recebido),
                    fmt(r.pendente)
                ]);

            autoTable(doc, {
                startY: y,
                margin: { left: 10, right: 10 },
                tableWidth: 'auto',
                head: [['Corretor', 'Qtd Vendas', 'Valor Total', 'Valor Recebido', 'Valor Pendente']],
                body: resumoRows,
                theme: 'striped',
                headStyles: {
                    fillColor: [100, 100, 100], // Cinza para diferenciar
                    textColor: [255, 255, 255],
                    fontStyle: 'bold',
                    fontSize: 8,
                    halign: 'center'
                },
                bodyStyles: {
                    fontSize: 8,
                    textColor: darkGray as any
                },
                columnStyles: {
                    0: { cellWidth: 'auto' },
                    1: { cellWidth: 25, halign: 'center' },
                    2: { cellWidth: 35, halign: 'right' },
                    3: { cellWidth: 35, halign: 'right' },
                    4: { cellWidth: 35, halign: 'right' }
                }
            });

            y = (doc as any).lastAutoTable.finalY + 10;

            // Lista de Vendas
            doc.setDrawColor(220, 220, 220);
            doc.line(15, y, pageWidth - 15, y);
            y += 6;
            doc.setTextColor(darkGray[0], darkGray[1], darkGray[2]);
            doc.setFontSize(11);
            doc.setFont('helvetica', 'bold');
            doc.text(`DETALHAMENTO DE VENDAS COMPLETO`, 15, y);
            y += 6;

            const tableData = vendasEstrutura.map((v: any) => {
                const { quadra, lote } = parseQuadraLote(v.identificador);
                const fullName = (v.corretor || '-').trim();
                const parts = fullName.split(/\s+/);
                const shortName = parts.length > 1 ? `${parts[0]} ${parts[parts.length - 1]}` : parts[0];

                return {
                    venda: v.venda || '-',
                    corretor: shortName, // Primeiro e Ultimo nome
                    cliente: (v.cliente || '-'), // Sem substring fixa para usar auto
                    ql: `${quadra}/${lote}`,
                    dataVenda: v.dataVenda || '-',
                    valorTotal: v.valorTotal || 0,
                    sTotal: (v.sinaisAberto || 0) + (v.sinaisPagos || 0),
                    sPagos: v.sinaisPagos || 0,
                    sVenc: v.sinaisVencidos || 0,
                    sPend: v.sinaisAberto || 0,
                    valorRec: v.valorSinaisPagos || 0
                };
            });

            // Ordenar por Corretor depois Data
            tableData.sort((a: any, b: any) => {
                if (a.corretor < b.corretor) return -1;
                if (a.corretor > b.corretor) return 1;
                return 0;
            });

            const bodyRows = tableData.map((r: any) => [
                r.venda,
                r.corretor,
                r.cliente,
                r.ql,
                r.dataVenda,
                fmt(r.valorTotal),
                //r.sTotal,
                r.sPagos,
                r.sVenc,
                r.sPend,
                fmt(r.valorRec)
            ]);

            // Totais Row - Calcular somas
            const tValorVendas = tableData.reduce((s: number, r: any) => s + r.valorTotal, 0);
            const tSinaisPagos = tableData.reduce((s: number, r: any) => s + r.sPagos, 0);
            const tSinaisVenc = tableData.reduce((s: number, r: any) => s + r.sVenc, 0);
            const tSinaisPend = tableData.reduce((s: number, r: any) => s + r.sPend, 0);
            const tValorRec = tableData.reduce((s: number, r: any) => s + r.valorRec, 0);

            const totalsRow = [
                'TOTAL',
                '',
                `${tableData.length} vendas`,
                '',
                '',
                fmt(tValorVendas),
                tSinaisPagos,
                tSinaisVenc,
                tSinaisPend,
                fmt(tValorRec)
            ];
            bodyRows.push(totalsRow);
            const totalsRowIndex = bodyRows.length - 1;

            autoTable(doc, {
                startY: y,
                margin: { left: 10, right: 10, bottom: 20 },
                tableWidth: 'auto',
                // Corretor column added
                head: [['#', 'Corretor', 'Cliente', 'Q/L', 'Data', 'Venda', 'Pg', 'Vc', 'Pd', 'Recebido']],
                body: bodyRows,
                theme: 'striped',
                headStyles: {
                    fillColor: [0, 137, 214],
                    textColor: [255, 255, 255],
                    fontStyle: 'bold',
                    fontSize: 6.5,
                    cellPadding: 1.5,
                    halign: 'center'
                },
                bodyStyles: {
                    fontSize: 6.5,
                    cellPadding: 1.5,
                    textColor: darkGray as any
                },
                alternateRowStyles: {
                    fillColor: [248, 248, 248]
                },
                columnStyles: {
                    0: { cellWidth: 10, halign: 'center' },
                    1: { cellWidth: 30 }, // Corretor (reduzido de 35)
                    2: { cellWidth: 'auto' }, // Cliente
                    3: { cellWidth: 12, halign: 'center' },
                    4: { cellWidth: 16, halign: 'center' },
                    5: { cellWidth: 24, halign: 'right' }, // Venda (aumentado de 20 para caber R$)
                    6: { cellWidth: 8, halign: 'center' },
                    7: { cellWidth: 8, halign: 'center' },
                    8: { cellWidth: 8, halign: 'center' },
                    9: { cellWidth: 24, halign: 'right' }  // Recebido (aumentado de 20 para caber R$)
                },
                didParseCell: (data: any) => {
                    if (data.section === 'body') {
                        // Linha de totais
                        if (data.row.index === totalsRowIndex) {
                            data.cell.styles.fillColor = [0, 137, 214];
                            data.cell.styles.textColor = [255, 255, 255];
                            data.cell.styles.fontStyle = 'bold';

                            // Mesclar colunas 0 e 1 para o texto "TOTAL"
                            if (data.column.index === 0) {
                                data.cell.colSpan = 2;
                                data.cell.styles.halign = 'center';
                            }
                            return;
                        }

                        const row = tableData[data.row.index];
                        if (!row) return;

                        // Pagos em verde (index 6)
                        if (data.column.index === 6 && row.sPagos > 0) {
                            data.cell.styles.textColor = green as any;
                            data.cell.styles.fontStyle = 'bold';
                        }
                        // Vencidos em vermelho (index 7)
                        if (data.column.index === 7 && row.sVenc > 0) {
                            data.cell.styles.textColor = red as any;
                            data.cell.styles.fontStyle = 'bold';
                        }
                        // Pendentes em laranja (index 8)
                        if (data.column.index === 8 && row.sPend > 0) {
                            data.cell.styles.textColor = orange as any;
                            data.cell.styles.fontStyle = 'bold';
                        }
                        // Valor recebido em verde (index 9)
                        if (data.column.index === 9 && row.valorRec > 0) {
                            data.cell.styles.textColor = green as any;
                        }
                    }
                },
                didDrawPage: (data: any) => {
                    const pageCount = doc.internal.pages.length - 1;
                    // Footer da pagina - Mesmo estilo do relatório de corretor
                    doc.setDrawColor(220, 220, 220);
                    doc.line(10, pageHeight - 12, pageWidth - 10, pageHeight - 12);
                    doc.setFontSize(7);
                    doc.setTextColor(gray[0], gray[1], gray[2]);
                    doc.text('VallePrime - Sistema de Gestao de Vendas', 10, pageHeight - 6);
                    doc.text(`Pagina ${data.pageNumber}/${pageCount}`, pageWidth / 2, pageHeight - 6, { align: 'center' });
                    doc.text('Desenvolvido por Vinicius Dev', pageWidth - 10, pageHeight - 6, { align: 'right' });
                }
            });

            window.open(doc.output('bloburl'), '_blank');
        } catch (err) {
            console.error('Erro ao gerar PDF:', err);
            alert('Erro ao gerar PDF. Tente novamente.');
        } finally {
            setGeneratingPdf(null);
        }
    };

    const generateSimplesPdf = async () => {
        setGeneratingPdf('SIMPLES');
        try {
            // Dynamic imports
            const { jsPDF } = await import('jspdf');
            const autoTable = (await import('jspdf-autotable')).default;

            // Reutilizar lógica de busca de dados com filtros no backend
            let url = `/api/resumo?empresa=${empresa}&obra=${obra}`;
            if (selectedEstrutura) {
                url += `&estrutura=${selectedEstrutura}`;
            }
            if (startDate) {
                url += `&data_inicio=${startDate}`;
            }
            if (endDate) {
                url += `&data_fim=${endDate}`;
            }

            const response = await fetch(url);
            if (!response.ok) throw new Error('Erro ao carregar dados');
            const result = await response.json();

            // Backend já retorna filtrado
            const vendasFiltradas = result.data || [];
            // Obter nome da obra da resposta ou fallback
            const obraNome = result.obraNome || `${empresa} - ${obra}`;

            // Obter nome da estrutura para o header
            let estruturaNome = '';
            if (selectedEstrutura) {
                const estv = estruturas.find(e => e.codigo.toString() === selectedEstrutura);
                estruturaNome = estv ? estv.nome : '';
            }

            // --- CÁLCULOS DE RESUMO ---
            const totalVendasGeral = vendasFiltradas.length;
            const valorTotalGeral = vendasFiltradas.reduce((acc: number, v: any) => acc + (v.valorTotal || 0), 0);

            // Agrupar por corretor
            const resumoCorretoresMap = new Map<string, { qtd: number, valor: number }>();
            vendasFiltradas.forEach((v: any) => {
                const nome = v.corretor || 'Indefinido';
                const atual = resumoCorretoresMap.get(nome) || { qtd: 0, valor: 0 };
                atual.qtd += 1;
                atual.valor += (v.valorTotal || 0);
                resumoCorretoresMap.set(nome, atual);
            });

            const resumoCorretores = Array.from(resumoCorretoresMap.entries()).map(([nome, dados]) => ({
                corretor: nome,
                qtd: dados.qtd,
                valor: dados.valor
            })).sort((a, b) => b.qtd - a.qtd); // Ordenar por qtd

            const doc = new jsPDF();
            const pageWidth = doc.internal.pageSize.getWidth();
            const pageHeight = doc.internal.pageSize.getHeight();

            // --- HEADER PADRÃO ---
            doc.setFillColor(0, 137, 214); // Azul Valle
            doc.rect(0, 0, pageWidth, 3, 'F');

            const logoUrl = '/logoprime.png';
            try {
                const img = new Image();
                img.src = logoUrl;
                await new Promise((resolve, reject) => {
                    img.onload = resolve;
                    img.onerror = reject;
                });
                const imgWidth = 40;
                const imgHeight = (img.height * imgWidth) / img.width;
                doc.addImage(img, 'PNG', 15, 10, imgWidth, imgHeight);
            } catch (e) {
                // Fallback
            }

            doc.setFont('helvetica', 'bold');
            doc.setFontSize(14);
            doc.setTextColor(0, 137, 214);
            doc.text(obraNome.toUpperCase(), 70, 10);

            doc.setFontSize(10);
            doc.setTextColor(100, 100, 100);
            doc.text('RELATÓRIO DE VENDAS SIMPLES', 70, 18);

            doc.setFontSize(11);
            doc.setTextColor(0, 0, 0);
            if (estruturaNome) {
                doc.setFont('helvetica', 'bold');
                doc.text(estruturaNome.toUpperCase(), 70, 27);
            } else {
                doc.text('GERAL', 70, 27);
            }

            doc.setFontSize(9);
            doc.setFont('helvetica', 'normal');
            doc.setTextColor(100, 100, 100);
            const hoje = new Date().toLocaleDateString('pt-BR');
            doc.text(`Emissão: ${hoje}`, pageWidth - 15, 10, { align: 'right' });

            if (startDate && endDate) {
                const pStart = new Date(startDate + 'T12:00:00').toLocaleDateString('pt-BR');
                const pEnd = new Date(endDate + 'T12:00:00').toLocaleDateString('pt-BR');
                doc.text(`Período: ${pStart} a ${pEnd}`, pageWidth - 15, 15, { align: 'right' });
            }

            doc.setDrawColor(200, 200, 200);
            doc.line(15, 45, pageWidth - 15, 45);

            let y = 50;

            // --- RESUMO GERAL ---
            doc.setFontSize(10);
            doc.setTextColor(0, 0, 0);
            doc.setFont('helvetica', 'bold');
            doc.text('RESUMO GERAL', 15, y);
            y += 5;

            doc.setFontSize(9);
            doc.setFont('helvetica', 'normal');
            doc.text(`Total de Vendas: ${totalVendasGeral}`, 15, y);
            doc.text(`Valor Total Vendas: ${valorTotalGeral.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })}`, 80, y);
            y += 10;

            // --- TABELA RESUMO POR CORRETOR ---
            doc.setFont('helvetica', 'bold');
            doc.setFontSize(10);
            doc.text('RESUMO POR CORRETOR', 15, y);
            y += 2;

            // --- CORES POR CORRETOR ---
            const pastelColors = [
                [220, 252, 231], // Green 100
                [219, 234, 254], // Blue 100
                [254, 249, 195], // Yellow 100
                [253, 230, 138], // Amber 200
                [229, 231, 235], // Gray 200
                [254, 226, 226], // Red 100
                [224, 231, 255], // Indigo 100
                [255, 237, 213], // Orange 100
                [243, 232, 255], // Purple 100
                [252, 231, 243], // Pink 100
            ];

            const corretorColorMap = new Map<string, number[]>();
            resumoCorretores.forEach((r, index) => {
                const color = pastelColors[index % pastelColors.length];
                corretorColorMap.set(r.corretor, color);
            });

            const resumoTableData = resumoCorretores.map(r => {
                // Short name logic
                const parts = r.corretor.trim().split(/\s+/);
                const shortName = parts.length > 1 ? `${parts[0]} ${parts[parts.length - 1]}` : parts[0];
                return [
                    shortName,
                    r.qtd.toString(),
                    r.valor.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })
                ];
            });

            autoTable(doc, {
                startY: y,
                margin: { left: 15, right: 15 },
                head: [['Corretor', 'Qtd', 'Valor Total']],
                body: resumoTableData,
                theme: 'grid', // Switch to grid to show colors better
                headStyles: {
                    fillColor: [0, 137, 214],
                    textColor: [255, 255, 255],
                    fontStyle: 'bold',
                    fontSize: 9,
                    halign: 'center'
                },
                bodyStyles: {
                    fontSize: 8,
                    textColor: [50, 50, 50]
                },
                columnStyles: {
                    0: { halign: 'left' },
                    1: { halign: 'center', cellWidth: 20 },
                    2: { halign: 'right', cellWidth: 40 }
                },
                didParseCell: (data: any) => {
                    if (data.section === 'body') {
                        // Find full name from short name matches or mapped index
                        // Since summary table order matches resumoCorretores order:
                        const rowIndex = data.row.index;
                        if (rowIndex < resumoCorretores.length) {
                            const cor = corretorColorMap.get(resumoCorretores[rowIndex].corretor);
                            if (cor) {
                                data.cell.styles.fillColor = cor;
                            }
                        }
                    }
                }
            });

            y = (doc as any).lastAutoTable.finalY + 10;

            // --- TABELA DETALHADA ---
            doc.setFont('helvetica', 'bold');
            doc.setFontSize(10);
            doc.setTextColor(0, 0, 0);
            doc.text('DETALHAMENTO DE VENDAS', 15, y);
            y += 2;

            const tableData = vendasFiltradas.map((v: any) => {
                const { quadra, lote } = parseQuadraLote(v.identificador);

                // Short name logic
                const fullName = (v.corretor || '-').trim();
                const parts = fullName.split(/\s+/);
                const shortName = parts.length > 1 ? `${parts[0]} ${parts[parts.length - 1]}` : parts[0];

                // Fix Data: usar v.dataVenda direto se já for string DD/MM/YYYY, ou formatar se for ISO
                let dataFormatada = v.dataVenda;
                if (v.dataVenda && v.dataVenda.includes('-')) {
                    // Se vier YYYY-MM-DD
                    const parts = v.dataVenda.split('-');
                    if (parts.length === 3) dataFormatada = `${parts[2]}/${parts[1]}/${parts[0]}`;
                }

                return [
                    v.venda || '-',
                    dataFormatada || '-',
                    v.cliente || '-',
                    shortName,
                    `${quadra}/${lote}`,
                    fullName // Hidden column for color mapping
                ];
            });

            // Ordenar por Venda
            tableData.sort((a: any, b: any) => b[0] - a[0]);

            autoTable(doc, {
                startY: y,

                margin: { left: 15, right: 15 },
                head: [['Venda', 'Data', 'Cliente', 'Corretor', 'Q/L']],
                body: tableData.map((r: any[]) => r.slice(0, 5)), // Exclude hidden column from view
                theme: 'grid',
                headStyles: {
                    fillColor: [0, 137, 214], // Azul Valle
                    textColor: [255, 255, 255],
                    fontStyle: 'bold',
                    fontSize: 9,
                    halign: 'center'
                },
                bodyStyles: {
                    fontSize: 8,
                    textColor: [50, 50, 50]
                },
                columnStyles: {
                    0: { halign: 'center', cellWidth: 20 },
                    1: { halign: 'center', cellWidth: 25 },
                    2: { halign: 'left', cellWidth: 'auto' }, // Cliente auto
                    3: { halign: 'left', cellWidth: 40 },
                    4: { halign: 'center', cellWidth: 20 }
                },
                didParseCell: (data: any) => {
                    if (data.section === 'body') {
                        const rowIndex = data.row.index;
                        // Access the hidden full name from the original data array
                        const originalRow = tableData[rowIndex];
                        const fullName = originalRow[5];
                        const cor = corretorColorMap.get(fullName);
                        if (cor) {
                            data.cell.styles.fillColor = cor;
                        }
                    }
                }
            });

            // Footer
            const pageCount = (doc as any).internal.getNumberOfPages();
            for (let i = 1; i <= pageCount; i++) {
                doc.setPage(i);

                // Linha Rodapé
                doc.setDrawColor(200, 200, 200);
                doc.line(15, pageHeight - 15, pageWidth - 15, pageHeight - 15);

                doc.setFontSize(8);
                doc.setTextColor(150, 150, 150);
                doc.text('VallePrime - Sistema de Gestão de Vendas', 15, pageHeight - 10);
                doc.text(`Página ${i} de ${pageCount}`, pageWidth / 2, pageHeight - 10, { align: 'center' });
                doc.text('Desenvolvido por Vinicius Dev', pageWidth - 15, pageHeight - 10, { align: 'right' });
            }

            window.open(doc.output('bloburl'), '_blank');
        } catch (err) {
            console.error('Erro ao gerar PDF Simples:', err);
            alert('Erro. Tente novamente.');
        } finally {
            setGeneratingPdf(null);
        }
    };
    const filteredData = useMemo(() => {
        if (!startDate && !endDate) return data;

        return data.filter(v => {
            // Use dataCadastro for filtering (same as Power BI)
            const dateStr = (v as any).dataCadastro || v.dataVenda;
            if (!dateStr) return false;
            const parts = dateStr.split('/');
            if (parts.length !== 3) return false;
            const vendaDate = new Date(parseInt(parts[2]), parseInt(parts[1]) - 1, parseInt(parts[0]));
            vendaDate.setHours(0, 0, 0, 0);

            if (startDate) {
                // startDate format from input is YYYY-MM-DD
                const startParts = startDate.split('-');
                const start = new Date(parseInt(startParts[0]), parseInt(startParts[1]) - 1, parseInt(startParts[2]));
                start.setHours(0, 0, 0, 0);
                if (vendaDate < start) return false;
            }
            if (endDate) {
                const endParts = endDate.split('-');
                const end = new Date(parseInt(endParts[0]), parseInt(endParts[1]) - 1, parseInt(endParts[2]));
                end.setHours(23, 59, 59, 999);
                if (vendaDate > end) return false;
            }
            return true;
        });
    }, [data, startDate, endDate]);

    // Convert aggregated data directly to stats format
    const corretoresStats = useMemo(() => {
        // If data is from aggregated endpoint, use it directly
        if (data.length > 0 && (data[0] as any)._aggregated) {
            const stats = data.map((item: any) => ({
                nome: item.corretor,
                totalVendas: item._totalVendas || 0,
                valorTotal: item._valorTotal || 0,
                comBoleto: item._comBoleto || 0,
                semBoleto: (item._totalVendas || 0) - (item._comBoleto || 0),
                sinaisAbertos: item._sinaisAbertos || 0,
                valorSinaisAberto: item._valorSinaisAberto || 0,
                sinaisPagos: item._sinaisPagos || 0,
                valorSinaisPagos: item._valorSinaisPagos || 0,
                sinaisVencidos: item._sinaisVencidos || 0,
                valorSinaisVencidos: item._valorSinaisVencidos || 0
            }));

            if (sortBy === 'vendas') {
                stats.sort((a, b) => b.totalVendas - a.totalVendas);
            } else {
                stats.sort((a, b) => b.valorTotal - a.valorTotal);
            }
            return stats;
        }

        // Legacy code for old data format (keeping for compatibility)
        const statsMap = new Map<string, CorretorStats>();

        filteredData.forEach(venda => {
            const corretor = venda.corretor || 'Não informado';
            const existing = statsMap.get(corretor) || {
                nome: corretor,
                totalVendas: 0,
                valorTotal: 0,
                comBoleto: 0,
                semBoleto: 0,
                sinaisAbertos: 0,
                valorSinaisAberto: 0,
                sinaisPagos: 0,
                valorSinaisPagos: 0,
                sinaisVencidos: 0,
                valorSinaisVencidos: 0
            };

            existing.totalVendas++;
            existing.valorTotal += venda.valorTotal || 0;
            if (venda.boletoGerado) {
                existing.comBoleto++;
            } else if (!(venda.sinaisTotal > 0 && venda.sinaisAberto === 0)) {
                existing.semBoleto++;
            }
            existing.sinaisAbertos += venda.sinaisAberto;
            existing.valorSinaisAberto += (venda as any).valorSinaisAberto || 0;
            existing.sinaisPagos += venda.sinaisPagos || 0;
            existing.valorSinaisPagos += (venda as any).valorSinaisPagos || 0;
            existing.sinaisVencidos += (venda as any).sinaisVencidos || 0;

            statsMap.set(corretor, existing);
        });

        const stats = Array.from(statsMap.values());

        if (sortBy === 'vendas') {
            stats.sort((a, b) => {
                if (b.totalVendas !== a.totalVendas) {
                    return b.totalVendas - a.totalVendas;
                }
                return b.valorTotal - a.valorTotal;
            });
        } else {
            stats.sort((a, b) => b.valorTotal - a.valorTotal);
        }

        return stats;
    }, [data, filteredData, sortBy]);

    // Filter stats by search term
    const filteredStats = useMemo(() => {
        if (!searchTerm) return corretoresStats;
        const lowerTerm = searchTerm.toLowerCase();
        return corretoresStats.filter(c => c.nome.toLowerCase().includes(lowerTerm));
    }, [corretoresStats, searchTerm]);

    // Summary metrics (update to use filteredStats)
    const totalCorretores = filteredStats.length;
    const totalVendas = filteredStats.reduce((sum, c) => sum + c.totalVendas, 0);
    const valorTotalGeral = filteredStats.reduce((sum, c) => sum + c.valorTotal, 0);
    const mediaVendasPorCorretor = totalCorretores > 0 ? (totalVendas / totalCorretores).toFixed(1) : '0';

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
                <p style={{ color: '#991B1B' }}>❌ {error}</p>
            </div>
        );
    }

    return (
        <div className="animate-fade-in">
            <div className="page-header">
                <div>
                    <h1 className="page-title">Estatísticas por Corretor</h1>
                    <p className="page-subtitle">Análise de desempenho dos corretores</p>
                </div>
            </div>

            {/* Filters */}
            <div className="filter-bar" style={{ marginBottom: '24px', flexWrap: 'wrap' }}>
                <div className="filter-group" style={{ flexGrow: 1, minWidth: '250px' }}>
                    <label className="filter-label">Buscar Corretor</label>
                    <div style={{ position: 'relative' }}>
                        <span style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#9CA3AF' }}>🔍</span>
                        <input
                            type="text"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            placeholder="Nome do corretor..."
                            className="filter-input"
                            style={{ width: '100%', paddingLeft: '36px' }}
                        />
                    </div>
                </div>
                <div className="filter-group">
                    <label className="filter-label">Data Início</label>
                    <input
                        type="date"
                        value={startDate}
                        onChange={(e) => setStartDate(e.target.value)}
                        className="filter-input"
                        style={{ width: '150px' }}
                    />
                </div>
                <div className="filter-group">
                    <label className="filter-label">Data Fim</label>
                    <input
                        type="date"
                        value={endDate}
                        onChange={(e) => setEndDate(e.target.value)}
                        className="filter-input"
                        style={{ width: '150px' }}
                    />
                </div>
                <div className="filter-group">
                    <label className="filter-label">Estrutura/Equipe</label>
                    <select
                        value={selectedEstrutura}
                        onChange={(e) => setSelectedEstrutura(e.target.value)}
                        className="filter-input"
                        style={{ width: '200px' }}
                    >
                        <option value="">Todas as Estruturas</option>
                        {estruturas.map((est) => (
                            <option key={est.codigo} value={est.codigo}>
                                {est.nome}
                            </option>
                        ))}
                    </select>
                </div>
                <div className="filter-group">
                    <label className="filter-label">Ordenar por</label>
                    <select
                        value={sortBy}
                        onChange={(e) => setSortBy(e.target.value as 'vendas' | 'valor')}
                        className="filter-input"
                        style={{ width: '150px' }}
                    >
                        <option value="vendas">Mais Vendas</option>
                        <option value="valor">Maior Valor</option>
                    </select>
                </div>
                <button onClick={loadData} className="btn btn-primary" style={{ height: '38px', alignSelf: 'flex-end', marginBottom: '1px' }}>
                    🔍 Buscar
                </button>
                <button
                    onClick={generateEstruturaPdf}
                    className="btn btn-secondary"
                    style={{
                        height: '38px',
                        alignSelf: 'flex-end',
                        marginBottom: '1px',
                        backgroundColor: '#FFF',
                        border: '1px solid #D1D5DB',
                        color: '#374151',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px'
                    }}
                    disabled={!!generatingPdf}
                >
                    {generatingPdf === 'ESTRUTURA' ? '⏳' : '📄'}
                    {selectedEstrutura ? 'PDF da Estrutura' : 'PDF Geral'}
                </button>
                <button
                    onClick={generateSimplesPdf}
                    className="btn btn-secondary"
                    style={{
                        height: '38px',
                        alignSelf: 'flex-end',
                        marginBottom: '1px',
                        backgroundColor: '#FFF',
                        border: '1px solid #D1D5DB',
                        color: '#374151',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '6px'
                    }}
                    disabled={!!generatingPdf}
                >
                    {generatingPdf === 'SIMPLES' ? '⏳' : '📑'}
                    Relatório Simples
                </button>
                <button
                    onClick={() => {
                        setStartDate('');
                        setEndDate('');
                        setSearchTerm('');
                    }}
                    className="btn btn-outline"
                    title="Limpar filtros"
                >
                    ✕
                </button>
            </div>

            {/* Empty state - no data loaded yet */}
            {data.length === 0 && !loading && !error && (
                <div className="card" style={{ textAlign: 'center', padding: '60px 20px', marginBottom: '24px' }}>
                    <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔍</div>
                    <h3 style={{ color: '#374151', marginBottom: '8px' }}>Selecione a Empresa e Obra</h3>
                    <p style={{ color: '#6B7280' }}>Clique em "Buscar" para carregar as estatísticas dos corretores</p>
                </div>
            )}

            {data.length > 0 && (
                <>
                    {/* Summary Cards */}
                    <div className="metric-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)', marginBottom: '24px' }}>
                        <div className="metric-card">
                            <div className="metric-card-icon">👥</div>
                            <div className="metric-card-content">
                                <div className="metric-label">TOTAL DE CORRETORES</div>
                                <div className="metric-value primary">{totalCorretores}</div>
                            </div>
                        </div>
                        <div className="metric-card">
                            <div className="metric-card-icon">📊</div>
                            <div className="metric-card-content">
                                <div className="metric-label">TOTAL DE VENDAS</div>
                                <div className="metric-value">{totalVendas}</div>
                            </div>
                        </div>
                        <div className="metric-card">
                            <div className="metric-card-icon">💰</div>
                            <div className="metric-card-content">
                                <div className="metric-label">VALOR TOTAL</div>
                                <div className="metric-value success">R$ {valorTotalGeral.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</div>
                            </div>
                        </div>
                        <div className="metric-card">
                            <div className="metric-card-icon">📈</div>
                            <div className="metric-card-content">
                                <div className="metric-label">MÉDIA POR CORRETOR</div>
                                <div className="metric-value">{mediaVendasPorCorretor}</div>
                            </div>
                        </div>
                    </div>

                    {/* Ranking Table */}
                    <div className="table-container">
                        <div className="table-header-row">
                            <span className="table-title">🏆 Ranking de Corretores</span>
                            <span className="badge badge-primary">{filteredStats.length} corretores</span>
                        </div>
                        <table style={{ tableLayout: 'fixed', minWidth: '1050px', fontSize: '12px' }}>
                            <thead>
                                <tr style={{ fontSize: '11px' }}>
                                    <th style={{ width: '35px', textAlign: 'center', padding: '8px 4px' }}>#</th>
                                    <th style={{ width: '200px', textAlign: 'left', padding: '8px 4px' }}>Corretor</th>
                                    <th style={{ width: '55px', textAlign: 'center', padding: '8px 4px' }}>Vendas</th>
                                    <th style={{ width: '110px', textAlign: 'right', padding: '8px 4px' }}>Valor Total</th>
                                    <th style={{ width: '60px', textAlign: 'center', padding: '8px 4px' }}>Boleto</th>
                                    <th style={{ width: '55px', textAlign: 'center', padding: '8px 4px' }}>Sem Bol</th>
                                    <th style={{ width: '95px', textAlign: 'right', padding: '8px 4px' }}>Sinais Pago</th>
                                    <th style={{ width: '95px', textAlign: 'right', padding: '8px 4px' }}>Sinais Abert</th>
                                    <th style={{ width: '55px', textAlign: 'center', padding: '8px 4px' }}>Venc.</th>
                                    <th style={{ width: '95px', textAlign: 'right', padding: '8px 4px' }}>Val. Vencido</th>
                                    <th style={{ width: '90px', textAlign: 'center', padding: '8px 4px' }}>Ações</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredStats.map((corretor, index) => (
                                    <tr key={corretor.nome} style={{ fontSize: '11px' }}>
                                        <td style={{ textAlign: 'center', padding: '6px 4px' }}>
                                            {index === 0 ? (
                                                <span style={{ fontSize: '16px' }}>🥇</span>
                                            ) : index === 1 ? (
                                                <span style={{ fontSize: '16px' }}>🥈</span>
                                            ) : index === 2 ? (
                                                <span style={{ fontSize: '16px' }}>🥉</span>
                                            ) : (
                                                <span style={{ color: '#64748B', fontWeight: 500 }}>{index + 1}</span>
                                            )}
                                        </td>
                                        <td style={{ fontWeight: 500, padding: '6px 4px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{corretor.nome}</td>
                                        <td style={{ textAlign: 'center', padding: '6px 4px' }}>
                                            <span className="badge badge-primary" style={{ fontSize: '10px', padding: '2px 5px' }}>{corretor.totalVendas}</span>
                                        </td>
                                        <td style={{ textAlign: 'right', padding: '6px 4px', fontWeight: 500, color: '#10B981', whiteSpace: 'nowrap' }}>
                                            R$ {corretor.valorTotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                                        </td>
                                        <td style={{ textAlign: 'center', padding: '6px 4px' }}>
                                            <span className="badge badge-success" style={{ fontSize: '10px', padding: '2px 5px' }}>{corretor.comBoleto}</span>
                                        </td>
                                        <td style={{ textAlign: 'center', padding: '6px 4px' }}>
                                            {corretor.semBoleto > 0 ? (
                                                <span className="badge badge-danger" style={{ fontSize: '10px', padding: '2px 5px' }}>{corretor.semBoleto}</span>
                                            ) : (
                                                <span style={{ color: '#94A3B8' }}>-</span>
                                            )}
                                        </td>
                                        <td style={{ textAlign: 'right', padding: '6px 4px', fontWeight: 500, color: '#10B981', whiteSpace: 'nowrap' }}>
                                            R$ {corretor.valorSinaisPagos.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                                        </td>
                                        <td style={{ textAlign: 'right', padding: '6px 4px', fontWeight: 500, color: '#F59E0B', whiteSpace: 'nowrap' }}>
                                            R$ {corretor.valorSinaisAberto.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                                        </td>
                                        <td style={{ textAlign: 'center', padding: '6px 4px' }}>
                                            {corretor.sinaisVencidos > 0 ? (
                                                <span className="badge badge-danger" style={{ fontSize: '10px', padding: '2px 5px' }}>{corretor.sinaisVencidos}</span>
                                            ) : (
                                                <span style={{ color: '#94A3B8' }}>-</span>
                                            )}
                                        </td>
                                        <td style={{ textAlign: 'right', padding: '6px 4px', fontWeight: 500, color: '#EF4444', whiteSpace: 'nowrap' }}>
                                            {(corretor.valorSinaisVencidos || 0) > 0 ? (
                                                <>R$ {(corretor.valorSinaisVencidos || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</>
                                            ) : (
                                                <span style={{ color: '#94A3B8' }}>-</span>
                                            )}
                                        </td>
                                        <td style={{ textAlign: 'center', padding: '6px 4px' }}>
                                            <div style={{ display: 'flex', gap: '4px', justifyContent: 'center' }}>
                                                <button
                                                    onClick={() => openCorretorDrawer(corretor, index + 1)}
                                                    className="btn"
                                                    style={{
                                                        padding: '3px 6px',
                                                        fontSize: '10px',
                                                        background: 'linear-gradient(135deg, #6366F1, #4F46E5)',
                                                        color: 'white',
                                                        border: 'none',
                                                        borderRadius: '4px',
                                                        cursor: 'pointer'
                                                    }}
                                                    title="Ver detalhes"
                                                >
                                                    👁️
                                                </button>
                                                <button
                                                    onClick={() => generateCorretorPdf(corretor.nome, corretor)}
                                                    disabled={generatingPdf !== null}
                                                    className="btn btn-outline"
                                                    style={{
                                                        padding: '3px 6px',
                                                        fontSize: '10px',
                                                        minWidth: '35px'
                                                    }}
                                                >
                                                    {generatingPdf === corretor.nome ? '⏳' : '📄'}
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </>
            )}

            {/* Drawer for Corretor Details */}
            {drawerOpen && selectedCorretor && (
                <>
                    {/* Backdrop */}
                    <div
                        onClick={closeDrawer}
                        style={{
                            position: 'fixed',
                            top: 0,
                            left: 0,
                            right: 0,
                            bottom: 0,
                            background: 'rgba(0, 0, 0, 0.5)',
                            zIndex: 998,
                            transition: 'opacity 0.3s'
                        }}
                    />
                    {/* Drawer Panel */}
                    <div
                        style={{
                            position: 'fixed',
                            top: 0,
                            right: 0,
                            width: '500px',
                            height: '100vh',
                            background: 'white',
                            boxShadow: '-4px 0 20px rgba(0,0,0,0.15)',
                            zIndex: 999,
                            display: 'flex',
                            flexDirection: 'column',
                            animation: 'slideIn 0.3s ease-out'
                        }}
                    >
                        {/* Header */}
                        <div style={{
                            padding: '20px 24px',
                            background: 'linear-gradient(135deg, #1E40AF, #3B82F6)',
                            color: 'white'
                        }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <div>
                                    <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 600 }}>Detalhes do Corretor</h2>
                                    <p style={{ margin: '4px 0 0', fontSize: '13px', opacity: 0.9 }}>
                                        Ranking #{(selectedCorretor as any).rank || '-'} • {selectedCorretor.totalVendas} vendas
                                    </p>
                                </div>
                                <button
                                    onClick={closeDrawer}
                                    style={{
                                        background: 'rgba(255,255,255,0.2)',
                                        border: 'none',
                                        borderRadius: '8px',
                                        padding: '8px 12px',
                                        color: 'white',
                                        cursor: 'pointer',
                                        fontSize: '14px'
                                    }}
                                >
                                    ✕ Fechar
                                </button>
                            </div>
                            <div style={{
                                marginTop: '12px',
                                padding: '12px',
                                background: 'rgba(255,255,255,0.15)',
                                borderRadius: '8px'
                            }}>
                                <p style={{ margin: 0, fontSize: '18px', fontWeight: 700 }}>👤 {selectedCorretor.nome}</p>
                            </div>
                        </div>

                        {/* Content */}
                        <div style={{ flex: 1, overflow: 'auto', padding: '20px 24px' }}>
                            {/* KPI Cards */}
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', marginBottom: '20px' }}>
                                <div style={{ padding: '14px', background: '#F0FDF4', borderRadius: '10px', border: '1px solid #BBF7D0' }}>
                                    <p style={{ margin: 0, fontSize: '11px', color: '#166534', fontWeight: 600 }}>SINAIS PAGOS</p>
                                    <p style={{ margin: '4px 0 0', fontSize: '18px', fontWeight: 700, color: '#15803D' }}>
                                        R$ {selectedCorretor.valorSinaisPagos.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                                    </p>
                                </div>
                                <div style={{ padding: '14px', background: '#FEF3C7', borderRadius: '10px', border: '1px solid #FDE68A' }}>
                                    <p style={{ margin: 0, fontSize: '11px', color: '#92400E', fontWeight: 600 }}>SINAIS ABERTOS</p>
                                    <p style={{ margin: '4px 0 0', fontSize: '18px', fontWeight: 700, color: '#B45309' }}>
                                        R$ {selectedCorretor.valorSinaisAberto.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                                    </p>
                                </div>
                                <div style={{ padding: '14px', background: '#FEE2E2', borderRadius: '10px', border: '1px solid #FECACA' }}>
                                    <p style={{ margin: 0, fontSize: '11px', color: '#991B1B', fontWeight: 600 }}>VENCIDOS ({selectedCorretor.sinaisVencidos})</p>
                                    <p style={{ margin: '4px 0 0', fontSize: '18px', fontWeight: 700, color: '#DC2626' }}>
                                        R$ {(selectedCorretor.valorSinaisVencidos || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                                    </p>
                                </div>
                                <div style={{ padding: '14px', background: '#EEF2FF', borderRadius: '10px', border: '1px solid #C7D2FE' }}>
                                    <p style={{ margin: 0, fontSize: '11px', color: '#3730A3', fontWeight: 600 }}>VALOR TOTAL</p>
                                    <p style={{ margin: '4px 0 0', fontSize: '18px', fontWeight: 700, color: '#4338CA' }}>
                                        R$ {selectedCorretor.valorTotal.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                                    </p>
                                </div>
                            </div>

                            {/* Action Buttons */}
                            <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
                                <button
                                    onClick={() => generateCorretorPdf(selectedCorretor.nome)}
                                    disabled={generatingPdf !== null}
                                    style={{
                                        flex: 1,
                                        padding: '12px',
                                        background: 'linear-gradient(135deg, #2563EB, #1D4ED8)',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '8px',
                                        fontSize: '13px',
                                        fontWeight: 600,
                                        cursor: 'pointer',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        gap: '6px'
                                    }}
                                >
                                    {generatingPdf === selectedCorretor.nome ? '⏳ Gerando...' : '📄 Gerar PDF'}
                                </button>
                            </div>

                            {/* Sales List */}
                            <div style={{ borderTop: '1px solid #E5E7EB', paddingTop: '16px' }}>
                                <h3 style={{ margin: '0 0 12px', fontSize: '14px', fontWeight: 600, color: '#374151' }}>
                                    📋 Últimas Vendas ({corretorVendas.length})
                                </h3>
                                {loadingVendas ? (
                                    <div style={{ textAlign: 'center', padding: '20px' }}>
                                        <div className="spinner" style={{ margin: '0 auto' }}></div>
                                    </div>
                                ) : corretorVendas.length === 0 ? (
                                    <p style={{ color: '#6B7280', textAlign: 'center', padding: '20px' }}>Nenhuma venda encontrada</p>
                                ) : (
                                    <div style={{ maxHeight: '300px', overflow: 'auto' }}>
                                        {corretorVendas.slice(0, 20).map((venda, idx) => {
                                            const { quadra, lote } = parseQuadraLote(venda.identificador);
                                            return (
                                                <div
                                                    key={idx}
                                                    style={{
                                                        padding: '12px',
                                                        background: idx % 2 === 0 ? '#F9FAFB' : 'white',
                                                        borderRadius: '6px',
                                                        marginBottom: '6px',
                                                        border: '1px solid #E5E7EB'
                                                    }}
                                                >
                                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                                        <div>
                                                            <p style={{ margin: 0, fontSize: '12px', fontWeight: 600, color: '#1F2937' }}>
                                                                Venda #{venda.venda} • Q{quadra}/L{lote}
                                                            </p>
                                                            <p style={{ margin: '2px 0 0', fontSize: '11px', color: '#6B7280' }}>
                                                                {(venda.cliente || '').substring(0, 35)}{(venda.cliente || '').length > 35 ? '...' : ''}
                                                            </p>
                                                        </div>
                                                        <div style={{ textAlign: 'right' }}>
                                                            <p style={{ margin: 0, fontSize: '12px', fontWeight: 600, color: '#10B981' }}>
                                                                R$ {(venda.valorTotal || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                                                            </p>
                                                            <p style={{ margin: '2px 0 0', fontSize: '10px', color: '#9CA3AF' }}>
                                                                {venda.dataVenda || '-'}
                                                            </p>
                                                        </div>
                                                    </div>
                                                    <div style={{ marginTop: '6px', display: 'flex', gap: '8px' }}>
                                                        <span style={{
                                                            fontSize: '10px',
                                                            padding: '2px 6px',
                                                            borderRadius: '4px',
                                                            background: venda.boletoGerado ? '#D1FAE5' : '#FEE2E2',
                                                            color: venda.boletoGerado ? '#059669' : '#DC2626'
                                                        }}>
                                                            {venda.boletoGerado ? '✓ Boleto' : '✗ Sem Boleto'}
                                                        </span>
                                                        {venda.sinaisAberto > 0 && (
                                                            <span style={{
                                                                fontSize: '10px',
                                                                padding: '2px 6px',
                                                                borderRadius: '4px',
                                                                background: '#FEF3C7',
                                                                color: '#D97706'
                                                            }}>
                                                                {venda.sinaisAberto} sinal aberto
                                                            </span>
                                                        )}
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </>
            )}

            {/* CSS Animation */}
            <style>{`
                @keyframes slideIn {
                    from { transform: translateX(100%); }
                    to { transform: translateX(0); }
                }
            `}</style>
        </div>
    );
};

