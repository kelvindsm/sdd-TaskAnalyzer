"""Suíte de validação automatizada (Test Harness) para o módulo TaskAnalyzer."""

import pytest
from src.task_analyzer import analyze_tasks, TaskValidationError


def test_cenario_1_calculo_metricas_sucesso():
    """Valida o cálculo exato de totais, horas médias e taxa de atraso (Cenário 1)."""
    tarefas = [
        {
            "id": 101,
            "titulo": "Configurar pipeline CI/CD",
            "prioridade": "alta",
            "data_criacao": "2026-03-01",
            "data_prazo": "2026-03-05",
            "data_conclusao": "2026-03-04",
            "status": "concluida",
        },
        {
            "id": 102,
            "titulo": "Elaborar especificacao SDD",
            "prioridade": "media",
            "data_criacao": "2026-03-01",
            "data_prazo": "2026-03-03",
            "data_conclusao": "2026-03-05",
            "status": "concluida",
        },
        {
            "id": 103,
            "titulo": "Ajustar tipagem do codigo",
            "prioridade": "baixa",
            "data_criacao": "2026-03-02",
            "data_prazo": "2026-03-03",
            "data_conclusao": "2026-03-03",
            "status": "concluida",
        },
        {
            "id": 104,
            "titulo": "Monitoramento de logs",
            "prioridade": "baixa",
            "data_criacao": "2026-03-02",
            "data_prazo": "2026-03-10",
            "data_conclusao": None,
            "status": "pendente",
        },
    ]

    resultado = analyze_tasks(tarefas)

    assert resultado["total_tarefas"] == 4
    assert resultado["total_concluidas"] == 3
    assert resultado["total_pendentes"] == 1
    # Duração em dias: 3 dias (72h) + 4 dias (96h) + 1 dia (24h) = 192h / 3 = 64.0h (ou 2.67 dias)
    assert resultado["tempo_medio_conclusao_horas"] == pytest.approx(64.0, 0.1)
    assert resultado["tempo_medio_conclusao_dias"] == pytest.approx(2.67, 0.05)
    # Atrasos: Apenas a tarefa 102 atrasou (1 de 3 = 33.33%)
    assert resultado["taxa_atraso_percentual"] == pytest.approx(33.33, 0.05)

    # Métricas segmentadas por prioridade
    assert resultado["metricas_por_prioridade"]["alta"]["concluidas"] == 1
    assert resultado["metricas_por_prioridade"]["alta"]["taxa_atraso_percentual"] == 0.0
    assert resultado["metricas_por_prioridade"]["media"]["taxa_atraso_percentual"] == 100.0
    assert resultado["metricas_por_prioridade"]["baixa"]["total"] == 2
    assert resultado["metricas_por_prioridade"]["baixa"]["concluidas"] == 1


def test_cenario_2_data_invalida_dispara_excecao():
    """Valida se data_conclusao < data_criacao dispara TaskValidationError (Cenário 2)."""
    tarefas_com_erro = [
        {
            "id": 201,
            "titulo": "Tarefa com cronologia invertida",
            "prioridade": "alta",
            "data_criacao": "2026-03-10",
            "data_prazo": "2026-03-15",
            "data_conclusao": "2026-03-05",  # Anterior à criação!
            "status": "concluida",
        }
    ]

    with pytest.raises(TaskValidationError) as exc_info:
        analyze_tasks(tarefas_com_erro)

    assert "anterior" in str(exc_info.value).lower()


def test_casos_de_borda_lista_vazia():
    """Valida comportamento de resiliência ao receber lista vazia (retorna 0.0)."""
    resultado = analyze_tasks([])

    assert resultado["total_tarefas"] == 0
    assert resultado["total_concluidas"] == 0
    assert resultado["tempo_medio_conclusao_horas"] == 0.0
    assert resultado["taxa_atraso_percentual"] == 0.0


def test_casos_de_borda_apenas_pendentes():
    """Valida retorno seguro de médias quando há tarefas, mas nenhuma concluída."""
    tarefas_pendentes = [
        {
            "id": 301,
            "titulo": "Tarefa pendente 1",
            "prioridade": "media",
            "data_criacao": "2026-03-01",
            "data_prazo": "2026-03-05",
            "data_conclusao": None,
            "status": "pendente",
        }
    ]

    resultado = analyze_tasks(tarefas_pendentes)

    assert resultado["total_tarefas"] == 1
    assert resultado["total_concluidas"] == 0
    assert resultado["total_pendentes"] == 1
    assert resultado["tempo_medio_conclusao_horas"] == 0.0
    assert resultado["taxa_atraso_percentual"] == 0.0