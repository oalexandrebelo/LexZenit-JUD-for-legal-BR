# /brag-slim · LexZenit Jurídico

**O que é:** skill jurídica para o Claude com 39 plugins e 176 workflows de Direito brasileiro, mais um núcleo local que guarda o original, reconhece citações sem fingir que as autenticou, pseudonimiza e para no gate de revisão humana.
**Para quem:** advogados, legal ops e engenharia jurídica que já usam o Claude.
**Diferencial:** honestidade operacional: cada etapa diz o que provou e o que não provou.
**Gancho:** a pergunta que todo advogado faz para uma IA: "essa decisão existe?"
**Frase mais forte:** "Reconhecer ≠ autenticar."
**UI real mostrada:** a frase sintética de `runtime/examples/engineering/citations.txt` e os `syntax_status` reais que o CLI devolveu nesta sessão (`ambiguous_year`, `decision_identity_unresolved`).
**Tom:** `polished` (sério, elegante), com a paleta Hum da LP: creme, menta, ciano, lilás, coral.
**Legenda para compartilhar:** ver `share-copy.txt`.

Formato: GIF 960×540 a 15 fps (sem áudio, por ser GIF) + MP4 1280×720 a 30 fps com os mesmos quadros.
Dados pessoais: só valores sintéticos (CPF de teste 111.444.777-35, ana@exemplo.com). Nenhum dado real.

## Storyboard (≈ 21 s)

| # | Tempo | Cena | Texto em tela |
|---|---|---|---|
| 1 | 0,0–3,2 | Gancho. Frase digitada em fundo creme; chip pêra aparece. | "O assistente citou STF RE 123.456." → chip "Essa decisão existe?" |
| 2 | 3,2–6,2 | Revelação. Sol nasce atrás do LZ; lockup e tagline. | "LexZenit · skill jurídica para o Claude" / "Raciocínio com lastro." |
| 3 | 6,2–9,4 | Estágio 1 · Evidência. Documento, carimbo SHA-256. | "1 · Evidência" / "O original fica guardado: hash, versão e localizador." |
| 4 | 9,4–13,2 | Estágio 2 · Citações. Spans acendem um a um com status. | "2 · Citações" / "Reconhecer ≠ autenticar." |
| 5 | 13,2–16,4 | Estágio 3 · Privacidade. Tarja cobre CPF e e-mail; vira pseudônimo. | "3 · Privacidade" / "Pseudônimo HMAC por caso. Nada sai da máquina." |
| 6 | 16,4–18,6 | Estágio 4 · Revisão. Selo de revisão. | "4 · Revisão" / "Nada sai sem um responsável." |
| 7 | 18,6–21,4 | Fecho. Números + comando de instalação + lockup. | "39 plugins · 176 workflows · 235 testes" / `/plugin install br-legal-engineering@legal-br` |

Transições: saída do conteúdo antigo, depois entrada do novo (sem crossfade de dois layouts).
