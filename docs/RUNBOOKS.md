# Runbooks brasileiros de ponta a ponta

Estes são procedimentos operacionais de revisão, não jobs já integrados a portais. Os comandos correspondem às skills existentes; não acionam o runtime local automaticamente. O operador precisa fornecer documentos autorizados e revisão profissional.

## A. Edital municipal ITS

**Entrada:** edital, retificações, ETP, TR, anexos, planilhas, contrato, identificação do ente e calendário aplicável. Ausência de anexo é lacuna. Não inferir regime exclusivamente pela data do nome do arquivo.

Abrir `/br-legal-core:procurement-regime-router-br`: identificar ente, procedimento, objeto composto, jurisdição, regime e datas. Registrar separadamente engenharia, fornecimento, conectividade, software e operação. Não estender uma regra econômica de engenharia a todas as parcelas automaticamente.

Executar `/br-procurement:etp-tr-coherence` e `/br-legal-core:cross-document-consistency-br`: mapear objeto, quantidades, cronograma, critérios de aceitação, pagamentos, garantia e dependências; cada conflito precisa de dois localizadores. Uma remissão quebrada não é um requisito atendido.

Na trilha técnica, usar skills ITS específicas. Para metrologia, relacionar finalidade de fiscalização, modelo, equipamento, documentação e datas. Para vídeo, decompor interoperabilidade por função, cliente/dispositivo e firmware. Para backhaul e SLA, declarar ponto de medição, perdas, exclusões, janelas e responsabilidades. Não deduzir ilegalidade de marca ou ausência da palavra ONVIF.

Na trilha econômica, reconciliar quantidades/unidades/orçamento. `runtime/lexguard_core` calcula quando recebe dados suficientes; não verifica sozinho a autenticidade da planilha. Preço abaixo de um limiar produz triagem/diligência no enquadramento correto, não ordem de desclassificação. BDI é memória de cálculo e análise contextual, não comparação cega a teto.

Consolidar por requisito: fato, fonte, objeto, regra, exceção, evidência, incerteza, consequência proposta. Fazer revisão adversarial das impugnações materiais. A minuta só afirma tempestividade após calendário e evento confirmados; sem isso, marcar o campo pendente. Nenhuma skill protocola a peça.

**Aceite:** todos os achados materiais têm localizador; as normas estão identificadas e temporalmente justificadas; cálculos têm entradas/unidades; conflitos e anexos ausentes aparecem; revisão da versão final é registrada fora do plugin.

## B. Produto digital destinado também a crianças

**Entrada:** público e uso provável, funcionalidades, jornada, coleta/tratamento, fornecedores, monetização, termos, política e controles. Não transferir dados reais de menores ao modelo para “testar anonimização”.

Usar `/br-data-ai:digital-product`, `/br-data-ai:privacy-impact` e `/br-consumer:consumer-contract`. Conectar o domínio de vulnerabilidade conforme perfil. Identificar titulares, finalidades, base/condições aplicáveis, operações e agentes; separar padrão de privacidade da política declarada. Conferir proteção digital específica e regulamentação atual sem assumir que checkbox de responsável soluciona todo o regime.

Para publicidade e perfilamento, examinar mecanismo efetivo de segmentação, informação usada, inferências e controles. Para IA, registrar modelo, propósito, instruções, armazenamento, subprocessadores e revisão. Não prometer conformidade porque há pseudônimo ou API contratada.

**Saída:** mapa de tratamento, riscos por funcionalidade, evidências de implementação, mudanças propostas, limitações e revisão jurídica. A skill não testa app, sensor, biometria ou backend sem ferramentas e autorização disponíveis.

## C. Transição tributária em operação empresarial

**Entrada:** pessoa/atividade, operação, jurisdição, período, regime, documentos fiscais, créditos e premissas. Não aceitar “empresa de serviços” como classificação econômica suficiente.

Usar `/br-tax:consumption-transition`. Identificar tributos e regras de transição de cada período, LC 214/LC 227 e alterações pertinentes. Separar hipótese, incidência, base, alíquota, crédito, obrigação acessória e competência administrativa. Nada disso deriva apenas do nome comercial da empresa.

Usar `/br-tax:fiscal-defense` para rito e controvérsia; `/br-tax:tax-settlement` para transação. Não chamar a Lei 13.988 de lei geral do CARF nem presumir que acordo fiscal extingue todo passivo. Cálculo só com norma e parâmetros confirmados; não inventar percentual.

**Saída:** matriz por operação/período, fontes/versões, impacto e incertezas, documentos adicionais e minuta consultiva sujeita a revisão. O runtime não apura tributo automaticamente nesta versão.

## D. Contencioso com precedente citado

**Entrada:** peça, anexos, decisão, intimação, pretensão e referências. Acesso a peça não significa acesso a autos completos.

Extrair citações com `/br-legal-core:citation-extraction-br`, conferir existência/teor e aplicar `/br-legal-core:precedent-binding-audit-br`. Distinguir ementa, voto, decisão colegiada, tese, trânsito, modulação e aderência aos fatos. Não converter DataJud em fonte universal de inteiro teor.

Usar `/br-legal-core:legal-syllogism-br` para explicitar premissas, exceções e subsunção; o art. 489 do CPC não é teste automático universal de qualquer petição. Contraposição relevante deve indicar motivo concreto de distinção ou objeção, não produzir argumento fictício de parte adversa como fato.

Citação exata pode ser conferida no runtime. Resultado `semantic_support_verified=false` é preservado até revisão material; a ferramenta só confirmou texto e proveniência local.

**Saída:** matriz de proposições, fundamentos, provas, objeções e pedidos. Prazo, cabimento e estratégia continuam sujeitos a revisão profissional sobre fatos e regras aplicáveis.

## E. Ingestão autorizada e construção do grafo

Selecionar documento de uso autorizado; conservar original. Se PDF, extrair em ferramenta apropriada e registrar página/transformação antes de importar texto — o módulo local rejeita PDF diretamente. Identificar fonte sem promovê-la a revisada apenas por ter domínio oficial.

Ingerir, conferir hashes/localizadores, revisar conteúdo e informar intervalo aplicável quando normativo. Propor arestas com trecho literal; revisar a relação e a prova. Consultar data de aplicação e data-limite de conhecimento. Interromper conclusão dependente quando grafo/truncamento/snapshot não sustentar abrangência alegada.

**Saída:** conjunto de evidências, paths e limites. Não há parecer gerado automaticamente ou sincronização contínua.
