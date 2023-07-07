import streamlit as st
from asprise_ocr.ocr import *
import pandas as pd
import base64
import re
import numpy as np
from forms import asprise_ocr_language_options


def st_upload_img_to_path(input_file_path: str = "input_img.jpg"):
    uploaded_file = st.file_uploader("画像またはPDFをアップロードしてください", type=["jpg", "jpeg", "png"])
    st.markdown(f"<p><br></p>", unsafe_allow_html=True)
    if uploaded_file:
        # アップロードされたファイルをディレクトリに保存
        with open(input_file_path, "wb") as file:
            file.write(uploaded_file.getbuffer())
        return uploaded_file

def df_to_csv_local_url(df: pd.DataFrame , output_csv_path: str = "output.csv"):
    """ データフレーム型の表をcsv形式でダウンロードできるURLを生成する関数 """
    # csvの生成＆ローカルディレクトリ上に保存（「path_or_buf」を指定したら、戻り値は「None」）
    df.to_csv(path_or_buf=output_csv_path, index=False, header=False, encoding='utf-8-sig')
    # ダウロードできるaタグを生成
    csv = df.to_csv(index=False, header=False, encoding='utf-8-sig')
    b64 = base64.b64encode(csv.encode('utf-8-sig')).decode()  # some strings <-> bytes conversions necessary here
    csv_local_href = f'<a href="data:file/csv;base64,{b64}" download={output_csv_path}>CSVでダウンロード</a>'
    return csv_local_href


def rtf_to_df(rtf_file, text_file):
    """ rtfファイル内の表をデータフレーム型に変換する関数 """
    def rtf_to_text(rtf_file, text_file):
        with open(rtf_file, 'r') as rtf:
            rtf_content = rtf.read()
        # RTFコードをプレーンテキストに変換する
        text_content = rtf_content.replace('\\par', '\n').encode('ascii', 'ignore').decode('ascii')
        with open(text_file, 'w') as text:
            text.write(text_content)
        return text_content
    
    def get_cell_text(text , before_end_pos):
        start_tag , end_tag , digits_pattern = r"\fs" , r"}\cell" , r'^(\d+)'
        start_index = before_end_pos + len(end_tag)
        start_pos = text.find(start_tag, start_index)
        end_pos = text.find(end_tag, start_pos)
        cell_text = text[start_pos + len(start_tag) : end_pos]
        match = re.match(digits_pattern, cell_text)
        first_digits_string = match.group(1)
        cell_text = cell_text[ len(first_digits_string) + 1 : ]
        return cell_text , end_pos

    def count_substring(string, substring):
        count , start = 0 , 0
        while True:
            index = string.find(substring, start)
            if index == -1:
                break
            count += 1
            start = index + len(substring)
        return count
    
    # rtfファイルからテキスト形式で取得
    text_content = rtf_to_text(rtf_file, text_file)

    start_tag , end_tag = r"{\trowd" , r"\row"
    rtf_rows_elements = []
    start_index = 0
    while True:
        start_pos = text_content.find(start_tag, start_index)
        if start_pos == -1:
            break
        end_pos = text_content.find(end_tag, start_pos)
        if end_pos == -1:
            break
        string_between_tags = text_content[start_pos + len(start_tag) : end_pos]
        rtf_rows_elements.append(string_between_tags)
        start_index = end_pos + len(end_tag)
    # 表全体の行数と列数を取得
    rows_count = len(rtf_rows_elements)
    col_tag = r"}\cell"
    cols_count = count_substring(rtf_rows_elements[0], col_tag)
    # 各セルの文字列をnumpyに格納
    table_cells = np.empty( (rows_count , cols_count) , dtype="object")
    for row in range(rows_count):
        before_end_pos = 0
        for col in range(cols_count):
            table_cells[row , col] , before_end_pos = get_cell_text(rtf_rows_elements[row] , before_end_pos)
            table_cells[row , col] = table_cells[row , col].replace('\n', '')
    df = pd.DataFrame(table_cells)
    return df



def main(page_subtitle="<h1>レシートのOCR</h1><p></p>"):
    """ 表から文字とその座標を認識するモジュール """
    st.write(f"<h3>{page_subtitle}</h3>" , unsafe_allow_html=True)

    # 言語の選択フォーム
    selected_language = st.selectbox("言語を選択してください", asprise_ocr_language_options[:, 0].tolist(), index=0)
    language_parameter = asprise_ocr_language_options[asprise_ocr_language_options[:, 0] == selected_language][0, 1]

    input_file_path = "media/img/input_img.jpg"
    output_rtf_path = "media/rtf/output_ocr.rtf"
    output_txt_path = "media/txt/output_ocr.txt"
    output_csv_path = "media/csv/output.csv"

    # 画像のアップロードフォーム
    uploaded_file = st_upload_img_to_path(input_file_path)

    if uploaded_file:
        ocr = Ocr()
        ocr.start_engine(language_parameter)   # deu, fra, por, spa - 30以上の言語に対応
        ocr.recognize(
            input_file_path,  # 画像ファイルのパス (gif, jpg, pdf, png, tif, etc.)
            OCR_PAGES_ALL,  # 選択されたページの領域座標のインデックス
            -1, -1, -1, -1,  # ページ全体ではなく、ページ上の領域を指定することも可能
            OCR_RECOGNIZE_TYPE_TEXT,  # 認識形式： TEXT、BARCODES、ALLのいずれか
            OCR_OUTPUT_FORMAT_RTF,  # 出力形式： TEXT or XML or PDF or RTF
            PROP_RTF_OUTPUT_FILE=output_rtf_path,  # 出力ファイルのパス
        )
        ocr.stop_engine()

        st.markdown(f"<h5>表のOCR結果</h5>", unsafe_allow_html=True)
        # RTFファイルから表をデータフレーム形式で取得
        df = rtf_to_df(output_rtf_path, output_txt_path)
        # データフレームをcsvに変換し、ダウンロードボタンを生成
        csv_local_href = df_to_csv_local_url(df, output_csv_path)
        st.markdown(csv_local_href , unsafe_allow_html=True)
        st.write(df)



if __name__ == '__main__':
    main()