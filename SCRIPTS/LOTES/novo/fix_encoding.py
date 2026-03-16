file_path = r'c:\Users\thalissom.cruz\Desktop\DASHVALLE\LOTES\novo\frontend\src\components\ConsultaVenda.tsx'

with open(file_path, 'rb') as f:
    content = f.read()

# Fix the arrow issue - replace improper > with proper JSX syntax
replacements = [
    (b"<span style={{ color: '#2563EB' }}>></span>", b"<span style={{ color: '#2563EB' }}>{'>'}</span>"),
    (b"<span style={{ color: '#2563EB' }}>>", b"<span style={{ color: '#2563EB' }}>{'>'}"),
]

for old, new in replacements:
    content = content.replace(old, new)

with open(file_path, 'wb') as f:
    f.write(content)

print('Fixed JSX syntax error!')
