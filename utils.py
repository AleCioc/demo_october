import streamlit as st
import re


def atoi(text):
    return int(text) if text.isdigit() else text


def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [atoi(c) for c in re.split(r'(\d+)', text)]


def add_logo():
    # st.markdown(
    #     """
    #     <style>
    #         [data-testid="stSidebarNav"] {
    #             background-image: url('images/SWITCH-Logo.png');
    #             background-repeat: no-repeat;
    #             padding-top: 0px;
    #             background-position: 20px 20px;
    #         }
    #         [data-testid="stSidebarNav"]::before {
    #             content: "MENU";
    #             margin-left: 20px;
    #             margin-top: 50px;
    #             margin-bottom: 50px;
    #             font-size: 30px;
    #             position: relative;
    #             top: 100px;
    #         }
    #     </style>
    #     """,
    #     unsafe_allow_html=True,
    # )
    st.sidebar.image("images/SWITCH-Logo.png", use_column_width=True)
