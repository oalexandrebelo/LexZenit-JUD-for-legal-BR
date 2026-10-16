---
titulo: "Avaliação de Risco e Impacto do Sistema de IA"
uso: "Classificar o sistema de IA nos regimes aplicáveis e documentar riscos, supervisão humana e monitoramento"
base_legal: "LGPD art. 20; leis estaduais de IA aplicáveis; PL 2338/2023 (em tramitação: usar como referência, não como obrigação); EU AI Act (Reg. 2024/1689) quando houver alcance na UE; Colorado SB 24-205 e outras leis americanas quando o N2 for EUA; NIST AI RMF e ISO/IEC 42001 como boas práticas"
---
# Avaliação de Risco e Impacto — {{sistema}}

> MINUTA — REVISÃO PROFISSIONAL OBRIGATÓRIA. Projeto de lei não é lei: registrar a classificação pelo PL 2338/2023 só como preparação.

## 1. Ficha do sistema
- Finalidade: {{finalidade}}
- Usuários e pessoas afetadas: {{afetados}}
- Modelo(s) e fornecedor(es): {{modelos}}
- Dados de entrada e de treino/ajuste: {{dados}}
- Saídas e como são usadas: {{saidas}}
- Decisão que afeta interesses de pessoas? {{decisao_relevante}}

## 2. Classificação por regime
| Regime | Classificação | Fundamento | Obrigações decorrentes |
|---|---|---|---|
| LGPD (decisão automatizada) | {{lgpd_class}} | art. 20 | Revisão e informação sobre critérios |
| Lei estadual de IA ({{uf}}) | {{uf_class}} | {{uf_fund}} | {{uf_obrig}} |
| PL 2338/2023 (referência) | {{pl_class}} | {{pl_fund}} | Preparação |
| EU AI Act | {{eu_class}} | {{eu_fund}} | {{eu_obrig}} |
| EUA (estadual) | {{us_class}} | {{us_fund}} | {{us_obrig}} |

## 3. Riscos
| Risco | Quem é afetado | Probabilidade | Gravidade | Mitigação | Responsável |
|---|---|---|---|---|---|
| Viés e discriminação | {{r1_quem}} | | | {{r1_mit}} | |
| Alucinação ou erro factual | {{r2_quem}} | | | {{r2_mit}} | |
| Uso indevido (deepfake, fraude) | {{r3_quem}} | | | {{r3_mit}} | |
| Exposição de dados pessoais | {{r4_quem}} | | | {{r4_mit}} | |

## 4. Supervisão humana e contestação
{{supervisao}} · Canal de contestação: {{canal}}.

## 5. Transparência
Aviso de IA no ponto de uso: {{aviso}}. Rotulagem de conteúdo sintético: {{rotulagem}}.

## 6. Monitoramento e registros
Métricas: {{metricas}}. Logs (entrada, saída, versão do modelo, data): {{logs}}. Reavaliação: {{periodicidade}}.

## 7. Aprovação
{{aprovador}} · {{data}}
