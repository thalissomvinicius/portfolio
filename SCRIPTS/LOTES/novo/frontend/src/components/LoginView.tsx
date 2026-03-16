import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import logoPrime from '../assets/logoprime.png';

export const LoginView: React.FC = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        const success = await login(username, password);

        if (!success) {
            setError('Usuário ou senha inválidos');
        }
        setLoading(false);
    };

    return (
        <div style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #1e3a5f 0%, #0d1b2a 100%)',
            padding: '20px'
        }}>
            <div style={{
                background: 'white',
                borderRadius: '24px',
                padding: '48px',
                width: '100%',
                maxWidth: '420px',
                boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)'
            }}>
                {/* Logo */}
                <div style={{ textAlign: 'center', marginBottom: '40px' }}>
                    <div style={{
                        background: 'white',
                        borderRadius: '16px',
                        padding: '16px 24px',
                        display: 'inline-block',
                        boxShadow: '0 4px 15px rgba(0, 0, 0, 0.08)',
                        marginBottom: '20px'
                    }}>
                        <img
                            src={logoPrime}
                            alt="Prime Imóveis"
                            style={{ height: '60px', objectFit: 'contain' }}
                        />
                    </div>
                    <h1 style={{ fontSize: '24px', fontWeight: 'bold', color: '#1e293b', margin: '0 0 8px 0' }}>
                        Sistema de Gestão
                    </h1>
                    <p style={{ color: '#64748b', margin: 0 }}>
                        Faça login para continuar
                    </p>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <div>
                        <label style={{
                            display: 'block',
                            fontSize: '14px',
                            fontWeight: '600',
                            color: '#334155',
                            marginBottom: '8px'
                        }}>
                            Usuário
                        </label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Digite seu usuário"
                            required
                            style={{
                                width: '100%',
                                padding: '14px 16px',
                                fontSize: '16px',
                                border: '2px solid #e2e8f0',
                                borderRadius: '12px',
                                outline: 'none',
                                transition: 'border-color 0.2s',
                                boxSizing: 'border-box'
                            }}
                            onFocus={(e) => e.target.style.borderColor = '#0089D6'}
                            onBlur={(e) => e.target.style.borderColor = '#e2e8f0'}
                        />
                    </div>

                    <div>
                        <label style={{
                            display: 'block',
                            fontSize: '14px',
                            fontWeight: '600',
                            color: '#334155',
                            marginBottom: '8px'
                        }}>
                            Senha
                        </label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Digite sua senha"
                            required
                            style={{
                                width: '100%',
                                padding: '14px 16px',
                                fontSize: '16px',
                                border: '2px solid #e2e8f0',
                                borderRadius: '12px',
                                outline: 'none',
                                transition: 'border-color 0.2s',
                                boxSizing: 'border-box'
                            }}
                            onFocus={(e) => e.target.style.borderColor = '#0089D6'}
                            onBlur={(e) => e.target.style.borderColor = '#e2e8f0'}
                        />
                    </div>

                    {error && (
                        <div style={{
                            background: '#fef2f2',
                            border: '1px solid #fecaca',
                            color: '#dc2626',
                            padding: '12px 16px',
                            borderRadius: '12px',
                            fontSize: '14px',
                            textAlign: 'center'
                        }}>
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        style={{
                            width: '100%',
                            padding: '16px',
                            fontSize: '16px',
                            fontWeight: 'bold',
                            color: 'white',
                            background: loading ? '#94a3b8' : 'linear-gradient(135deg, #0089D6 0%, #0077be 100%)',
                            border: 'none',
                            borderRadius: '12px',
                            cursor: loading ? 'not-allowed' : 'pointer',
                            transition: 'transform 0.2s, box-shadow 0.2s',
                            boxShadow: '0 4px 15px rgba(0, 137, 214, 0.3)'
                        }}
                    >
                        {loading ? 'Entrando...' : 'Entrar'}
                    </button>
                </form>

                {/* Footer */}
                <div style={{ marginTop: '32px', textAlign: 'center' }}>
                    <p style={{ fontSize: '12px', color: '#94a3b8', margin: '0 0 4px 0' }}>
                        © 2025 Prime Imóveis - Todos os direitos reservados
                    </p>
                    <p style={{ fontSize: '11px', color: '#8CC63E', fontStyle: 'italic', margin: 0 }}>
                        Desenvolvido por Vinicius Dev
                    </p>
                </div>
            </div>
        </div>
    );
};
