# AI Context Rules & Governance (AI Harness)

## Diretrizes Arquiteturais
- Runtime mínimo obrigatório: Python 3.11+.
- Type hints em 100% das funções, métodos e parâmetros.
- Padrão PEP 8 estrito e Single Responsibility Principle (SRP).
- Docstrings no padrão Google Style (Args, Returns, Raises).
- Logs estruturados utilizando o módulo nativo `logging`.
- Tratamento explícito de exceções via `TaskValidationError`.

## Proibições Rígidas (Guardrails)
- Proibido o uso de bibliotecas externas para manipulação de dados ou cálculos (ex.: pandas, numpy).
- Permitido externamente apenas o framework `pytest` para testes.
- Proibido persistir dados em arquivos locais (JSON, CSV) ou bancos de dados.
- Proibido modificar a suíte de testes `tests/test_harness.py`.
- Proibido gerar código sem a respectiva cobertura de testes.