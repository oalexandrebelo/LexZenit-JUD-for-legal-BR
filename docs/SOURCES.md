# Governança das fontes

## Inventário não é integração

189 registros: 24 páginas primárias identificadas (incluindo projetos dos autores e documentação técnica), 28 referências herdadas sem nova conferência e 137 sementes. Nenhum registro declara conector ou inteiro teor embarcado. Identificação de página não comprova leitura integral, vigência ou disponibilidade permanente. O nome Open-ECLI-Utils não identificado fica no registro de pesquisa com URL nula, e não recebe um endpoint inventado.

## Contrato para um conector futuro

Registrar instituição, jurisdição, dataset, documentação de acesso, autenticação, termos, direitos, limites, paginação, filtros temporais, tratamento de sigilo, semântica de 404/429/5xx, reprocessamento, conteúdo obtido, hash, horário observado, HTTP status/ETag, redirecionamentos, extrator e localizador.

Não inventar endpoint “api” por convenção. Não tratar portal público como autorização universal. Captcha ou bloqueio interrompe aquela rota autorizada; não construir evasão. Autorizações de acesso não são transferíveis entre tribunais.

Normas técnicas licenciadas e bases privadas exigem direitos de leitura, armazenamento, embedding, reprodução e compartilhamento examinados separadamente. O pacote não redistribui NBR, doutrina comercial, autos sigilosos ou bases policiais.

## Níveis de evidência propostos

`identified` → `retrieved` → `integrity_checked` → `text_extracted` → `citation_located` → `content_reviewed` → `legal_application_reviewed`.

Esses níveis são governança para o serviço corporativo. O núcleo local implementa ingestão, integridade, citação e **atestação declarada**, não todos os estágios autenticados. Não reutilizar um booleano `verified` para tudo. Ementa não prova a abrangência integral do julgamento.

## Atualização, cache e invalidação

Snapshot histórico pode sustentar recorte histórico. Não pode certificar atualidade após falha de sincronização. Fonte indisponível mantém a conclusão correspondente pendente; partes independentes podem prosseguir. O catálogo não agenda monitoramento.

A ingestão futura precisa de cursor/checkpoint por origem, backoff com jitter, respeito a Retry-After, fila limitada, deduplicação por versão e reconciliação. Alteração normativa deve invalidar dependências de achados, minutas e revisões, não apenas embeddings. A invalidação não apaga histórico.

## Sigilo nas consultas públicas

Não usar autos, identificadores ou segredos como consulta sem base/autorização apropriada. Pesquisar referências normativas públicas e assunto minimizado. O host/LLM/browser pode transmitir dados; instruções do plugin não implementam isolamento.

## Homologação por origem

Exigir respostas reais autorizadas, teste de paginação incompleta/duplicada, mudança de esquema, bloqueio, timeout, backfill, direitos, localizadores e comparação de recall com inventário manual. Publicar data e limites. 100 URLs não equivalem a 100 conectores.
