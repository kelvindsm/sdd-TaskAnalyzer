"""Módulo analítico TaskAnalyzer para métricas de produtividade."""

from datetime import datetime
import logging
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


class TaskValidationError(ValueError):
    """Exceção disparada para inconsistências cadastrais ou temporais em tarefas."""
    pass


def _parse_datetime(date_str: str) -> datetime:
    """Converte strings de datas em objetos datetime com suporte a ISO ou YYYY-MM-DD.

    Args:
        date_str: String de data a ser convertida.

    Returns:
        datetime: Objeto datetime correspondente.

    Raises:
        TaskValidationError: Se a data estiver em formato inválido.
    """
    try:
        if "T" in date_str or " " in date_str:
            return datetime.fromisoformat(date_str.replace("Z", ""))
        return datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, TypeError) as exc:
        raise TaskValidationError(f"Formato de data inválido: {date_str}") from exc


def _validar_tarefa(tarefa: Dict[str, Any]) -> None:
    """Valida a consistência de campos obrigatórios e integridade temporal da tarefa.

    Args:
        tarefa: Dicionário contendo os dados da tarefa.

    Raises:
        TaskValidationError: Se campos obrigatórios faltarem ou houver inconsistência.
    """
    campos_obrigatorios = ["id", "titulo", "prioridade", "data_criacao", "data_prazo", "status"]
    for campo in campos_obrigatorios:
        if campo not in tarefa or tarefa[campo] is None:
            raise TaskValidationError(f"Campo obrigatório ausente: {campo}")

    dt_criacao = _parse_datetime(tarefa["data_criacao"])
    dt_prazo = _parse_datetime(tarefa["data_prazo"])

    if dt_prazo < dt_criacao:
        raise TaskValidationError(f"Data de prazo não pode ser anterior à data de criação (ID {tarefa['id']}).")

    if tarefa.get("status") == "concluida":
        if not tarefa.get("data_conclusao"):
            raise TaskValidationError(f"Tarefa concluída sem data de conclusão (ID {tarefa['id']}).")

        dt_conclusao = _parse_datetime(tarefa["data_conclusao"])
        if dt_conclusao < dt_criacao:
            raise TaskValidationError(
                f"Data de conclusão não pode ser anterior à data de criação (ID {tarefa['id']})."
            )


def analyze_tasks(tarefas: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analisa um conjunto de tarefas e calcula métricas de produtividade e eficiência temporal.

    Args:
        tarefas: Lista de dicionários representando as tarefas a analisar.

    Returns:
        Dict[str, Any]: Métricas gerais e segmentadas por nível de prioridade.

    Raises:
        TaskValidationError: Se houver qualquer inconsistência nas datas informadas.
    """
    logger.info("Iniciando análise de lote com %d tarefa(s).", len(tarefas))

    prioridades_padrao = ["baixa", "media", "alta"]
    metricas_prioridade: Dict[str, Dict[str, Any]] = {
        p: {
            "total": 0,
            "concluidas": 0,
            "tempo_medio_conclusao_horas": 0.0,
            "tempo_medio_dias": 0.0,
            "taxa_atraso_percentual": 0.0,
        }
        for p in prioridades_padrao
    }

    if not tarefas:
        logger.warning("Lote vazio recebido. Retornando métricas zeradas.")
        return {
            "total_tarefas": 0,
            "total_concluidas": 0,
            "total_pendentes": 0,
            "tempo_medio_conclusao_horas": 0.0,
            "tempo_medio_conclusao_dias": 0.0,
            "taxa_atraso_percentual": 0.0,
            "metricas_por_prioridade": metricas_prioridade,
        }

    total_tarefas = len(tarefas)
    concluidas_count = 0
    atrasadas_count = 0
    soma_horas = 0.0

    duracoes_por_p: Dict[str, List[float]] = {p: [] for p in prioridades_padrao}
    atrasadas_por_p: Dict[str, int] = {p: 0 for p in prioridades_padrao}

    for t in tarefas:
        _validar_tarefa(t)
        p = str(t.get("prioridade", "")).lower()
        if p not in metricas_prioridade:
            metricas_prioridade[p] = {
                "total": 0,
                "concluidas": 0,
                "tempo_medio_conclusao_horas": 0.0,
                "tempo_medio_dias": 0.0,
                "taxa_atraso_percentual": 0.0,
            }
            duracoes_por_p[p] = []
            atrasadas_por_p[p] = 0

        metricas_prioridade[p]["total"] += 1

        if t.get("status") == "concluida":
            concluidas_count += 1
            metricas_prioridade[p]["concluidas"] += 1

            dt_criacao = _parse_datetime(t["data_criacao"])
            dt_prazo = _parse_datetime(t["data_prazo"])
            dt_conclusao = _parse_datetime(t["data_conclusao"])

            horas = (dt_conclusao - dt_criacao).total_seconds() / 3600.0
            soma_horas += horas
            duracoes_por_p[p].append(horas)

            if dt_conclusao > dt_prazo:
                atrasadas_count += 1
                atrasadas_por_p[p] += 1

    total_pendentes = total_tarefas - concluidas_count
    tempo_medio_horas = round(soma_horas / concluidas_count, 2) if concluidas_count > 0 else 0.0
    taxa_atraso_geral = round((atrasadas_count / concluidas_count) * 100.0, 2) if concluidas_count > 0 else 0.0

    for p, dados in metricas_prioridade.items():
        total_p_concluidas = dados["concluidas"]
        if total_p_concluidas > 0:
            media_h = sum(duracoes_por_p[p]) / total_p_concluidas
            dados["tempo_medio_conclusao_horas"] = round(media_h, 2)
            dados["tempo_medio_dias"] = round(media_h / 24.0, 2)
            dados["taxa_atraso_percentual"] = round((atrasadas_por_p[p] / total_p_concluidas) * 100.0, 2)

    logger.info("Análise concluída com sucesso. Concluídas: %d, Atrasadas: %d", concluidas_count, atrasadas_count)

    return {
        "total_tarefas": total_tarefas,
        "total_concluidas": concluidas_count,
        "total_pendentes": total_pendentes,
        "tempo_medio_conclusao_horas": tempo_medio_horas,
        "tempo_medio_conclusao_dias": round(tempo_medio_horas / 24.0, 2),
        "taxa_atraso_percentual": taxa_atraso_geral,
        "metricas_por_prioridade": metricas_prioridade,
    }


# Alias para garantir compatibilidade retroativa com a especificação da Fase 1
analisar_tarefas = analyze_tasks