import streamlit as st


def cargar_estilos() -> None:
    """
    Carga los estilos visuales de las tarjetas de OT.
    """
    st.markdown(
        """
        <style>
        [class*="st-key-ot_card_"] {
            border-radius: 0.75rem;
            padding: 0.35rem 0.65rem;
            transition:
                background-color 0.2s ease,
                border-color 0.2s ease;
        }

        [class*="st-key-ot_card_produccion_"] {
            background-color: rgba(46, 160, 67, 0.12);
            border: 1px solid rgba(46, 160, 67, 0.38);
        }

        [class*="st-key-ot_card_pausada_"] {
            background-color: rgba(120, 120, 120, 0.13);
            border: 1px solid rgba(120, 120, 120, 0.36);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
