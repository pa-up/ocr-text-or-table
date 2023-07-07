import streamlit as st
import os
from views import table_ocr

st.title('画像加工・認識アプリ')
st.write('\n')


def change_page(page):
    st.session_state["page"] = page

def page1():
    # 別ページへの遷移
    # st.button("page2はこちら >", on_click=change_page, args=["page2"])
    # 画像処理の実行
    page_subtitle = "<p></p><h3>表のOCR</h3>"
    table_ocr.main(page_subtitle)

def page2():
    # 別ページへの遷移
    st.button("表のOCRはこちら >", on_click=change_page, args=["page1"])
    # 画像処理の実行
    page_subtitle = "<p></p><h3>page2です</h3>"
    # view2.main(page_subtitle)



# メイン
def main():
    # セッション状態を取得
    session_state = st.session_state

    # セッション状態によってページを表示
    if "page" not in session_state:
        session_state["page"] = "page1"

    if session_state["page"] == "page1":
        page1()
    if session_state["page"] == "page2":
        page2()

if __name__ == "__main__":
    main()
