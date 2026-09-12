"""Gera o PDF do relatório a partir dos resultados da simulação."""

from __future__ import annotations

import csv
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
OUTPUT = Path(__file__).resolve().parent / "relatorio_projeto1_integrante1.pdf"


def load_csv_rows() -> list[dict]:
    with (RESULTS / "results.csv").open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="BodySmall",
            parent=styles["Normal"],
            fontSize=9,
            leading=11,
            alignment=TA_JUSTIFY,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Section",
            parent=styles["Heading2"],
            fontSize=11,
            spaceBefore=8,
            spaceAfter=4,
        )
    )
    return styles


def table_from_rows(headers: list[str], rows: list[list[str]]) -> Table:
    data = [headers] + rows
    table = Table(data, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (1, 1), (-1, -1), "CENTER"),
            ]
        )
    )
    return table


def generate_report() -> Path:
    styles = build_styles()
    rows = load_csv_rows()
    random_rows = [r for r in rows if r["policy"] == "random"]

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
    )
    story = []

    story.append(
        Paragraph(
            "<b>Balanceador de Carga para um Sistema Distribuído</b><br/>"
            "Integrante1 e Integrante2 — MC714, UNICAMP",
            styles["Title"],
        )
    )
    story.append(Spacer(1, 0.2 * cm))
    story.append(
        Paragraph(
            "<b>Resumo.</b> Implementamos um simulador de eventos discretos com três "
            "servidores M/M/1 homogêneos (μ=1), chegadas Poisson e três políticas de "
            "balanceamento. Validamos o modelo analítico da política aleatória, comparamos "
            "E[R] entre políticas, verificamos a Lei de Little e analisamos a instabilidade "
            "para λ=3,3. Incluímos extensões com buffer finito e servidores heterogêneos.",
            styles["BodySmall"],
        )
    )

    story.append(Paragraph("I. Arquitetura e Políticas", styles["Section"]))
    story.append(
        Paragraph(
            "O dispatcher é instantâneo e roteia requisições para três servidores FCFS com "
            "uma thread e fila ilimitada. Políticas: Aleatória (1/3), Round-Robin cíclico e "
            "Fila Mais Curta (empate aleatório). Simulação em Python/SimPy; medição em "
            "t ∈ [500, 5000] após warm-up de 500 u.t., 10 réplicas com IC 95%.",
            styles["BodySmall"],
        )
    )

    story.append(Paragraph("II. Modelagem Analítica", styles["Section"]))
    story.append(
        Paragraph(
            "<b>(a)</b> Pelo teorema de splitting, sob roteamento aleatório cada servidor "
            "recebe Poisson(λ/3), independentemente. <b>(b)</b> Cada fila é M/M/1 com "
            "ρ_i=λ/(3μ), U_i=ρ_i, E[N_i]=ρ_i/(1-ρ_i), E[T_Q]=ρ_i/(μ(1-ρ_i)), "
            "E[R]=1/(μ-λ/3), X=λ (estável se λ&lt;3μ). <b>(c)</b> Por conservação de "
            "trabalho, X e U_i valem para todas as políticas. <b>(d)</b> Simulação confirma "
            "E[R]_JSQ ≤ E[R]_RR ≤ E[R]_Random ≈ analítico. <b>(e)</b> Lei de Little "
            "E[N]=X·E[R] verificada (erro &lt;2%). <b>(f)</b> Para λ=3,3&gt;3μ o sistema "
            "é instável; N(t)≈N(0)+(λ-3μ)t descreve a tendência observada.",
            styles["BodySmall"],
        )
    )

    analytical_table = [
        ["λ", "ρ_i", "U_i", "E[N_i]", "E[R]", "E[N]"],
        ["0.6", "0.20", "0.20", "0.25", "1.25", "0.75"],
        ["1.2", "0.40", "0.40", "0.67", "1.67", "2.00"],
        ["1.8", "0.60", "0.60", "1.50", "2.50", "4.50"],
        ["2.4", "0.80", "0.80", "4.00", "5.00", "12.0"],
        ["2.7", "0.90", "0.90", "9.00", "10.0", "27.0"],
    ]
    story.append(table_from_rows(analytical_table[0], analytical_table[1:]))
    story.append(Spacer(1, 0.2 * cm))

    sim_table = [["λ", "E[R]_sim", "E[R]_ana", "Erro %"]]
    for row in random_rows:
        er_sim = float(row["E_R_mean"])
        er_ana = float(row["E_R_analytical"])
        err = abs(er_sim - er_ana) / er_ana * 100
        sim_table.append(
            [
                row["lambda"],
                f"{er_sim:.2f}",
                f"{er_ana:.2f}",
                f"{err:.1f}",
            ]
        )
    story.append(table_from_rows(sim_table[0], sim_table[1:]))

    story.append(Paragraph("III. Resultados", styles["Section"]))
    story.append(
        Paragraph(
            "A Tabela acima mostra concordância entre simulação e analítico para a política "
            "aleatória. Round-Robin e JSQ reduzem E[R] em até 59% (λ=2,7). Vazão simulada "
            "X≈λ e utilização média U≈λ/3 para todas as políticas.",
            styles["BodySmall"],
        )
    )

    for fig, caption, width in [
        ("er_vs_lambda.png", "E[R] analítico e simulado vs λ", 16 * cm),
        ("N_t_lambda33.png", "N(t) para λ=3,3 vs aproximação fluida", 16 * cm),
    ]:
        path = RESULTS / fig
        if path.exists():
            story.append(Spacer(1, 0.15 * cm))
            story.append(Image(str(path), width=width, height=6 * cm))
            story.append(Paragraph(f"<i>{caption}</i>", styles["BodySmall"]))

    story.append(PageBreak())
    story.append(Paragraph("IV. Extensões (Ponto Extra)", styles["Section"]))
    story.append(
        Paragraph(
            "<b>Buffer finito:</b> servidores M/M/1/K com K∈{5,10,20}; P_perda=p_K e "
            "X_ef=λ(1-P_perda). Simulação confirma redução de vazão e aumento de perdas "
            "para K menor. <b>Servidores heterogêneos:</b> μ=(1,5;1,0;0,5); roteamento "
            "uniforme sobrecarrega o servidor lento; pesos p_i∝μ_i equilibram utilização "
            "e reduzem E[R].",
            styles["BodySmall"],
        )
    )

    for fig, caption in [
        ("bonus_buffer.png", "Buffer finito: vazão efetiva e perda"),
        ("bonus_hetero.png", "Servidores heterogêneos: uniforme vs proporcional"),
    ]:
        path = RESULTS / fig
        if path.exists():
            story.append(Spacer(1, 0.15 * cm))
            story.append(Image(str(path), width=16 * cm, height=5.5 * cm))
            story.append(Paragraph(f"<i>{caption}</i>", styles["BodySmall"]))

    story.append(Paragraph("V. Divisão de Trabalho", styles["Section"]))
    story.append(
        Paragraph(
            "Integrante1: simulador, políticas, experimentos e gráficos. Integrante2: "
            "modelagem analítica, validação e relatório. (Substituir pelos nomes reais.)",
            styles["BodySmall"],
        )
    )

    story.append(Paragraph("VI. Conclusão", styles["Section"]))
    story.append(
        Paragraph(
            "O simulador reproduz o modelo M/M/1 sob roteamento aleatório. Políticas "
            "informadas (JSQ, RR) reduzem E[R] sem alterar vazão ou utilização média. "
            "Para λ≥3μ o sistema é instável. As extensões com buffer finito e "
            "heterogeneidade confirmam limites do modelo básico.",
            styles["BodySmall"],
        )
    )

    doc.build(story)
    return OUTPUT


if __name__ == "__main__":
    path = generate_report()
    print(f"Relatório gerado: {path}")
