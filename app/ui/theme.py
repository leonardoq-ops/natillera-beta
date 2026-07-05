"""Injects the Natillera Aesthetics Guide design system as a single
<style> block. Call once at the very top of streamlit_app.py, before
st.navigation().run(), so every page (including the login page) picks
it up - Streamlit's markdown-injected CSS is global once emitted into
the DOM, it doesn't need to be repeated per-page.
"""
import streamlit as st

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:wght@400;700&family=DM+Sans:wght@400;500;600&family=DM+Mono:wght@400;600&display=swap');

:root {
  --color-navy: #1A2B4A;
  --color-oro: #C9942A;
  --color-oro-hover: #A67C1E;
  --color-teal: #1D9E75;
  --color-red: #8B2020;
  --color-green: #2D7A3C;
  --color-gris-dark: #3D4E61;
  --color-gris-light: #D1CDBD;
  --color-gray-bg: #E8E6E1;
  --color-white: #FFFFFF;
}

h1, h2, h3, .nat-header,
h1 span, h2 span, h3 span,
[data-testid="stHeadingWithActionElements"] h1,
[data-testid="stHeadingWithActionElements"] h2,
[data-testid="stHeadingWithActionElements"] h3 { font-family: 'Fraunces', serif !important; }
body, .nat-body { font-family: 'DM Sans', sans-serif; }
.nat-number, .nat-mono { font-family: 'DM Mono', monospace; }

.nat-the-number {
  font-family: 'DM Mono', monospace;
  font-size: 48px;
  font-weight: 700;
  color: var(--color-oro);
  text-align: center;
  animation: nat-pulse 2s ease-in-out infinite;
}
@media (max-width: 767px) { .nat-the-number { font-size: 36px; } }
@keyframes nat-pulse { 0%, 100% { opacity: 0.95; } 50% { opacity: 1.0; } }

.nat-card {
  border-radius: 12px;
  padding: 24px;
  max-width: 1400px;
  background: linear-gradient(135deg, #1A2B4A 0%, #0F1C2E 100%);
  box-shadow: 0 4px 12px rgba(26,43,74,0.15),
              inset 0 1px 2px rgba(255,255,255,0.1),
              inset 0 -2px 4px rgba(0,0,0,0.2);
  border: 1px solid rgba(201,148,42,0.1);
  margin-bottom: 12px;
}

.nat-badge {
  display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px;
  border-radius: 8px; font-family: 'DM Sans', sans-serif; font-weight: 600; font-size: 14px;
}
.nat-badge-teal  { background: rgba(29,158,117,0.15); color: var(--color-teal); }
.nat-badge-red   { background: rgba(139,32,32,0.15); color: var(--color-red); }
.nat-badge-green { background: rgba(45,122,60,0.15); color: var(--color-green); }

.stButton>button {
  min-height: 44px;
  background-color: var(--color-oro);
  color: var(--color-white);
  border: none;
  transition: all 0.2s ease-out;
}
.stButton>button:hover { background-color: var(--color-oro-hover); transform: scale(1.02); }
</style>
"""

def inject_theme():
    st.markdown(_CSS, unsafe_allow_html=True)


def the_number_html(monto: int) -> str:
    """Returns the HTML for THE NUMBER. Note: a <script>-based count-up
    animation was tried here and removed - st.markdown(unsafe_allow_html=True)
    inserts HTML via innerHTML, and browsers never execute <script> tags
    inserted that way, so the counter silently never ran (stuck at $0).
    The CSS opacity pulse (in _CSS above) doesn't need script execution
    and still applies."""
    formatted = f"${monto:,}".replace(",", ".")
    return f'<div class="nat-the-number">{formatted}</div>'
