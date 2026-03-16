import React, { useState, useEffect } from 'react';
import { Users, Plus, Edit2, Trash2, X, Check, Shield, User, Eye, Clock, Monitor, Circle } from 'lucide-react';

interface UserData {
    id: string;
    username: string;
    nome: string;
    role: string;
    modulos: string[];
}

interface UserForm {
    username: string;
    password: string;
    nome: string;
    role: string;
    modulos: string[];
}

interface PageHistoryEntry {
    page: string;
    pageName: string;
    timestamp: string;
}

interface UserActivity {
    isOnline: boolean;
    lastAccess: string | null;
    lastHeartbeat: string | null;
    pageHistory: PageHistoryEntry[];
}

const MODULOS_DISPONIVEIS = [
    { id: 'loteamento', nome: 'Dashboard Executivo' },
    { id: 'evolucao', nome: 'Evolução' },
    { id: 'boletos', nome: 'Gerenciamento de Boletos' },
    { id: 'recebimentos', nome: 'Recebimentos' },
    { id: 'inadimplentes', nome: 'Inadimplência' },
    { id: 'corretores', nome: 'Corretores' },
    { id: 'relatorio-corretor', nome: 'Relatório Corretor' },
    { id: 'consulta', nome: 'Consultar Venda' },
    { id: 'disponibilidades', nome: 'Disponibilidades' },
    { id: 'contratos', nome: 'Contratos' },
    { id: 'quitacao', nome: 'Termos e Contratos' },
    { id: 'mensagens', nome: 'Mensagens Diárias' },
    { id: 'feedbacks', nome: 'Feedbacks' },
    { id: 'sobre', nome: 'Sobre' },
];

export const AdminView: React.FC = () => {
    const [users, setUsers] = useState<UserData[]>([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [editingId, setEditingId] = useState<string | null>(null);
    const [form, setForm] = useState<UserForm>({ username: '', password: '', nome: '', role: 'user', modulos: [] });
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');

    // Activity modal states
    const [showActivityModal, setShowActivityModal] = useState(false);
    const [selectedUser, setSelectedUser] = useState<UserData | null>(null);
    const [userActivity, setUserActivity] = useState<UserActivity | null>(null);
    const [loadingActivity, setLoadingActivity] = useState(false);

    const loadUserActivity = async (userId: string) => {
        setLoadingActivity(true);
        try {
            const response = await fetch(`/api/users/${userId}/activity`);
            if (response.ok) {
                const data = await response.json();
                setUserActivity(data);
            }
        } catch (err) {
            console.error('Erro ao carregar atividade:', err);
        } finally {
            setLoadingActivity(false);
        }
    };

    const handleViewActivity = (user: UserData) => {
        setSelectedUser(user);
        setShowActivityModal(true);
        loadUserActivity(user.id);
    };

    const formatDateTime = (isoString: string | null) => {
        if (!isoString) return 'Nunca';
        try {
            const date = new Date(isoString);
            return date.toLocaleString('pt-BR');
        } catch {
            return 'Data inválida';
        }
    };

    const formatTimeAgo = (isoString: string | null) => {
        if (!isoString) return 'Nunca';
        try {
            const date = new Date(isoString);
            const now = new Date();
            const diffSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

            if (diffSeconds < 60) return 'Agora mesmo';
            if (diffSeconds < 3600) return `Há ${Math.floor(diffSeconds / 60)} min`;
            if (diffSeconds < 86400) return `Há ${Math.floor(diffSeconds / 3600)} horas`;
            return `Há ${Math.floor(diffSeconds / 86400)} dias`;
        } catch {
            return 'Desconhecido';
        }
    };

    const loadUsers = async () => {
        try {
            const response = await fetch('/api/users');
            if (response.ok) {
                const data = await response.json();
                setUsers(data);
            }
        } catch (err) {
            console.error('Erro ao carregar usuários:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadUsers();
    }, []);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setSaving(true);

        try {
            const url = editingId ? `/api/users/${editingId}` : '/api/users';
            const method = editingId ? 'PUT' : 'POST';

            // Se for admin, dar acesso a tudo
            const modulosToSave = form.role === 'admin' ? ['all'] : form.modulos;

            const response = await fetch(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ...form, modulos: modulosToSave })
            });

            if (response.ok) {
                setShowForm(false);
                setEditingId(null);
                setForm({ username: '', password: '', nome: '', role: 'user', modulos: [] });
                loadUsers();
            } else {
                const data = await response.json();
                setError(data.detail || 'Erro ao salvar usuário');
            }
        } catch (err) {
            setError('Erro ao conectar com o servidor');
        } finally {
            setSaving(false);
        }
    };

    const handleEdit = (user: UserData) => {
        const modulos = user.modulos.includes('all') ? MODULOS_DISPONIVEIS.map(m => m.id) : user.modulos;
        setForm({ username: user.username, password: '', nome: user.nome, role: user.role, modulos });
        setEditingId(user.id);
        setShowForm(true);
        setError('');
    };

    const handleDelete = async (id: string) => {
        if (!confirm('Deseja realmente excluir este usuário?')) return;

        try {
            const response = await fetch(`/api/users/${id}`, { method: 'DELETE' });
            if (response.ok) {
                loadUsers();
            } else {
                const data = await response.json();
                alert(data.detail || 'Erro ao excluir usuário');
            }
        } catch (err) {
            alert('Erro ao conectar com o servidor');
        }
    };

    const handleCancel = () => {
        setShowForm(false);
        setEditingId(null);
        setForm({ username: '', password: '', nome: '', role: 'user', modulos: [] });
        setError('');
    };

    const toggleModulo = (moduloId: string) => {
        if (form.modulos.includes(moduloId)) {
            setForm({ ...form, modulos: form.modulos.filter(m => m !== moduloId) });
        } else {
            setForm({ ...form, modulos: [...form.modulos, moduloId] });
        }
    };

    const selectAllModulos = () => {
        setForm({ ...form, modulos: MODULOS_DISPONIVEIS.map(m => m.id) });
    };

    const clearAllModulos = () => {
        setForm({ ...form, modulos: [] });
    };

    return (
        <div style={{ padding: '24px', minHeight: '100vh', background: 'linear-gradient(to bottom right, #f8fafc, #f1f5f9)' }}>
            <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
                {/* Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div style={{ background: '#7c3aed', padding: '12px', borderRadius: '12px', boxShadow: '0 10px 15px -3px rgba(124, 58, 237, 0.2)' }}>
                            <Users style={{ width: '32px', height: '32px', color: 'white' }} />
                        </div>
                        <div>
                            <h1 style={{ fontSize: '28px', fontWeight: 'bold', color: '#1e293b', margin: 0 }}>Administração de Usuários</h1>
                            <p style={{ color: '#64748b', margin: 0 }}>Gerencie os usuários e permissões do sistema</p>
                        </div>
                    </div>

                    <button
                        onClick={() => { setShowForm(true); setEditingId(null); setForm({ username: '', password: '', nome: '', role: 'user', modulos: [] }); }}
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                            padding: '12px 20px',
                            background: '#7c3aed',
                            color: 'white',
                            border: 'none',
                            borderRadius: '12px',
                            fontWeight: 'bold',
                            cursor: 'pointer',
                            boxShadow: '0 4px 15px rgba(124, 58, 237, 0.3)'
                        }}
                    >
                        <Plus size={20} />
                        Novo Usuário
                    </button>
                </div>

                {/* Form Modal */}
                {showForm && (
                    <div style={{
                        position: 'fixed',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        background: 'rgba(0,0,0,0.5)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        zIndex: 1000,
                        padding: '20px',
                        overflowY: 'auto'
                    }}>
                        <div style={{
                            background: 'white',
                            borderRadius: '20px',
                            padding: '32px',
                            width: '100%',
                            maxWidth: '600px',
                            maxHeight: '90vh',
                            overflowY: 'auto',
                            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
                        }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                                <h2 style={{ fontSize: '20px', fontWeight: 'bold', color: '#1e293b', margin: 0 }}>
                                    {editingId ? 'Editar Usuário' : 'Novo Usuário'}
                                </h2>
                                <button onClick={handleCancel} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#94a3b8' }}>
                                    <X size={24} />
                                </button>
                            </div>

                            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                                <div>
                                    <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#475569', marginBottom: '8px' }}>Nome Completo</label>
                                    <input
                                        type="text"
                                        value={form.nome}
                                        onChange={(e) => setForm({ ...form, nome: e.target.value })}
                                        required
                                        style={{ width: '100%', padding: '12px 16px', border: '1px solid #e2e8f0', borderRadius: '10px', fontSize: '14px', boxSizing: 'border-box' }}
                                        placeholder="Ex: João Silva"
                                    />
                                </div>

                                <div>
                                    <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#475569', marginBottom: '8px' }}>Usuário (login)</label>
                                    <input
                                        type="text"
                                        value={form.username}
                                        onChange={(e) => setForm({ ...form, username: e.target.value })}
                                        required
                                        style={{ width: '100%', padding: '12px 16px', border: '1px solid #e2e8f0', borderRadius: '10px', fontSize: '14px', boxSizing: 'border-box' }}
                                        placeholder="Ex: joao.silva"
                                    />
                                </div>

                                <div>
                                    <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#475569', marginBottom: '8px' }}>
                                        Senha {editingId && <span style={{ fontWeight: 'normal', color: '#94a3b8' }}>(deixe em branco para manter)</span>}
                                    </label>
                                    <input
                                        type="password"
                                        value={form.password}
                                        onChange={(e) => setForm({ ...form, password: e.target.value })}
                                        required={!editingId}
                                        style={{ width: '100%', padding: '12px 16px', border: '1px solid #e2e8f0', borderRadius: '10px', fontSize: '14px', boxSizing: 'border-box' }}
                                        placeholder="••••••••"
                                    />
                                </div>

                                <div>
                                    <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#475569', marginBottom: '8px' }}>Perfil</label>
                                    <select
                                        value={form.role}
                                        onChange={(e) => setForm({ ...form, role: e.target.value })}
                                        style={{ width: '100%', padding: '12px 16px', border: '1px solid #e2e8f0', borderRadius: '10px', fontSize: '14px', boxSizing: 'border-box', cursor: 'pointer' }}
                                    >
                                        <option value="user">Usuário</option>
                                        <option value="admin">Administrador</option>
                                    </select>
                                </div>

                                {/* Módulos - só mostra se não for admin */}
                                {form.role !== 'admin' && (
                                    <div>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                                            <label style={{ fontSize: '14px', fontWeight: '600', color: '#475569' }}>Módulos com Acesso</label>
                                            <div style={{ display: 'flex', gap: '8px' }}>
                                                <button type="button" onClick={selectAllModulos} style={{ fontSize: '12px', padding: '4px 10px', background: '#f1f5f9', border: 'none', borderRadius: '6px', cursor: 'pointer', color: '#475569' }}>
                                                    Todos
                                                </button>
                                                <button type="button" onClick={clearAllModulos} style={{ fontSize: '12px', padding: '4px 10px', background: '#f1f5f9', border: 'none', borderRadius: '6px', cursor: 'pointer', color: '#475569' }}>
                                                    Nenhum
                                                </button>
                                            </div>
                                        </div>
                                        <div style={{
                                            display: 'grid',
                                            gridTemplateColumns: 'repeat(2, 1fr)',
                                            gap: '8px',
                                            background: '#f8fafc',
                                            padding: '16px',
                                            borderRadius: '12px',
                                            border: '1px solid #e2e8f0'
                                        }}>
                                            {MODULOS_DISPONIVEIS.map((modulo) => (
                                                <label
                                                    key={modulo.id}
                                                    style={{
                                                        display: 'flex',
                                                        alignItems: 'center',
                                                        gap: '8px',
                                                        padding: '10px 12px',
                                                        background: form.modulos.includes(modulo.id) ? '#ede9fe' : 'white',
                                                        border: form.modulos.includes(modulo.id) ? '2px solid #7c3aed' : '1px solid #e2e8f0',
                                                        borderRadius: '8px',
                                                        cursor: 'pointer',
                                                        transition: 'all 0.2s'
                                                    }}
                                                >
                                                    <input
                                                        type="checkbox"
                                                        checked={form.modulos.includes(modulo.id)}
                                                        onChange={() => toggleModulo(modulo.id)}
                                                        style={{ accentColor: '#7c3aed' }}
                                                    />
                                                    <span style={{
                                                        fontSize: '13px',
                                                        color: form.modulos.includes(modulo.id) ? '#7c3aed' : '#475569',
                                                        fontWeight: form.modulos.includes(modulo.id) ? '500' : '400'
                                                    }}>
                                                        {modulo.nome}
                                                    </span>
                                                </label>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {form.role === 'admin' && (
                                    <div style={{
                                        background: '#ede9fe',
                                        padding: '16px',
                                        borderRadius: '12px',
                                        border: '1px solid #c4b5fd',
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '12px'
                                    }}>
                                        <Shield size={24} color="#7c3aed" />
                                        <div>
                                            <p style={{ margin: 0, fontWeight: '600', color: '#7c3aed' }}>Administrador</p>
                                            <p style={{ margin: '4px 0 0 0', fontSize: '13px', color: '#6d28d9' }}>
                                                Tem acesso a todos os módulos e pode gerenciar usuários
                                            </p>
                                        </div>
                                    </div>
                                )}

                                {error && (
                                    <div style={{ background: '#fef2f2', border: '1px solid #fecaca', color: '#dc2626', padding: '12px', borderRadius: '10px', fontSize: '14px' }}>
                                        {error}
                                    </div>
                                )}

                                <div style={{ display: 'flex', gap: '12px', marginTop: '8px' }}>
                                    <button
                                        type="button"
                                        onClick={handleCancel}
                                        style={{ flex: 1, padding: '14px', border: '1px solid #e2e8f0', borderRadius: '10px', background: 'white', cursor: 'pointer', fontWeight: '500' }}
                                    >
                                        Cancelar
                                    </button>
                                    <button
                                        type="submit"
                                        disabled={saving}
                                        style={{
                                            flex: 1,
                                            padding: '14px',
                                            border: 'none',
                                            borderRadius: '10px',
                                            background: '#7c3aed',
                                            color: 'white',
                                            cursor: saving ? 'not-allowed' : 'pointer',
                                            fontWeight: 'bold',
                                            opacity: saving ? 0.5 : 1,
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            gap: '8px'
                                        }}
                                    >
                                        <Check size={18} />
                                        {saving ? 'Salvando...' : 'Salvar'}
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                )}

                {/* Users Table */}
                <div style={{ background: 'white', borderRadius: '16px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
                    {loading ? (
                        <div style={{ padding: '48px', textAlign: 'center' }}>
                            <div style={{ width: '40px', height: '40px', border: '4px solid #e2e8f0', borderTopColor: '#7c3aed', borderRadius: '50%', animation: 'spin 1s linear infinite', margin: '0 auto' }}></div>
                        </div>
                    ) : users.length === 0 ? (
                        <div style={{ padding: '48px', textAlign: 'center', color: '#64748b' }}>
                            Nenhum usuário cadastrado
                        </div>
                    ) : (
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead>
                                <tr style={{ background: '#f8fafc' }}>
                                    <th style={{ padding: '16px 24px', textAlign: 'left', fontSize: '12px', fontWeight: '600', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Usuário</th>
                                    <th style={{ padding: '16px 24px', textAlign: 'left', fontSize: '12px', fontWeight: '600', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Nome</th>
                                    <th style={{ padding: '16px 24px', textAlign: 'left', fontSize: '12px', fontWeight: '600', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Perfil</th>
                                    <th style={{ padding: '16px 24px', textAlign: 'left', fontSize: '12px', fontWeight: '600', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Módulos</th>
                                    <th style={{ padding: '16px 24px', textAlign: 'right', fontSize: '12px', fontWeight: '600', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Ações</th>
                                </tr>
                            </thead>
                            <tbody>
                                {users.map((user) => (
                                    <tr key={user.id} style={{ borderTop: '1px solid #f1f5f9' }}>
                                        <td style={{ padding: '16px 24px' }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                                <div style={{
                                                    width: '40px',
                                                    height: '40px',
                                                    borderRadius: '10px',
                                                    background: user.role === 'admin' ? '#7c3aed' : '#e2e8f0',
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    justifyContent: 'center',
                                                    color: user.role === 'admin' ? 'white' : '#64748b'
                                                }}>
                                                    {user.role === 'admin' ? <Shield size={20} /> : <User size={20} />}
                                                </div>
                                                <span style={{ fontWeight: '500', color: '#1e293b' }}>{user.username}</span>
                                            </div>
                                        </td>
                                        <td style={{ padding: '16px 24px', color: '#475569' }}>{user.nome}</td>
                                        <td style={{ padding: '16px 24px' }}>
                                            <span style={{
                                                display: 'inline-block',
                                                padding: '4px 12px',
                                                borderRadius: '9999px',
                                                fontSize: '12px',
                                                fontWeight: '500',
                                                background: user.role === 'admin' ? '#ede9fe' : '#f1f5f9',
                                                color: user.role === 'admin' ? '#7c3aed' : '#64748b'
                                            }}>
                                                {user.role === 'admin' ? 'Administrador' : 'Usuário'}
                                            </span>
                                        </td>
                                        <td style={{ padding: '16px 24px', color: '#64748b', fontSize: '13px' }}>
                                            {user.modulos.includes('all') ? (
                                                <span style={{ color: '#7c3aed', fontWeight: '500' }}>Todos</span>
                                            ) : (
                                                <span>{user.modulos.length} módulo(s)</span>
                                            )}
                                        </td>
                                        <td style={{ padding: '16px 24px', textAlign: 'right' }}>
                                            <button
                                                onClick={() => handleViewActivity(user)}
                                                style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '8px', color: '#10b981', marginRight: '4px' }}
                                                title="Ver Atividade"
                                            >
                                                <Eye size={18} />
                                            </button>
                                            <button
                                                onClick={() => handleEdit(user)}
                                                style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '8px', color: '#64748b', marginRight: '4px' }}
                                                title="Editar"
                                            >
                                                <Edit2 size={18} />
                                            </button>
                                            <button
                                                onClick={() => handleDelete(user.id)}
                                                style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '8px', color: '#64748b' }}
                                                title="Excluir"
                                            >
                                                <Trash2 size={18} />
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>

                {/* Activity Modal */}
                {showActivityModal && selectedUser && (
                    <div style={{
                        position: 'fixed',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        background: 'rgba(0,0,0,0.5)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        zIndex: 1000,
                        padding: '20px'
                    }}>
                        <div style={{
                            background: 'white',
                            borderRadius: '20px',
                            padding: '32px',
                            width: '100%',
                            maxWidth: '500px',
                            maxHeight: '80vh',
                            overflowY: 'auto',
                            boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25)'
                        }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                                <h2 style={{ fontSize: '20px', fontWeight: 'bold', color: '#1e293b', margin: 0 }}>
                                    Atividade do Usuário
                                </h2>
                                <button
                                    onClick={() => { setShowActivityModal(false); setSelectedUser(null); setUserActivity(null); }}
                                    style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#94a3b8' }}
                                >
                                    <X size={24} />
                                </button>
                            </div>

                            {/* User Info */}
                            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '24px', padding: '16px', background: '#f8fafc', borderRadius: '12px' }}>
                                <div style={{
                                    width: '50px',
                                    height: '50px',
                                    borderRadius: '12px',
                                    background: selectedUser.role === 'admin' ? '#7c3aed' : '#e2e8f0',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    color: selectedUser.role === 'admin' ? 'white' : '#64748b'
                                }}>
                                    {selectedUser.role === 'admin' ? <Shield size={24} /> : <User size={24} />}
                                </div>
                                <div>
                                    <p style={{ margin: 0, fontWeight: '600', fontSize: '16px', color: '#1e293b' }}>{selectedUser.nome}</p>
                                    <p style={{ margin: '4px 0 0 0', fontSize: '14px', color: '#64748b' }}>@{selectedUser.username}</p>
                                </div>
                            </div>

                            {loadingActivity ? (
                                <div style={{ textAlign: 'center', padding: '40px' }}>
                                    <div style={{ width: '40px', height: '40px', border: '4px solid #e2e8f0', borderTopColor: '#7c3aed', borderRadius: '50%', animation: 'spin 1s linear infinite', margin: '0 auto' }}></div>
                                    <p style={{ color: '#64748b', marginTop: '16px' }}>Carregando atividade...</p>
                                </div>
                            ) : userActivity ? (
                                <>
                                    {/* Status Online */}
                                    <div style={{ display: 'flex', gap: '16px', marginBottom: '20px' }}>
                                        <div style={{ flex: 1, padding: '16px', background: userActivity.isOnline ? '#ecfdf5' : '#fef2f2', borderRadius: '12px', border: `1px solid ${userActivity.isOnline ? '#a7f3d0' : '#fecaca'}` }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                                                <Circle size={12} fill={userActivity.isOnline ? '#10b981' : '#ef4444'} color={userActivity.isOnline ? '#10b981' : '#ef4444'} />
                                                <span style={{ fontSize: '12px', fontWeight: '600', color: userActivity.isOnline ? '#059669' : '#dc2626', textTransform: 'uppercase' }}>
                                                    {userActivity.isOnline ? 'Online' : 'Offline'}
                                                </span>
                                            </div>
                                            <p style={{ margin: 0, fontSize: '13px', color: '#64748b' }}>
                                                {userActivity.isOnline ? 'Usuário está ativo agora' : formatTimeAgo(userActivity.lastHeartbeat)}
                                            </p>
                                        </div>

                                        <div style={{ flex: 1, padding: '16px', background: '#f0f9ff', borderRadius: '12px', border: '1px solid #bae6fd' }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                                                <Clock size={14} color="#0284c7" />
                                                <span style={{ fontSize: '12px', fontWeight: '600', color: '#0284c7', textTransform: 'uppercase' }}>
                                                    Último Acesso
                                                </span>
                                            </div>
                                            <p style={{ margin: 0, fontSize: '13px', color: '#64748b' }}>
                                                {formatDateTime(userActivity.lastAccess)}
                                            </p>
                                        </div>
                                    </div>

                                    {/* Page History */}
                                    <div>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
                                            <Monitor size={16} color="#7c3aed" />
                                            <span style={{ fontSize: '14px', fontWeight: '600', color: '#475569' }}>Histórico de Páginas</span>
                                        </div>

                                        {userActivity.pageHistory.length === 0 ? (
                                            <p style={{ color: '#94a3b8', fontSize: '14px', textAlign: 'center', padding: '24px' }}>
                                                Nenhuma página acessada ainda
                                            </p>
                                        ) : (
                                            <div style={{ maxHeight: '250px', overflowY: 'auto', background: '#f8fafc', borderRadius: '12px', padding: '8px' }}>
                                                {userActivity.pageHistory.map((entry, index) => (
                                                    <div key={index} style={{
                                                        display: 'flex',
                                                        justifyContent: 'space-between',
                                                        alignItems: 'center',
                                                        padding: '10px 12px',
                                                        background: 'white',
                                                        borderRadius: '8px',
                                                        marginBottom: index < userActivity.pageHistory.length - 1 ? '6px' : 0,
                                                        border: '1px solid #e2e8f0'
                                                    }}>
                                                        <span style={{ fontSize: '13px', color: '#1e293b', fontWeight: '500' }}>
                                                            {entry.pageName}
                                                        </span>
                                                        <span style={{ fontSize: '11px', color: '#94a3b8' }}>
                                                            {formatTimeAgo(entry.timestamp)}
                                                        </span>
                                                    </div>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </>
                            ) : (
                                <p style={{ color: '#94a3b8', textAlign: 'center', padding: '24px' }}>
                                    Sem dados de atividade
                                </p>
                            )}

                            <button
                                onClick={() => { setShowActivityModal(false); setSelectedUser(null); setUserActivity(null); }}
                                style={{
                                    width: '100%',
                                    marginTop: '24px',
                                    padding: '14px',
                                    border: '1px solid #e2e8f0',
                                    borderRadius: '10px',
                                    background: 'white',
                                    cursor: 'pointer',
                                    fontWeight: '500',
                                    color: '#475569'
                                }}
                            >
                                Fechar
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};
