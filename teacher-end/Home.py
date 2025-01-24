import streamlit as st

st.set_page_config('Sys1')

def main():
    st.latex(r'''a + 1/y + \int a x^2 + y^2 \,dx''')
    

if __name__ == '__main__':
    main()