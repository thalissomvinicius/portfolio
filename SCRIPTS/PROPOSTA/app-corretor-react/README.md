# Valle Prime - Portal do Corretor

Aplicação React + TypeScript para consulta de lotes disponíveis nos empreendimentos Valle Prime.

## 🚀 Tecnologias

- **React 18** - Framework UI
- **TypeScript** - Tipagem estática
- **Vite** - Build tool moderna e rápida
- **CSS Modules** - Estilos componentizados

## 📦 Instalação

```bash
# Instalar dependências
npm install

# Executar em desenvolvimento
npm run dev

# Build para produção
npm run build

# Preview da build de produção
npm run preview
```

## 🎯 Funcionalidades

- ✅ Listagem de lotes com informações detalhadas
- ✅ Filtros por status, quadra e busca livre
- ✅ Estatísticas em tempo real
- ✅ Modal com detalhes completos do lote
- ✅ Integração com API Valle Prime
- ✅ Design responsivo (desktop e mobile)
- ✅ Botão para gerar proposta (lotes disponíveis)

## 🔌 API

A aplicação consome a API Valle Prime:
- **Base URL**: `http://apiweb.valleprime.com.br:8000/api`
- **Endpoint**: `/consulta/{cod_empreendimento}/`

## 📱 Empreendimentos Disponíveis

| Código | Nome | Cidade | Estado |
|--------|------|--------|--------|
| 600 | Residencial Jardim do Valle | Dom Eliseu | PA |
| 601 | Residencial Jardim América | Capanema | PA |
| 602 | Residencial Salles Jardim | Castanhal | PA |
| 603 | Residencial Jardim Castanhal | Castanhal | PA |
| 604 | Residencial Ipitinga | Tomé-Açu | PA |
| 605 | Residencial Valle do Ipitinga | Tomé-Açu | PA |
| 610 | Residencial Jardim do Valle | Tailândia | PA |
| 616 | Residencial Jardim do Valle | Barcarena | PA |
| 617 | Residencial Jardim América II | Capanema | PA |
| 618 | Residencial Jardim do Valle II | Tailândia | PA |
| 620 | Residencial Jardim Valle do Uraim | Paragominas | PA |
| 621 | Residencial Parque do Valle | Rondon do Pará | PA |
| 622 | Residencial Jardim Valle do Uraim II | Rondon do Pará | PA |
| 623 | Residencial Jardim Castanhal III | Castanhal | PA |
| 624 | Residencial Valle do Ipitinga II | Tomé-Açu | PA |
| 625 | Residencial Valle dos Ipês | Tomé-Açu | PA |
| 626 | Residencial Jardim do Valle II | Dom Eliseu | PA |

## 🎨 Design

- Interface moderna com gradientes e sombras
- Animações suaves
- Cards interativos
- Modal responsivo
- Cores semânticas por status

## 📄 Estrutura do Projeto

```
src/
├── components/        # Componentes React
│   ├── Header/
│   ├── Filters/
│   ├── Stats/
│   ├── LoteCard/
│   └── LoteModal/
├── services/         # Serviços de API
├── types/            # Tipos TypeScript
├── App.tsx           # Componente principal
└── main.tsx          # Entry point
```

## 🔧 Configuração CORS

Se encontrar problemas de CORS ao conectar com a API, você pode:

1. Usar um proxy reverso (recomendado para produção)
2. Configurar o servidor para permitir CORS
3. Usar uma extensão de navegador (apenas desenvolvimento)

## 📝 Licença

© 2025 Valle Prime - Todos os direitos reservados
