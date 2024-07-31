import streamlit as st

from app.dashboard import main, set_page_style

def run_app():
    set_page_style()
    main()

if __name__ == "__main__":
    run_app()