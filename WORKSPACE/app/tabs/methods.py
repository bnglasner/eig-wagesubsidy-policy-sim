"""
Tab 3: Public-facing methods.

Renders WORKSPACE/docs/pipeline_methodology_public.md in a structured,
easy-to-read format with quick navigation.
"""
from __future__ import annotations

from pathlib import Path

import streamlit as st


_HERE = Path(__file__).resolve()
_PROJECT = _HERE.parents[3]
_METHODS_DOC = _PROJECT / "WORKSPACE" / "docs" / "pipeline_methodology_public.md"


def _parse_sections(md_text: str) -> list[tuple[str, str]]:
    """Return (section_title, section_markdown) tuples for top-level ## sections."""
    parts = md_text.split("\n## ")
    sections: list[tuple[str, str]] = []
    for i, chunk in enumerate(parts):
        if i == 0:
            continue
        lines = chunk.splitlines()
        if not lines:
            continue
        title = lines[0].strip()
        body = "\n".join(lines[1:]).strip()
        sections.append((title, body))
    return sections


def render() -> None:
    st.header("Methods")
    st.caption(
        "This tab documents the full pipeline methodology, from policy design to ORG eligibility, "
        "PolicyEngine interaction modeling, and output construction."
    )

    if not _METHODS_DOC.exists():
        st.warning(
            f"Methodology document not found at:\n\n`{_METHODS_DOC}`\n\n"
            "Expected file: `WORKSPACE/docs/pipeline_methodology_public.md`"
        )
        return

    md_text = _METHODS_DOC.read_text(encoding="utf-8")
    sections = _parse_sections(md_text)
    if not sections:
        st.warning("Methodology file was found but no `##` sections could be parsed.")
        st.markdown(md_text)
        return

    section_titles = [s[0] for s in sections]
    selected = st.selectbox("Jump to section", section_titles)

    st.subheader(selected)
    selected_body = next(body for title, body in sections if title == selected)
    st.markdown(selected_body)

    st.divider()
    st.subheader("Full Methodology")
    for title, body in sections:
        with st.expander(title, expanded=False):
            st.markdown(body)

    st.download_button(
        label="Download Methodology Markdown",
        data=md_text,
        file_name="pipeline_methodology_public.md",
        mime="text/markdown",
    )
