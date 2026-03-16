import React from 'react';
import { FaHome, FaFileAlt } from 'react-icons/fa';
import './Header.css';

interface HeaderProps {
    onNovaPropostaClick: () => void;
}

const Header: React.FC<HeaderProps> = ({ onNovaPropostaClick }) => {
    return (
        <header className="header">
            <div className="header-content">
                <div className="logo-section">
                    <img src="/Valle-logo-azul.png" alt="Valle Prime" className="logo" />
                    <h1 className="portal-name">Portal do Corretor</h1>
                </div>

                <nav className="nav">
                    <a href="#lotes" className="nav-link active">
                        <FaHome /> Lotes
                    </a>
                    <button onClick={onNovaPropostaClick} className="nav-link nav-button">
                        <FaFileAlt /> Nova Proposta
                    </button>
                </nav>
            </div>
        </header>
    );
};

export default Header;
