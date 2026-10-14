# Especificação Técnica SDD — TaskAnalyzer

## 1. Contrato de Entrada
Recebe `tarefas: list[dict]`, onde cada item possui:
- `id`: int | str
- `titulo`: str
- `prioridade`: "baixa" | "media" | "alta"
- `data_criacao`: str (ISO YYYY-MM-DD ou YYYY-MM-DDTHH:MM:SS)
- `data_prazo`: str (ISO YYYY-MM-DD ou YYYY-MM-DDTHH:MM:SS)
- `data_conclusao`: str | None
- `status`: "concluida" | "pendente"

## 2. Contrato de Saída
Retorna `dict` estruturado com:
- `total_tarefas`: int
- `total_concluidas`: int
- `total_pendentes`: int
- `tempo_medio_conclusao_horas`: float (2 casas decimais)
- `taxa_atraso_percentual`: float (2 casas decimais)
- `metricas_por_prioridade`: dict ("baixa", "media", "alta")

## 3. Regras de Exceção e Borda
- `data_conclusao < data_criacao` -> Lança `TaskValidationError`.
- Entradas vazias ou sem tarefas concluídas -> Retorna médias como 0.0 sem erros não tratados.