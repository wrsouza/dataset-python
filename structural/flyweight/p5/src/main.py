"""Streamlit application: Glyph Font Renderer (Flyweight pattern).

Composition root: builds the GlyphFactoryImpl (concrete infrastructure) and
injects it into the use cases (application layer), which depend only on the
GlyphFactory protocol (DIP).
"""

from __future__ import annotations

import streamlit as st

from fontrender.application.use_cases import (
    GetCacheStatisticsUseCase,
    RenderTextUseCase,
)
from fontrender.domain.entities import FontStyle, PositionedGlyph
from fontrender.infrastructure.font_metrics import FONT_METRIC_PROFILES
from fontrender.infrastructure.glyph_factory import GlyphFactoryImpl

AVAILABLE_WEIGHTS = ["regular", "bold", "light"]
DEFAULT_TEXT = "the quick brown fox jumps over the lazy dog\nthe quick brown fox"
PIXELS_PER_LAYOUT_UNIT = 1


@st.cache_resource
def get_factory() -> GlyphFactoryImpl:
    """Build the GlyphFactoryImpl once per Streamlit session — the shared pool."""
    return GlyphFactoryImpl()


def render_layout_preview(positioned_glyphs: list[PositionedGlyph]) -> None:
    """Render a simple textual/visual preview of the computed glyph layout."""
    if not positioned_glyphs:
        st.info("Digite um texto para visualizar o layout.")
        return

    max_y = max(p.y for p in positioned_glyphs)
    lines: dict[int, list[PositionedGlyph]] = {}
    for positioned in positioned_glyphs:
        lines.setdefault(positioned.y, []).append(positioned)

    for y in sorted(lines):
        ordered = sorted(lines[y], key=lambda p: p.x)
        st.text("".join(p.glyph.char for p in ordered))

    st.caption(f"{len(positioned_glyphs)} glyphs posicionados, altura total {max_y}px")


def render_glyph_table(positioned_glyphs: list[PositionedGlyph]) -> None:
    """Show extrinsic (x, y) vs intrinsic (shared Glyph id) data per occurrence."""
    rows = [
        {
            "char": repr(p.glyph.char),
            "x": p.x,
            "y": p.y,
            "glyph_id (flyweight)": id(p.glyph),
            "width": p.glyph.width,
            "height": p.glyph.height,
        }
        for p in positioned_glyphs[:50]
    ]
    st.dataframe(rows, width="stretch")
    if len(positioned_glyphs) > 50:
        st.caption("Exibindo as primeiras 50 ocorrências de glyph.")


def render_statistics(total_characters: int, factory: GlyphFactoryImpl) -> None:
    """Show cache hit/miss stats and the memory economy of the Flyweight pool."""
    stats_use_case = GetCacheStatisticsUseCase(factory=factory)
    stats = stats_use_case.execute(total_characters)

    col_total, col_unique, col_hits, col_misses = st.columns(4)
    col_total.metric("Total de caracteres", stats.total_characters)
    col_unique.metric("Glyphs únicos (Flyweights)", stats.unique_glyphs)
    col_hits.metric("Cache hits", stats.cache_hits)
    col_misses.metric("Cache misses", stats.cache_misses)

    st.progress(min(1.0, stats.savings_percentage / 100))
    st.success(
        f"Economia de criação de objetos: {stats.savings_percentage:.1f}% "
        f"— razão de compartilhamento {stats.sharing_ratio:.1f}:1"
    )


def main() -> None:
    """Streamlit entry point."""
    st.set_page_config(page_title="Glyph Font Renderer", layout="wide")
    st.title("Glyph Font Renderer — Flyweight Pattern")
    st.caption(
        "Cada caractere de uma fonte (char + família + tamanho + peso) tem um "
        "único Glyph (Flyweight) compartilhado entre todas as ocorrências no "
        "texto. A posição (x, y) de cada ocorrência é estado extrínseco, "
        "guardado apenas no PositionedGlyph."
    )

    factory = get_factory()

    with st.sidebar:
        st.header("Configuração da fonte")
        font_family = st.selectbox(
            "Família", options=sorted(FONT_METRIC_PROFILES.keys())
        )
        size = st.slider("Tamanho", min_value=8, max_value=72, value=16)
        weight = st.selectbox("Peso", options=AVAILABLE_WEIGHTS)
        if st.button("Limpar cache de Glyphs"):
            factory.reset()

    text = st.text_area("Texto a renderizar", value=DEFAULT_TEXT, height=120)

    style = FontStyle(font_family=font_family, size=size, weight=weight)
    render_use_case = RenderTextUseCase(factory=factory)
    positioned_glyphs = render_use_case.execute(text, style)

    total_characters = len(text.replace("\n", ""))

    st.subheader("Layout renderizado")
    render_layout_preview(positioned_glyphs)

    st.subheader("Estatísticas do Flyweight Pool")
    render_statistics(total_characters, factory)

    st.subheader("Detalhe das ocorrências (PositionedGlyph)")
    render_glyph_table(positioned_glyphs)


if __name__ == "__main__":
    main()
