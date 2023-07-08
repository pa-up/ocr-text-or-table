import streamlit as st
from ocr.asprise_ocr import *
from ocr import assist_ocr
import pandas as pd
import re
import numpy as np
import cv2
from forms import asprise_ocr_language_options
from views import easy_st, google_api


def add_rectangle_with_text(input_img_list: list, divide_square_path: str):
    """
    リストに格納された画像を文字列が描かれた長方形を挟んで縦に連結する関数
    parameters :
        input_img_list (list) : List[np.ndarray , np.ndarray , ...]
        text (str) : 長方形の内部に描く文字列
    """
    def resize_image_with_width(image: np.ndarray, target_width):
        # 元の画像のサイズを取得
        height, width = image.shape[:2]
        # アスペクト比を計算
        aspect_ratio = height / width
        # ターゲットの横の長さに基づいてリサイズ
        target_height = int(aspect_ratio * target_width)
        resized_image = cv2.resize(image, (target_width, target_height))
        return resized_image

    result_img_list = []
    for input_img in input_img_list:
        # 長方形のサイズと位置を計算
        height, width, _ = input_img.shape
        # 長方形の描画
        divide_square_img = cv2.cvtColor(cv2.imread(divide_square_path) , cv2.COLOR_BGR2RGB)
        divide_square_img = resize_image_with_width(divide_square_img , width)
        # 元の画像と長方形を結合
        result_img = np.vstack((input_img, divide_square_img ))
        result_img_list.append(result_img)
    
    base_size_width = result_img_list[0].shape[1]
    before_img = result_img_list[0]
    for loop in range(len(result_img_list)):
        if loop < len(result_img_list) - 1:
            current_img = result_img_list[loop + 1]
            current_img = resize_image_with_width(current_img, base_size_width)
            completed_result_img = np.vstack((before_img, current_img))
            before_img = completed_result_img
    
    return completed_result_img


    
def main(page_subtitle="<h1>表のOCR</h1><p></p>"):
    st.write(f"<h3>{page_subtitle}</h3>" , unsafe_allow_html=True)

    # 言語の選択フォーム
    selected_language = st.selectbox("言語を選択してください", asprise_ocr_language_options[:, 0].tolist(), index=0)
    language_parameter = asprise_ocr_language_options[asprise_ocr_language_options[:, 0] == selected_language][0, 1]

    input_file_path = "media/img/input_img.jpg"
    output_xml_path = "media/xml/output_ocr.xml"
    cell_img_base_path = "media/img/cell_img"
    output_csv_path = "media/csv/table_ocr.csv"

    # 画像のアップロードフォーム
    input_rgb_img: np.ndarray = easy_st.st_upload_img_to_path(input_file_path)
    if isinstance(input_rgb_img,  np.ndarray):
        ocr = Ocr()
        ocr.start_engine(language_parameter)   # deu, fra, por, spa - 30以上の言語に対応
        xml_text = ocr.recognize(
            input_file_path,  # 画像ファイルのパス (gif, jpg, pdf, png, tif, etc.)
            OCR_PAGES_ALL,  # 選択されたページの領域座標のインデックス
            -1, -1, -1, -1,  # ページ全体ではなく、ページ上の領域を指定することも可能
            OCR_RECOGNIZE_TYPE_TEXT,  # 認識形式： TEXT、BARCODES、ALLのいずれか
            OCR_OUTPUT_FORMAT_XML,  # 出力形式： TEXT or XML or PDF or RTF
            # PROP_XML_OUTPUT_FILE=output_xml_path,  # 出力ファイルのパス(TEXT or XML は戻り値で取得)
        )
        ocr.stop_engine()

        # ファイルにXMLデータを書き込む
        with open(output_xml_path, 'w') as f:
            f.write(xml_text)

        st.markdown(f"<h5>表のOCR結果</h5>", unsafe_allow_html=True)
        # 表のセルの切り抜き画像を全て取得
        cells_imgs: np.ndarray  = assist_ocr.xml_to_cells_image(input_rgb_img , output_xml_path)
        table_rows , table_cols = cells_imgs.shape[0] , cells_imgs.shape[1]
        # セルごとにOCR
        cell_number = 0
        cells_ocr_text = np.empty( (table_rows , table_cols) , dtype="object" )
        for col in range(table_cols):
            same_cols_imgs_list = []
            for row in range(table_rows):
                # セルの画像を保存
                cell_img: np.ndarray = cells_imgs[row , col]
                # 列ごとに表の画像を分割
                same_cols_imgs_list.append(cell_img)
                cell_number += 1
            
            # 同じ列の画像として連結
            divide_square_path = "static/img/divide_cell.png"
            same_cols_imgs: np.ndarray = add_rectangle_with_text(same_cols_imgs_list , divide_square_path)
            input_same_cols_img_path = f"media/img/cell_{col}.jpg"
            cv2.imwrite(input_same_cols_img_path, cv2.cvtColor(same_cols_imgs, cv2.COLOR_RGB2BGR))

            # Google APIでOCR実行
            google_drive_ocr = google_api.ManipulateGoogleDriveAPI()
            output_same_cols_txt_path = f"media/txt/ocr_{col}.txt"
            same_cols_ocr_text = google_drive_ocr.drive_ocr(
                input_file_path = input_same_cols_img_path , output_txt_path = output_same_cols_txt_path ,
            )
            same_cols_ocr_text = assist_ocr.remove_pipe_from_string(same_cols_ocr_text)
            # OCR結果のテキストをセルごとに分解してリストに格納
            same_cols_ocr_text_list = re.split(r"\d{5,}", same_cols_ocr_text)
            same_cols_ocr_text_list = [text.strip() for text in same_cols_ocr_text_list if text.strip()]
            cells_ocr_text[ : , col ] = np.array(same_cols_ocr_text_list)
        
        df = pd.DataFrame(cells_ocr_text)
        csv_local_href = google_api.df_to_csv_local_url(df, output_csv_path)
        st.markdown(csv_local_href , unsafe_allow_html=True)
        st.write(cells_ocr_text)
        



if __name__ == '__main__':
    main()