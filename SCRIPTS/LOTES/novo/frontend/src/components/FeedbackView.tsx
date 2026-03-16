import React, { useState, useEffect } from 'react';
import { Send, MessageSquare, Trash2, Edit2, X, Check } from 'lucide-react';

interface Feedback {
    id?: string;
    autor: string;
    mensagem: string;
    data: string;
    tipo: string;
}

export const FeedbackView: React.FC = () => {
    const [feedbacks, setFeedbacks] = useState<Feedback[]>([]);
    const [loading, setLoading] = useState(true);
    const [mensagem, setMensagem] = useState('');
    const [autor, setAutor] = useState('');
    const [tipo, setTipo] = useState('Sugestão');
    const [sending, setSending] = useState(false);
    const [editingId, setEditingId] = useState<string | null>(null);

    const loadFeedbacks = async () => {
        try {
            const response = await fetch('/api/feedbacks');
            if (response.ok) {
                const data = await response.json();
                setFeedbacks(data);
            }
        } catch (error) {
            console.error('Erro ao carregar feedbacks:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadFeedbacks();
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!mensagem.trim() || !autor.trim()) return;

        setSending(true);
        try {
            const url = editingId ? `/api/feedbacks/${editingId}` : '/api/feedbacks';
            const method = editingId ? 'PUT' : 'POST';

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    autor,
                    mensagem,
                    tipo
                }),
            });

            if (response.ok) {
                setMensagem('');
                setAutor('');
                setTipo('Sugestão');
                setEditingId(null);
                loadFeedbacks();
            }
        } catch (error) {
            console.error('Erro ao enviar feedback:', error);
        } finally {
            setSending(false);
        }
    };

    const handleDelete = async (id: string) => {
        if (!confirm('Deseja realmente excluir este feedback?')) return;

        try {
            const response = await fetch(`/api/feedbacks/${id}`, {
                method: 'DELETE',
            });
            if (response.ok) {
                loadFeedbacks();
            }
        } catch (error) {
            console.error('Erro ao excluir feedback:', error);
        }
    };

    const handleEdit = (feedback: Feedback) => {
        if (!feedback.id) return;
        setAutor(feedback.autor);
        setMensagem(feedback.mensagem);
        setTipo(feedback.tipo);
        setEditingId(feedback.id);
    };

    const handleCancelEdit = () => {
        setAutor('');
        setMensagem('');
        setTipo('Sugestão');
        setEditingId(null);
    };

    const getTypeColor = (feedbackTipo: string) => {
        switch (feedbackTipo) {
            case 'Erro': return 'bg-red-500';
            case 'Elogio': return 'bg-green-500';
            case 'Sugestão': return 'bg-blue-500';
            default: return 'bg-slate-400';
        }
    };

    const getTypeBadgeStyle = (feedbackTipo: string) => {
        switch (feedbackTipo) {
            case 'Erro': return 'bg-red-50 text-red-600 border border-red-100';
            case 'Elogio': return 'bg-green-50 text-green-600 border border-green-100';
            case 'Sugestão': return 'bg-blue-50 text-blue-600 border border-blue-100';
            default: return 'bg-slate-50 text-slate-600 border border-slate-100';
        }
    };

    return (
        <div style={{ padding: '24px', minHeight: '100vh', background: 'linear-gradient(to bottom right, #f8fafc, #f1f5f9)' }}>
            <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
                <header style={{ display: 'flex', alignItems: 'center', gap: '12px', paddingBottom: '24px', borderBottom: '1px solid #e2e8f0', marginBottom: '32px' }}>
                    <div style={{ background: '#2563eb', padding: '12px', borderRadius: '12px', boxShadow: '0 10px 15px -3px rgba(37, 99, 235, 0.2)' }}>
                        <MessageSquare style={{ width: '32px', height: '32px', color: 'white' }} />
                    </div>
                    <div>
                        <h1 style={{ fontSize: '28px', fontWeight: 'bold', color: '#1e293b', margin: 0 }}>Feedbacks e Sugestões</h1>
                        <p style={{ color: '#64748b', margin: 0 }}>Ajude-nos a melhorar o sistema com sua opinião.</p>
                    </div>
                </header>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '32px' }}>
                    {/* Formulário */}
                    <div style={{ background: 'white', padding: '32px', borderRadius: '16px', boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.1)', border: '1px solid #f1f5f9', height: 'fit-content', position: 'sticky', top: '24px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                            <h2 style={{ fontSize: '20px', fontWeight: 'bold', color: '#334155', margin: 0 }}>
                                {editingId ? 'Editar Feedback' : 'Deixe sua opinião'}
                            </h2>
                            {editingId && (
                                <button onClick={handleCancelEdit} style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', padding: '8px' }}>
                                    <X size={20} />
                                </button>
                            )}
                        </div>

                        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                            <div>
                                <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#475569', marginBottom: '8px' }}>Seu Nome</label>
                                <input
                                    type="text"
                                    value={autor}
                                    onChange={(e) => setAutor(e.target.value)}
                                    style={{ width: '100%', padding: '12px 16px', background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '12px', outline: 'none', fontSize: '14px', boxSizing: 'border-box' }}
                                    placeholder="Ex: João Silva"
                                    required
                                />
                            </div>

                            <div>
                                <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#475569', marginBottom: '8px' }}>Tipo de Mensagem</label>
                                <select
                                    value={tipo}
                                    onChange={(e) => setTipo(e.target.value)}
                                    style={{ width: '100%', padding: '12px 16px', background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '12px', outline: 'none', fontSize: '14px', cursor: 'pointer', boxSizing: 'border-box' }}
                                >
                                    <option value="Sugestão">💡 Sugestão</option>
                                    <option value="Elogio">👏 Elogio</option>
                                    <option value="Erro">⚠️ Relatar Erro</option>
                                    <option value="Outro">📝 Outro</option>
                                </select>
                            </div>

                            <div>
                                <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#475569', marginBottom: '8px' }}>Sua Mensagem</label>
                                <textarea
                                    value={mensagem}
                                    onChange={(e) => setMensagem(e.target.value)}
                                    style={{ width: '100%', padding: '12px 16px', background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '12px', outline: 'none', height: '160px', resize: 'none', fontSize: '14px', boxSizing: 'border-box' }}
                                    placeholder="Descreva detalhadamente sua sugestão ou feedback..."
                                    required
                                />
                            </div>

                            <button
                                type="submit"
                                disabled={sending}
                                style={{
                                    width: '100%',
                                    fontWeight: 'bold',
                                    padding: '14px 16px',
                                    borderRadius: '12px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    gap: '8px',
                                    transition: 'all 0.2s',
                                    boxShadow: editingId ? '0 10px 15px -3px rgba(245, 158, 11, 0.3)' : '0 10px 15px -3px rgba(37, 99, 235, 0.3)',
                                    background: editingId ? '#f59e0b' : '#2563eb',
                                    color: 'white',
                                    border: 'none',
                                    cursor: sending ? 'not-allowed' : 'pointer',
                                    opacity: sending ? 0.5 : 1
                                }}
                            >
                                {editingId ? <Check size={20} /> : <Send size={20} />}
                                {sending ? 'Enviando...' : (editingId ? 'Salvar Alterações' : 'Enviar Feedback')}
                            </button>
                        </form>
                    </div>

                    {/* Lista */}
                    <div>
                        <h2 style={{ fontSize: '20px', fontWeight: 'bold', color: '#334155', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '24px' }}>
                            Feedbacks Recentes
                            <span style={{ fontSize: '14px', fontWeight: 'normal', color: '#94a3b8', background: '#f1f5f9', padding: '4px 12px', borderRadius: '9999px' }}>
                                {feedbacks.length}
                            </span>
                        </h2>

                        {loading ? (
                            <div style={{ display: 'flex', justifyContent: 'center', padding: '48px' }}>
                                <div style={{ width: '40px', height: '40px', border: '4px solid #e2e8f0', borderTopColor: '#2563eb', borderRadius: '50%', animation: 'spin 1s linear infinite' }}></div>
                            </div>
                        ) : feedbacks.length === 0 ? (
                            <div style={{ background: 'white', padding: '48px', borderRadius: '16px', textAlign: 'center', boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)', border: '1px solid #f1f5f9', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px' }}>
                                <div style={{ width: '64px', height: '64px', background: '#f8fafc', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#cbd5e1' }}>
                                    <MessageSquare size={32} />
                                </div>
                                <div>
                                    <p style={{ color: '#64748b', fontWeight: '500', margin: 0 }}>Nenhum feedback registrado ainda.</p>
                                    <p style={{ color: '#94a3b8', fontSize: '14px', margin: '4px 0 0 0' }}>Seja o primeiro a colaborar!</p>
                                </div>
                            </div>
                        ) : (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                                {feedbacks.map((item, index) => (
                                    <div key={item.id || index} style={{ background: 'white', padding: '24px', borderRadius: '16px', boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.05)', border: '1px solid #f1f5f9', position: 'relative', overflow: 'hidden' }}>
                                        {/* Barra lateral colorida */}
                                        <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: '6px' }} className={getTypeColor(item.tipo)}></div>

                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px', paddingLeft: '12px' }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                                <div style={{ width: '40px', height: '40px', background: '#f1f5f9', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#475569', fontWeight: 'bold', boxShadow: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.05)' }}>
                                                    {item.autor.charAt(0).toUpperCase()}
                                                </div>
                                                <div>
                                                    <h3 style={{ fontWeight: 'bold', color: '#1e293b', fontSize: '18px', lineHeight: '1.2', margin: 0 }}>{item.autor}</h3>
                                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '4px' }}>
                                                        <span style={{ fontSize: '10px', textTransform: 'uppercase', letterSpacing: '0.05em', fontWeight: 'bold', padding: '2px 8px', borderRadius: '6px' }} className={getTypeBadgeStyle(item.tipo)}>
                                                            {item.tipo}
                                                        </span>
                                                        <span style={{ fontSize: '12px', color: '#94a3b8', fontWeight: '500' }}>{item.data}</span>
                                                    </div>
                                                </div>
                                            </div>

                                            <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                                                <button
                                                    onClick={() => handleEdit(item)}
                                                    style={{ padding: '8px', color: '#94a3b8', background: 'transparent', border: 'none', borderRadius: '8px', cursor: 'pointer' }}
                                                    title="Editar"
                                                >
                                                    <Edit2 size={18} />
                                                </button>
                                                <button
                                                    onClick={() => item.id && handleDelete(item.id)}
                                                    style={{ padding: '8px', color: '#94a3b8', background: 'transparent', border: 'none', borderRadius: '8px', cursor: 'pointer' }}
                                                    title="Excluir"
                                                >
                                                    <Trash2 size={18} />
                                                </button>
                                            </div>
                                        </div>

                                        <div style={{ paddingLeft: '64px' }}>
                                            <p style={{ color: '#475569', lineHeight: '1.6', whiteSpace: 'pre-wrap', margin: 0 }}>{item.mensagem}</p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};
