import streamlit as st
import io
import numpy as np
from PIL import Image
import os
from views import easy_st, google_api
from forms import drive_ocr_language_options , google_translate_language_options
from deep_translator import GoogleTranslator


def display_free_size_img(img_np):
    with st.expander("表示画像のサイズを調整"):
       img_size = st.slider("", min_value=10, max_value=600, value=300, step=30)
    st.image(img_np, width=img_size)
    st.write("<p><br></p>", unsafe_allow_html=True)



def main(page_subtitle="<h1>テキストのOCR</h1><p></p>"):
    st.write(page_subtitle, unsafe_allow_html=True)

    # 言語の選択フォーム
    selected_language = st.selectbox("言語を選択してください", drive_ocr_language_options[:, 0].tolist(), index=0)
    language_parameter = drive_ocr_language_options[drive_ocr_language_options[:, 0] == selected_language][0, 1]
    # st.write("日本語（縦書き）の場合、2桁以上の半角数字は正しく認識されない可能性があります。", unsafe_allow_html=True)
    st.write("<p></p>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("画像またはPDFをアップロードしてください", type=["jpg", "jpeg", "png", "pdf"])
    st.markdown("<p><br></p>", unsafe_allow_html=True)

    if uploaded_file:
        output_pdf_path = "media/pdf/ocr.pdf"
        output_txt_path = "media/txt/ocr_output.txt"
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        if file_extension in ['.pdf']:
            input_file_path = output_pdf_path
        else:
            st.write("<h5>アップロードされた画像</h5>", unsafe_allow_html=True)
            img_np = np.array(Image.open(uploaded_file))[..., :3]
            display_free_size_img(img_np)
            input_file_path = "media/img/ocr" + file_extension

        # アップロードされたファイルをディレクトリに保存
        with open(input_file_path, "wb") as file:
            file.write(uploaded_file.getbuffer())
        
        # OCRを実行
        ocr_text_html_list = []
        st.write("<p></p>", unsafe_allow_html=True)
        st.write("<h4>OCR結果</h4>", unsafe_allow_html=True)

        google_drive_ocr = google_api.ManipulateGoogleDriveAPI()
        ocr_text = google_drive_ocr.drive_ocr(
            input_file_path = input_file_path , output_txt_path = output_txt_path ,
            output_pdf_path = output_pdf_path , language_parameter = language_parameter ,
        )

        # pdfのダウンロードボタンを表示
        with open(output_pdf_path, "rb") as f:
            st.download_button("PDFをダウンロード", f.read(), file_name="ocr.pdf")
        
        # テキストのみをhtmlで取得
        ocr_text_html = ocr_text.replace('\n', '<br>')
        ocr_text_html_list.append(ocr_text_html)
        styled_text = f'<div style="background-color: #f0f2f6; padding: 20px; border-radius: 5px; cursor: text; " contenteditable="true">{ocr_text_html}</div>'
        st.markdown(styled_text, unsafe_allow_html=True)
        st.write("<p><br></p>", unsafe_allow_html=True)

        # 翻訳結果を表示
        st.write("<h5>OCR結果を翻訳</h1>", unsafe_allow_html=True)
        output_language = st.selectbox("翻訳後の言語を選択してください", google_translate_language_options[:, 0].tolist() , index=1)
        output_parameter = google_translate_language_options[google_translate_language_options[:, 0] == output_language][0, 1]
        translated_text = GoogleTranslator(source="auto" ,target=output_parameter).translate(ocr_text)
        translated_text = translated_text.replace('\n', '<br>')
        styled_text = f'<div style="background-color: #f0f2f6; padding: 20px; border-radius: 5px; cursor: text; " contenteditable="true">{translated_text}</div>'
        st.markdown(styled_text, unsafe_allow_html=True)

if __name__ == '__main__':
    main()
