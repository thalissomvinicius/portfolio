import React from 'react';
import logoPrime from '../assets/logoprime.png';

interface EmpresaOption {
    empresa: number;
    obra: string;
    nome: string;
}

interface User {
    id: string;
    username: string;
    nome: string;
    role: string;
    modulos: string[];
}

interface SidebarProps {
    activeView: 'dashboard' | 'boletos' | 'consulta' | 'corretores' | 'mensagens' | 'inadimplentes' | 'evolucao' | 'recebimentos' | 'loteamento' | 'disponibilidades' | 'contratos' | 'quitacao' | 'sobre' | 'feedbacks' | 'admin';
    onViewChange: (view: 'dashboard' | 'boletos' | 'consulta' | 'corretores' | 'mensagens' | 'inadimplentes' | 'evolucao' | 'recebimentos' | 'loteamento' | 'disponibilidades' | 'contratos' | 'quitacao' | 'sobre' | 'feedbacks' | 'admin') => void;
    onRefresh: () => void;
    empresas: EmpresaOption[];
    selectedEmpresaIndex: number;
    onEmpresaChange: (index: number) => void;
    isCollapsed: boolean;
    onToggleCollapse: () => void;
    user: User | null;
    onLogout: () => void;
}

// SVG Icons
const icons = {
    dashboard: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M14 2V8H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M9 15L11 17L15 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
    ),
    consulta: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="11" cy="11" r="8" stroke="currentColor" strokeWidth="2" />
            <path d="M21 21L16.65 16.65" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        </svg>
    ),
    corretores: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M17 21V19C17 17.9391 16.5786 16.9217 15.8284 16.1716C15.0783 15.4214 14.0609 15 13 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <circle cx="9" cy="7" r="4" stroke="currentColor" strokeWidth="2" />
            <path d="M23 21V19C22.9993 18.1137 22.7044 17.2528 22.1614 16.5523C21.6184 15.8519 20.8581 15.3516 20 15.13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M16 3.13C16.8604 3.35031 17.623 3.85071 18.1676 4.55232C18.7122 5.25392 19.0078 6.11683 19.0078 7.005C19.0078 7.89318 18.7122 8.75608 18.1676 9.45769C17.623 10.1593 16.8604 10.6597 16 10.88" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
    ),
    mensagens: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 11.5C21.0034 12.8199 20.6951 14.1219 20.1 15.3C19.3944 16.7118 18.3098 17.8992 16.9674 18.7293C15.6251 19.5594 14.0782 19.9994 12.5 20C11.1801 20.0035 9.87812 19.6951 8.7 19.1L3 21L4.9 15.3C4.30493 14.1219 3.99656 12.8199 4 11.5C4.00061 9.92179 4.44061 8.37488 5.27072 7.03258C6.10083 5.69028 7.28825 4.6056 8.7 3.90003C9.87812 3.30496 11.1801 2.99659 12.5 3.00003H13C15.0843 3.11502 17.053 3.99479 18.5291 5.47089C20.0052 6.94699 20.885 8.91568 21 11V11.5Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
    ),
    inadimplentes: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M10.29 3.86L1.82 18C1.64 18.3 1.56 18.65 1.56 19C1.56 19.89 2.27 20.64 3.16 20.64H20.84C21.73 20.64 22.44 19.89 22.44 19C22.44 18.65 22.36 18.3 22.18 18L13.71 3.86C13.32 3.19 12.67 2.84 12 2.84C11.33 2.84 10.68 3.19 10.29 3.86Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M12 9V13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M12 17H12.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
    ),
    evolucao: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M18 20V10" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M12 20V4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M6 20V14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
    ),
    recebimentos: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 1V23" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M17 5L12 1L7 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M21 12H3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <rect x="3" y="16" width="18" height="6" rx="1" stroke="currentColor" strokeWidth="2" />
        </svg>
    ),
    relatorioCorretor: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M14 2V8H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M16 13H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M16 17H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M10 9H9H8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
    ),
    loteamento: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 21H4V3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M7 14L12 9L16 13L21 8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <circle cx="21" cy="8" r="2" stroke="currentColor" strokeWidth="2" />
        </svg>
    ),
    sobre: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
            <path d="M12 16V12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            <circle cx="12" cy="8" r="1" fill="currentColor" />
        </svg>
    ),
    disponibilidades: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <polyline points="9 22 9 12 15 12 15 22" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
    ),
    contratos: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M14 2V8H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M12 18V12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            <path d="M9 15L12 12L15 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
    ),
    quitacao: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M9 11L12 14L22 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M21 12V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V5C3 4.46957 3.21071 3.96086 3.58579 3.58579C3.96086 3.21071 4.46957 3 5 3H16" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
    ),
    refresh: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M23 4V10H17" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M1 20V14H7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M3.51 9C4.01717 7.56678 4.87913 6.28531 6.01547 5.27542C7.1518 4.26553 8.52547 3.55976 10.0083 3.22426C11.4911 2.88875 13.0348 2.93434 14.4952 3.35677C15.9556 3.77921 17.2853 4.56471 18.36 5.64L23 10M1 14L5.64 18.36C6.71475 19.4353 8.04437 20.2208 9.50481 20.6432C10.9652 21.0657 12.5089 21.1112 13.9917 20.7757C15.4745 20.4402 16.8482 19.7345 17.9845 18.7246C19.1209 17.7147 19.9828 16.4332 20.49 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
    ),
    home: (
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 9L12 2L21 9V20C21 20.5304 20.7893 21.0391 20.4142 21.4142C20.0391 21.7893 19.5304 22 19 22H5C4.46957 22 3.96086 21.7893 3.58579 21.4142C3.21071 21.0391 3 20.5304 3 20V9Z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M9 22V12H15V22" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
    ),
    menu: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M3 12H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            <path d="M3 6H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
            <path d="M3 18H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
        </svg>
    ),
    chevronLeft: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M15 18L9 12L15 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
    ),
    chevronRight: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M9 18L15 12L9 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
    ),
    feedback: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 11.5C21.0034 12.8199 20.6951 14.1219 20.1 15.3C19.3944 16.7118 18.3098 17.8992 16.9674 18.7293C15.6251 19.5594 14.0782 19.9994 12.5 20C11.1801 20.0035 9.87812 19.6951 8.7 19.1L3 21L4.9 15.3C4.30493 14.1219 3.99656 12.8199 4 11.5C4.00061 9.92179 4.44061 8.37488 5.27072 7.03258C6.10083 5.69028 7.28825 4.6056 8.7 3.90003C9.87812 3.30496 11.1801 2.99659 12.5 3.00003H13C15.0843 3.11502 17.053 3.99479 18.5291 5.47089C20.0052 6.94699 20.885 8.91568 21 11V11.5Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M12 11V11.01" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M12 17V17.01" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
    ),
    admin: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
    ),
    logout: (
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <polyline points="16 17 21 12 16 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            <line x1="21" y1="12" x2="9" y2="12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
    )
};

interface NavItemProps {
    icon: React.ReactNode;
    label: string;
    isActive: boolean;
    isCollapsed: boolean;
    onClick: () => void;
}

const NavItem: React.FC<NavItemProps> = ({ icon, label, isActive, isCollapsed, onClick }) => (
    <div
        className={`nav-item ${isActive ? 'active' : ''}`}
        onClick={onClick}
        style={{
            cursor: 'pointer',
            justifyContent: isCollapsed ? 'center' : 'flex-start',
            padding: isCollapsed ? '12px' : '12px 16px',
        }}
        title={isCollapsed ? label : undefined}
    >
        {icon}
        {!isCollapsed && <span>{label}</span>}
    </div>
);

export const Sidebar: React.FC<SidebarProps> = ({
    activeView,
    onViewChange,
    onRefresh,
    empresas,
    selectedEmpresaIndex,
    onEmpresaChange,
    isCollapsed,
    onToggleCollapse,
    user,
    onLogout
}) => {
    // Função para verificar acesso aos módulos
    const hasAccess = (modulo: string): boolean => {
        if (!user) return false;
        if (user.role === 'admin') return true;
        if (user.modulos?.includes('all')) return true;
        return user.modulos?.includes(modulo) ?? false;
    };
    return (
        <aside
            className="sidebar"
            style={{
                width: isCollapsed ? '72px' : '260px',
                transition: 'width 0.3s ease',
                padding: isCollapsed ? '16px 8px' : '20px 12px',
            }}
        >
            {/* Logo & Toggle */}
            <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: isCollapsed ? 'center' : 'space-between',
                marginBottom: isCollapsed ? '24px' : '24px',
                padding: isCollapsed ? '0' : '0 8px',
            }}>
                {!isCollapsed ? (
                    <div className="sidebar-logo" style={{
                        marginBottom: 0,
                        padding: '6px 10px',
                        background: 'white',
                        borderRadius: '10px',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.12)'
                    }}>
                        <img src={logoPrime} alt="Prime Imóveis" className="sidebar-logo-img" />
                    </div>
                ) : (
                    <div className="sidebar-logo-icon" style={{ width: '40px', height: '40px', background: 'linear-gradient(135deg, #0089D6 0%, #8CC63E 100%)' }}>
                        <span style={{ fontSize: '16px', fontWeight: 700, color: 'white' }}>P</span>
                    </div>
                )}

                {!isCollapsed && (
                    <button
                        onClick={onToggleCollapse}
                        style={{
                            background: 'rgba(255,255,255,0.1)',
                            border: 'none',
                            borderRadius: '8px',
                            padding: '8px',
                            cursor: 'pointer',
                            color: 'white',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            transition: 'background 0.2s'
                        }}
                        title="Recolher menu"
                    >
                        {icons.chevronLeft}
                    </button>
                )}
            </div>

            {/* Toggle Button when collapsed */}
            {isCollapsed && (
                <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '16px' }}>
                    <button
                        onClick={onToggleCollapse}
                        style={{
                            background: 'rgba(255,255,255,0.1)',
                            border: 'none',
                            borderRadius: '8px',
                            padding: '8px',
                            cursor: 'pointer',
                            color: 'white',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            transition: 'background 0.2s'
                        }}
                        title="Expandir menu"
                    >
                        {icons.chevronRight}
                    </button>
                </div>
            )}

            {/* Seletor de Empresa - Only when expanded */}
            {!isCollapsed && (
                <div style={{
                    padding: '16px 12px',
                    background: 'rgba(255,255,255,0.03)',
                    borderRadius: '12px',
                    marginBottom: '16px',
                    border: '1px solid rgba(255,255,255,0.06)'
                }}>
                    <label style={{
                        display: 'block',
                        fontSize: '10px',
                        color: 'rgba(255,255,255,0.5)',
                        marginBottom: '8px',
                        textTransform: 'uppercase',
                        letterSpacing: '1px',
                        fontWeight: 600
                    }}>
                        🏢 Empreendimento
                    </label>
                    <select
                        value={selectedEmpresaIndex}
                        onChange={(e) => onEmpresaChange(parseInt(e.target.value))}
                        style={{
                            width: '100%',
                            padding: '10px 12px',
                            borderRadius: '8px',
                            border: '1px solid rgba(255,255,255,0.1)',
                            background: 'rgba(255,255,255,0.08)',
                            color: 'white',
                            fontSize: '12px',
                            fontWeight: 500,
                            cursor: 'pointer',
                            outline: 'none',
                            transition: 'all 0.2s'
                        }}
                    >
                        {empresas.map((emp, idx) => (
                            <option key={idx} value={idx} style={{ color: '#1E293B', background: 'white' }}>
                                {emp.nome}
                            </option>
                        ))}
                    </select>
                </div>
            )}

            {/* Navigation */}
            <nav className="sidebar-nav" style={{ flex: 1 }}>
                {hasAccess('loteamento') && <NavItem icon={icons.loteamento} label="Dashboard Executivo" isActive={activeView === 'loteamento'} isCollapsed={isCollapsed} onClick={() => onViewChange('loteamento')} />}
                {hasAccess('evolucao') && <NavItem icon={icons.evolucao} label="Evolução" isActive={activeView === 'evolucao'} isCollapsed={isCollapsed} onClick={() => onViewChange('evolucao')} />}
                {hasAccess('boletos') && <NavItem icon={icons.dashboard} label="Gerenciamento de Boletos" isActive={activeView === 'boletos'} isCollapsed={isCollapsed} onClick={() => onViewChange('boletos')} />}
                {hasAccess('recebimentos') && <NavItem icon={icons.recebimentos} label="Recebimentos" isActive={activeView === 'recebimentos'} isCollapsed={isCollapsed} onClick={() => onViewChange('recebimentos')} />}
                {hasAccess('inadimplentes') && <NavItem icon={icons.inadimplentes} label="Inadimplência" isActive={activeView === 'inadimplentes'} isCollapsed={isCollapsed} onClick={() => onViewChange('inadimplentes')} />}
                {hasAccess('corretores') && <NavItem icon={icons.corretores} label="Corretores" isActive={activeView === 'corretores'} isCollapsed={isCollapsed} onClick={() => onViewChange('corretores')} />}
                {hasAccess('consulta') && <NavItem icon={icons.consulta} label="Consultar Venda" isActive={activeView === 'consulta'} isCollapsed={isCollapsed} onClick={() => onViewChange('consulta')} />}
                {hasAccess('disponibilidades') && <NavItem icon={icons.disponibilidades} label="Disponibilidades" isActive={activeView === 'disponibilidades'} isCollapsed={isCollapsed} onClick={() => onViewChange('disponibilidades')} />}
                {hasAccess('contratos') && <NavItem icon={icons.contratos} label="Contratos" isActive={activeView === 'contratos'} isCollapsed={isCollapsed} onClick={() => onViewChange('contratos')} />}
                {hasAccess('quitacao') && <NavItem icon={icons.quitacao} label="Termos e Contratos" isActive={activeView === 'quitacao'} isCollapsed={isCollapsed} onClick={() => onViewChange('quitacao')} />}
                {hasAccess('mensagens') && <NavItem icon={icons.mensagens} label="Mensagens Diárias" isActive={activeView === 'mensagens'} isCollapsed={isCollapsed} onClick={() => onViewChange('mensagens')} />}
                {hasAccess('feedbacks') && <NavItem icon={icons.feedback} label="Feedbacks" isActive={activeView === 'feedbacks'} isCollapsed={isCollapsed} onClick={() => onViewChange('feedbacks')} />}
                {hasAccess('sobre') && <NavItem icon={icons.sobre} label="Sobre" isActive={activeView === 'sobre'} isCollapsed={isCollapsed} onClick={() => onViewChange('sobre')} />}

                {user?.role === 'admin' && (
                    <NavItem icon={icons.admin} label="Administração" isActive={activeView === 'admin'} isCollapsed={isCollapsed} onClick={() => onViewChange('admin')} />
                )}

                <div style={{ marginTop: '16px' }}>
                    <NavItem icon={icons.refresh} label="Atualizar" isActive={false} isCollapsed={isCollapsed} onClick={onRefresh} />
                    <NavItem icon={icons.logout} label="Sair" isActive={false} isCollapsed={isCollapsed} onClick={onLogout} />
                </div>
            </nav>

            {/* Footer - Only when expanded */}
            {!isCollapsed && (
                <div style={{
                    marginTop: 'auto',
                    padding: '16px 8px',
                    borderTop: '1px solid rgba(255,255,255,0.1)'
                }}>
                    {user && (
                        <div style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '10px',
                            marginBottom: '12px',
                            padding: '10px',
                            background: 'rgba(255,255,255,0.05)',
                            borderRadius: '10px'
                        }}>
                            <div style={{
                                width: '36px',
                                height: '36px',
                                borderRadius: '10px',
                                background: user.role === 'admin' ? '#7c3aed' : '#0089D6',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                color: 'white',
                                fontWeight: 'bold',
                                fontSize: '14px'
                            }}>
                                {user.nome.charAt(0).toUpperCase()}
                            </div>
                            <div style={{ overflow: 'hidden' }}>
                                <p style={{ color: 'white', fontSize: '12px', fontWeight: '600', margin: 0, whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>
                                    {user.nome}
                                </p>
                                <p style={{ color: 'rgba(255,255,255,0.5)', fontSize: '10px', margin: 0 }}>
                                    {user.role === 'admin' ? 'Administrador' : 'Usuário'}
                                </p>
                            </div>
                        </div>
                    )}
                    <p style={{
                        fontSize: '10px',
                        color: 'rgba(255,255,255,0.5)',
                        textAlign: 'center',
                        marginBottom: '4px'
                    }}>
                        © 2025 Prime Imóveis
                    </p>
                    <p style={{
                        fontSize: '9px',
                        color: 'rgba(140, 198, 62, 0.7)',
                        textAlign: 'center',
                        fontStyle: 'italic'
                    }}>
                        Vinicius Dev
                    </p>
                </div>
            )}
        </aside>
    );
};
