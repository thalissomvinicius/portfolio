import React, { useEffect } from 'react';

interface SobreViewProps {
    empresa: number;
    obra: string;
}

export const SobreView: React.FC<SobreViewProps> = () => {
    // Scroll para o topo quando o componente montar
    useEffect(() => {
        window.scrollTo(0, 0);
    }, []);

    return (
        <div className="animate-fade-in" style={{ maxWidth: '1200px', margin: '0 auto' }}>
            {/* Hero Section - Prime Imóveis Design */}
            <div style={{
                background: 'linear-gradient(135deg, #00528F 0%, #0089D6 50%, #00A5FF 100%)',
                borderRadius: '24px',
                padding: '60px 40px',
                marginBottom: '32px',
                position: 'relative',
                overflow: 'hidden',
                boxShadow: '0 25px 50px -12px rgba(0, 82, 143, 0.25)'
            }}>
                {/* Background Decoration */}
                <div style={{
                    position: 'absolute',
                    top: '-100px',
                    right: '-100px',
                    width: '400px',
                    height: '400px',
                    borderRadius: '50%',
                    background: 'linear-gradient(135deg, rgba(140, 198, 62, 0.2) 0%, rgba(0, 137, 214, 0.15) 100%)',
                    filter: 'blur(60px)'
                }} />
                <div style={{
                    position: 'absolute',
                    bottom: '-80px',
                    left: '-80px',
                    width: '300px',
                    height: '300px',
                    borderRadius: '50%',
                    background: 'linear-gradient(135deg, rgba(140, 198, 62, 0.2) 0%, rgba(0, 165, 255, 0.15) 100%)',
                    filter: 'blur(60px)'
                }} />

                <div style={{ position: 'relative', zIndex: 1, textAlign: 'center' }}>
                    <div style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '8px',
                        background: 'rgba(140, 198, 62, 0.2)',
                        padding: '8px 16px',
                        borderRadius: '100px',
                        marginBottom: '24px',
                        border: '1px solid rgba(140, 198, 62, 0.4)'
                    }}>
                        <span style={{ width: '8px', height: '8px', background: '#8CC63E', borderRadius: '50%' }} />
                        <span style={{ color: 'rgba(255,255,255,0.8)', fontSize: '13px', fontWeight: 500 }}>Sistema Ativo</span>
                    </div>

                    <h1 style={{
                        fontSize: '48px',
                        fontWeight: 800,
                        color: 'white',
                        marginBottom: '16px',
                        letterSpacing: '-1px',
                        textShadow: '0 2px 20px rgba(0,0,0,0.2)'
                    }}>
                        Prime Imóveis Dashboard
                    </h1>

                    <p style={{
                        fontSize: '18px',
                        color: 'rgba(255,255,255,0.85)',
                        maxWidth: '600px',
                        margin: '0 auto 32px',
                        lineHeight: 1.7
                    }}>
                        Sistema inteligente para gestão completa de loteamentos imobiliários,
                        vendas e controle financeiro em tempo real.
                    </p>

                    <div style={{ display: 'flex', justifyContent: 'center', gap: '24px' }}>
                        <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '32px', fontWeight: 700, color: '#8CC63E' }}>12+</div>
                            <div style={{ fontSize: '13px', color: 'rgba(255,255,255,0.7)' }}>Módulos</div>
                        </div>
                        <div style={{ width: '1px', background: 'rgba(255,255,255,0.2)' }} />
                        <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '32px', fontWeight: 700, color: '#8CC63E' }}>100%</div>
                            <div style={{ fontSize: '13px', color: 'rgba(255,255,255,0.7)' }}>Tempo Real</div>
                        </div>
                        <div style={{ width: '1px', background: 'rgba(255,255,255,0.2)' }} />
                        <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '32px', fontWeight: 700, color: 'white' }}>v2.0</div>
                            <div style={{ fontSize: '13px', color: 'rgba(255,255,255,0.7)' }}>Versão 2025</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Features Grid */}
            <div style={{ marginBottom: '32px' }}>
                <h2 style={{
                    fontSize: '24px',
                    fontWeight: 700,
                    color: '#1E293B',
                    marginBottom: '24px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px'
                }}>
                    <span style={{
                        width: '4px',
                        height: '24px',
                        background: 'linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%)',
                        borderRadius: '2px'
                    }} />
                    Funcionalidades
                </h2>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
                    <FeatureCard icon="📊" title="Dashboard" color="#3B82F6" />
                    <FeatureCard icon="💰" title="Recebimentos" color="#10B981" />
                    <FeatureCard icon="👥" title="Corretores" color="#8B5CF6" />
                    <FeatureCard icon="⚠️" title="Inadimplência" color="#EF4444" />
                    <FeatureCard icon="📈" title="Evolução" color="#F59E0B" />
                    <FeatureCard icon="📱" title="WhatsApp" color="#25D366" />
                    <FeatureCard icon="🔍" title="Consultas" color="#06B6D4" />
                    <FeatureCard icon="🏘️" title="Executivo" color="#EC4899" />
                </div>
            </div>

            {/* How to Use */}
            <div style={{
                background: 'linear-gradient(135deg, #F8FAFC 0%, #F1F5F9 100%)',
                borderRadius: '20px',
                padding: '32px',
                marginBottom: '32px',
                border: '1px solid #E2E8F0'
            }}>
                <h2 style={{
                    fontSize: '24px',
                    fontWeight: 700,
                    color: '#1E293B',
                    marginBottom: '24px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px'
                }}>
                    <span style={{
                        width: '4px',
                        height: '24px',
                        background: 'linear-gradient(135deg, #10B981 0%, #06B6D4 100%)',
                        borderRadius: '2px'
                    }} />
                    Como Utilizar
                </h2>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px' }}>
                    <StepCard number={1} title="Selecione" desc="Escolha o empreendimento" />
                    <StepCard number={2} title="Navegue" desc="Acesse os módulos" />
                    <StepCard number={3} title="Filtre" desc="Refine os dados" />
                    <StepCard number={4} title="Exporte" desc="Gere relatórios PDF" />
                </div>
            </div>

            {/* Developer Section - Prime Imóveis */}
            <div style={{
                background: 'linear-gradient(135deg, #00528F 0%, #0089D6 100%)',
                borderRadius: '24px',
                padding: '40px',
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: '40px',
                alignItems: 'center',
                position: 'relative',
                overflow: 'hidden'
            }}>
                {/* Background Glow */}
                <div style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    width: '500px',
                    height: '500px',
                    borderRadius: '50%',
                    background: 'radial-gradient(circle, rgba(59, 130, 246, 0.1) 0%, transparent 70%)',
                    filter: 'blur(40px)'
                }} />

                <div style={{ position: 'relative', zIndex: 1 }}>
                    <div style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '8px',
                        background: 'rgba(16, 185, 129, 0.2)',
                        padding: '6px 14px',
                        borderRadius: '100px',
                        marginBottom: '20px',
                        border: '1px solid rgba(16, 185, 129, 0.3)'
                    }}>
                        <span style={{ fontSize: '12px', color: '#10B981', fontWeight: 600 }}>DESENVOLVEDOR</span>
                    </div>

                    <h2 style={{
                        fontSize: '36px',
                        fontWeight: 800,
                        color: 'white',
                        marginBottom: '16px',
                        letterSpacing: '-0.5px'
                    }}>
                        Vinicius Dev
                    </h2>

                    <p style={{
                        fontSize: '15px',
                        color: 'rgba(255,255,255,0.85)',
                        lineHeight: 1.8,
                        marginBottom: '24px'
                    }}>
                        Sistema desenvolvido com foco em <span style={{ color: '#8CC63E' }}>performance</span>,{' '}
                        <span style={{ color: '#FFD700' }}>usabilidade</span> e{' '}
                        <span style={{ color: 'white' }}>integração em tempo real</span> com o banco de dados corporativo.
                    </p>

                    {/* Contact Buttons */}
                    <div style={{ display: 'flex', gap: '12px' }}>
                        <a
                            href="https://wa.me/5591991697664"
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{
                                background: 'linear-gradient(135deg, #25D366 0%, #128C7E 100%)',
                                padding: '12px 24px',
                                borderRadius: '12px',
                                fontSize: '14px',
                                color: 'white',
                                textDecoration: 'none',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px',
                                fontWeight: 600,
                                boxShadow: '0 4px 15px rgba(37, 211, 102, 0.3)',
                                transition: 'transform 0.2s, box-shadow 0.2s'
                            }}
                        >
                            📱 WhatsApp
                        </a>
                        <a
                            href="https://instagram.com/eu._.vini"
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{
                                background: 'linear-gradient(135deg, #833AB4 0%, #E1306C 50%, #F77737 100%)',
                                padding: '12px 24px',
                                borderRadius: '12px',
                                fontSize: '14px',
                                color: 'white',
                                textDecoration: 'none',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px',
                                fontWeight: 600,
                                boxShadow: '0 4px 15px rgba(225, 48, 108, 0.3)',
                                transition: 'transform 0.2s, box-shadow 0.2s'
                            }}
                        >
                            📷 @eu._.vini
                        </a>
                    </div>
                </div>

                {/* Tech Stack */}
                <div style={{ position: 'relative', zIndex: 1 }}>
                    <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.7)', marginBottom: '16px', fontWeight: 600, letterSpacing: '1px' }}>
                        TECNOLOGIAS UTILIZADAS
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        <TechBadge
                            icon="⚛️"
                            name="React + TypeScript"
                            desc="Frontend moderno e tipado"
                            color="#61DAFB"
                        />
                        <TechBadge
                            icon="🐍"
                            name="FastAPI + Python"
                            desc="Backend de alta performance"
                            color="#009688"
                        />
                        <TechBadge
                            icon="🗃️"
                            name="SQL Server"
                            desc="Banco de dados corporativo"
                            color="#CC2927"
                        />
                    </div>
                </div>
            </div>

            {/* Footer */}
            <div style={{
                textAlign: 'center',
                padding: '32px',
                color: '#94A3B8',
                fontSize: '13px'
            }}>
                © 2025 VallePrime • Todos os direitos reservados
            </div>
        </div >
    );
};

// Feature Card Component
const FeatureCard: React.FC<{ icon: string; title: string; color: string }> = ({ icon, title, color }) => (
    <div style={{
        background: 'white',
        borderRadius: '16px',
        padding: '20px',
        textAlign: 'center',
        border: '1px solid #E2E8F0',
        transition: 'transform 0.2s, box-shadow 0.2s',
        cursor: 'pointer'
    }}
        onMouseOver={(e) => {
            e.currentTarget.style.transform = 'translateY(-4px)';
            e.currentTarget.style.boxShadow = '0 12px 24px -8px rgba(0,0,0,0.1)';
        }}
        onMouseOut={(e) => {
            e.currentTarget.style.transform = 'translateY(0)';
            e.currentTarget.style.boxShadow = 'none';
        }}
    >
        <div style={{
            width: '48px',
            height: '48px',
            borderRadius: '12px',
            background: `${color}15`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 12px',
            fontSize: '24px'
        }}>
            {icon}
        </div>
        <div style={{ fontWeight: 600, color: '#1E293B', fontSize: '14px' }}>{title}</div>
    </div>
);

// Step Card Component
const StepCard: React.FC<{ number: number; title: string; desc: string }> = ({ number, title, desc }) => (
    <div style={{
        background: 'white',
        borderRadius: '16px',
        padding: '24px 20px',
        textAlign: 'center',
        boxShadow: '0 4px 12px rgba(0,0,0,0.05)'
    }}>
        <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '50%',
            background: 'linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%)',
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 700,
            fontSize: '16px',
            margin: '0 auto 12px',
            boxShadow: '0 4px 12px rgba(59, 130, 246, 0.3)'
        }}>
            {number}
        </div>
        <div style={{ fontWeight: 600, color: '#1E293B', fontSize: '14px', marginBottom: '4px' }}>{title}</div>
        <div style={{ fontSize: '12px', color: '#64748B' }}>{desc}</div>
    </div>
);

// Tech Badge Component
const TechBadge: React.FC<{ icon: string; name: string; desc: string; color: string }> = ({ icon, name, desc, color }) => (
    <div style={{
        background: 'rgba(255,255,255,0.05)',
        borderRadius: '12px',
        padding: '16px',
        display: 'flex',
        alignItems: 'center',
        gap: '16px',
        border: '1px solid rgba(255,255,255,0.1)'
    }}>
        <div style={{
            width: '44px',
            height: '44px',
            borderRadius: '10px',
            background: `${color}20`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '22px'
        }}>
            {icon}
        </div>
        <div>
            <div style={{ fontWeight: 600, color: 'white', fontSize: '14px', marginBottom: '2px' }}>{name}</div>
            <div style={{ fontSize: '12px', color: 'rgba(255,255,255,0.7)' }}>{desc}</div>
        </div>
    </div>
);
