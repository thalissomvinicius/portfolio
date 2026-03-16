import sys
from typing import List, Dict
from database import execute_query

PERSON_TABLE_HINTS = ['Pes', 'Pessoa']
CITY_KEYWORDS = ['naturalidade', 'cidnasc', 'cidade_nascimento', 'cidadenascimento']
UF_KEYWORDS = ['ufnaturalidade', 'uf_naturalidade', 'ufnasc', 'ufnascimento']
ID_KEYS = ['cod_pf', 'cod_pes']
WIDE_KEYWORDS = ['nasc', 'nat', 'natural', 'cidade', 'cid']

def list_person_tables() -> List[str]:
    rows = execute_query("SELECT name FROM sys.tables")
    names = [r.get('name') for r in rows]
    result = []
    for n in names:
        low = n.lower()
        if any(h.lower() in low for h in PERSON_TABLE_HINTS):
            result.append(n)
    return result

def list_columns(table: str) -> List[str]:
    q = f"SELECT name FROM sys.columns WHERE object_id = OBJECT_ID('{table}')"
    rows = execute_query(q)
    return [r.get('name') for r in rows]

def find_candidate_columns(table: str) -> Dict[str, List[str]]:
    cols = [c.lower() for c in list_columns(table)]
    city_cols = [c for c in cols if any(k in c for k in CITY_KEYWORDS)]
    uf_cols = [c for c in cols if any(k in c for k in UF_KEYWORDS)]
    id_cols = [c for c in cols if c in ID_KEYS]
    wide_cols = [c for c in cols if any(k in c for k in WIDE_KEYWORDS)]
    return {"city": city_cols, "uf": uf_cols, "id": id_cols, "wide": wide_cols}

def fetch_values(table: str, cod_pes: int, cols: Dict[str, List[str]]) -> Dict[str, str]:
    keys = cols.get('id') or []
    if not keys:
        return {}
    city = cols.get('city') or []
    uf = cols.get('uf') or []
    sel = []
    if city:
        sel.extend(city)
    if uf:
        sel.extend(uf)
    if cols.get('wide'):
        for w in cols.get('wide'):
            if w not in sel:
                sel.append(w)
    if not sel:
        return {}
    key = keys[0]
    query = f"SELECT {', '.join(sel)} FROM {table} WITH(NOLOCK) WHERE {key} = {int(cod_pes)}"
    rows = execute_query(query)
    return rows[0] if rows else {}

def list_city_table_columns() -> Dict[str, List[str]]:
    rows = execute_query("SELECT name FROM sys.tables WHERE name IN ('Cidades','CidadeDePara','CidadeLegislacao')")
    out = {}
    for r in rows:
        t = r.get('name')
        cols = list_columns(t)
        out[t] = cols
    return out

def search_city_name(code: str) -> Dict[str, str]:
    tables = ['Cidades','CidadeDePara','CidadeLegislacao']
    for t in tables:
        cols = list_columns(t)
        id_cols = [c for c in cols if 'cod' in c.lower() or 'id' in c.lower()]
        name_cols = [c for c in cols if 'nome' in c.lower() or 'cidade' in c.lower() or 'descricao' in c.lower()]
        if not id_cols or not name_cols:
            continue
        idc = id_cols[0]
        namec = name_cols[0]
        q = f"SELECT TOP 1 {namec} AS nome FROM {t} WITH(NOLOCK) WHERE TRY_CONVERT(int, {idc}) = TRY_CONVERT(int, ?)"
        rows = execute_query(q, (code,))
        if rows:
            return {"tabela": t, "nome": str(rows[0].get('nome'))}
    return {}

def main():
    cod = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    print("Tabelas de pessoa:")
    tables = list_person_tables()
    print(tables)
    print("Colunas candidatas por tabela:")
    mapa = {}
    for t in tables:
        mapa[t] = find_candidate_columns(t)
    print(mapa)
    if cod:
        print(f"Valores para pessoa {cod}:")
        resultados = {}
        for t in tables:
            vals = fetch_values(t, cod, mapa[t])
            if vals:
                resultados[t] = vals
        print(resultados)
        for t, vals in resultados.items():
            for k, v in vals.items():
                if v is not None and str(v).strip().isdigit():
                    city_guess = search_city_name(str(v).strip())
                    if city_guess:
                        print({"origem": f"{t}.{k}", "codigo": v, "cidade": city_guess})

if __name__ == "__main__":
    main()
