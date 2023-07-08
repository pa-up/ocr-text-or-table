import streamlit as st
import os
from views import text_ocr, table_ocr

st.title('画像加工・認識アプリ')
st.write('\n')


def change_page(page):
    st.session_state["page"] = page

def text_ocr_page():
    # 別ページへの遷移
    st.button("表のOCR" + "はこちら >", on_click=change_page, args=["table_ocr_page"])
    # 画像処理の実行
    page_subtitle = "<p></p><h3>テキストのOCR</h3>"
    text_ocr.main(page_subtitle)

def table_ocr_page():
    # 別ページへの遷移
    st.button("テキストのOCR" + "はこちら >", on_click=change_page, args=["text_ocr_page"])
    # 画像処理の実行
    page_subtitle = "<p></p><h3>表のOCR</h3>"
    table_ocr.main(page_subtitle)


# メイン
def main():
    # セッション状態を取得
    session_state = st.session_state

    # セッション状態によってページを表示
    if "page" not in session_state:
        session_state["page"] = "text_ocr_page"

    if session_state["page"] == "text_ocr_page":
        text_ocr_page()
    if session_state["page"] == "table_ocr_page":
        table_ocr_page()

if __name__ == "__main__":
    main()
