import React, { useState } from 'react';
import type { Lote, Empreendimento } from '../../types';
import { FaCalculator, FaCopy, FaCheck, FaTimes } from 'react-icons/fa';
import './OrcamentoModal.css';

interface OrcamentoModalProps {
    lote: Lote | null;
    empreendimento: Empreendimento | null;
    isOpen: boolean;
    onClose: () => void;
}

const OrcamentoModal: React.FC<OrcamentoModalProps> = ({ lote, empreendimento, isOpen, onClose }) => {
    const [isLancamento, setIsLancamento] = useState(false);
    const [numParcelas, setNumParcelas] = useState(36);
    const [copied, setCopied] = useState(false);

    if (!isOpen || !lote || !empreendimento) return null;

    // Extrair valor numérico do lote
    const valorLote = parseFloat(lote.Valor_Terreno.replace(/[^\d,]/g, '').replace(',', '.'));

    // Cálculos
    const sinal = valorLote * 0.05; // 5% de sinal
    const corretagem = valorLote * 0.05; // 5% de corretagem (ajustar se necessário)
    const parcelasCorretagem = isLancamento ? 3 : 5;
    const valorParcelaCorretagem = corretagem / parcelasCorretagem;

    const saldoParcelar = valorLote - sinal;
    const valorParcela = saldoParcelar / numParcelas;

    // Determinar tipo de parcela
    let tipoParcela = '';
    if (numParcelas >= 2 && numParcelas <= 36) {
        tipoParcela = 'Parcelas Fixas';
    } else if (numParcelas >= 37 && numParcelas <= 72) {
        tipoParcela = 'Parcelas Reajustáveis Anualmente';
    } else if (numParcelas >= 73 && numParcelas <= 200) {
        tipoParcela = 'Parcelas Reajustáveis Anualmente';
    }

    // Gerar mensagem
    const gerarMensagem = () => {
        const msg = `🏡 *ORÇAMENTO - ${empreendimento.nome.toUpperCase()}*
📍 ${empreendimento.cidade}/${empreendimento.estado}

*DADOS DO LOTE:*
▫️ Quadra: ${lote.QD}
▫️ Lote: ${lote.LT}
▫️ Área: ${lote.M2} m²
▫️ Logradouro: ${lote.Logradouro}

💰 *VALORES:*
▫️ Valor Total: ${formatarMoeda(valorLote)}

*FORMA DE PAGAMENTO:*

1️⃣ *Sinal (5%):* ${formatarMoeda(sinal)}

2️⃣ *Corretagem:* ${formatarMoeda(corretagem)}
   └ Parcelado em ${parcelasCorretagem}x de ${formatarMoeda(valorParcelaCorretagem)}${isLancamento ? ' (Lançamento)' : ''}

3️⃣ *Saldo a Parcelar:* ${formatarMoeda(saldoParcelar)}
   └ ${numParcelas}x de ${formatarMoeda(valorParcela)}
   └ ${tipoParcela}

📋 *PLANOS DISPONÍVEIS:*
• 2 a 36 parcelas: Fixas
• 37 a 72 parcelas: Reajustáveis
• 73 a 200 parcelas: Reajustáveis

✅ *Status:* ${lote.Status_Terreno}

---
📞 Entre em contato para mais informações!
🏢 Valle Prime Loteamentos`;

        return msg;
    };

    const formatarMoeda = (valor: number): string => {
        return valor.toLocaleString('pt-BR', {
            style: 'currency',
            currency: 'BRL'
        });
    };

    const copiarMensagem = () => {
        const mensagem = gerarMensagem();
        navigator.clipboard.writeText(mensagem).then(() => {
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        });
    };

    return (
        <div className={`orcamento-modal ${isOpen ? 'active' : ''}`} onClick={onClose}>
            <div className="orcamento-content" onClick={(e) => e.stopPropagation()}>
                <button className="orcamento-close" onClick={onClose}>
                    <FaTimes />
                </button>

                <div className="orcamento-header">
                    <FaCalculator />
                    <h2>Gerar Orçamento</h2>
                    <p>Quadra {lote.QD} - Lote {lote.LT}</p>
                </div>

                <div className="orcamento-body">
                    <div className="orcamento-options">
                        <div className="option-group">
                            <label className="option-label">
                                <input
                                    type="checkbox"
                                    checked={isLancamento}
                                    onChange={(e) => setIsLancamento(e.target.checked)}
                                />
                                <span>É lançamento? (Corretagem em 3x)</span>
                            </label>
                        </div>

                        <div className="option-group">
                            <label className="option-label">Número de Parcelas:</label>
                            <select
                                className="option-select"
                                value={numParcelas}
                                onChange={(e) => setNumParcelas(Number(e.target.value))}
                            >
                                <optgroup label="Parcelas Fixas (2-36)">
                                    {[...Array(35)].map((_, i) => (
                                        <option key={i + 2} value={i + 2}>{i + 2}x</option>
                                    ))}
                                </optgroup>
                                <optgroup label="Parcelas Reajustáveis (37-72)">
                                    {[...Array(36)].map((_, i) => (
                                        <option key={i + 37} value={i + 37}>{i + 37}x</option>
                                    ))}
                                </optgroup>
                                <optgroup label="Parcelas Reajustáveis (73-200)">
                                    {[...Array(128)].map((_, i) => (
                                        <option key={i + 73} value={i + 73}>{i + 73}x</option>
                                    ))}
                                </optgroup>
                            </select>
                        </div>
                    </div>

                    <div className="orcamento-preview">
                        <h3>Resumo do Orçamento</h3>
                        <div className="resumo-grid">
                            <div className="resumo-item">
                                <span className="resumo-label">Valor do Lote:</span>
                                <span className="resumo-value">{formatarMoeda(valorLote)}</span>
                            </div>
                            <div className="resumo-item">
                                <span className="resumo-label">Sinal (5%):</span>
                                <span className="resumo-value highlight">{formatarMoeda(sinal)}</span>
                            </div>
                            <div className="resumo-item">
                                <span className="resumo-label">Corretagem:</span>
                                <span className="resumo-value">{parcelasCorretagem}x de {formatarMoeda(valorParcelaCorretagem)}</span>
                            </div>
                            <div className="resumo-item">
                                <span className="resumo-label">Saldo a Parcelar:</span>
                                <span className="resumo-value">{formatarMoeda(saldoParcelar)}</span>
                            </div>
                            <div className="resumo-item">
                                <span className="resumo-label">Parcelas:</span>
                                <span className="resumo-value highlight">{numParcelas}x de {formatarMoeda(valorParcela)}</span>
                            </div>
                            <div className="resumo-item full">
                                <span className="resumo-label">Tipo:</span>
                                <span className="resumo-value">{tipoParcela}</span>
                            </div>
                        </div>
                    </div>

                    <div className="orcamento-message">
                        <h3>Mensagem para o Cliente</h3>
                        <pre className="message-preview">{gerarMensagem()}</pre>
                    </div>
                </div>

                <div className="orcamento-footer">
                    <button className="btn-secondary" onClick={onClose}>
                        Fechar
                    </button>
                    <button
                        className={`btn-copy ${copied ? 'copied' : ''}`}
                        onClick={copiarMensagem}
                    >
                        {copied ? (
                            <>
                                <FaCheck /> Copiado!
                            </>
                        ) : (
                            <>
                                <FaCopy /> Copiar Mensagem
                            </>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default OrcamentoModal;
