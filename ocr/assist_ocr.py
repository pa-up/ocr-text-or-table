from ocr.asprise_ocr import *
import pandas as pd
import re
import requests
import json
import numpy as np
import xml.etree.ElementTree as ET


def xml_to_cells_image(input_rgb_img: np.ndarray , input_xml_path: str):
    """ OCRされたXMLファイルから表のセルの切り抜き画像を全て取得する関数 """
    # XMLファイルをパースしてElementTreeオブジェクトを取得
    tree = ET.parse(input_xml_path)
    root = tree.getroot()

    # 入力画像全体の大きさを取得
    page = root.find('.//page')
    input_img_width , input_img_height = int(page.get('width')) , int(page.get('height'))

    # 表の行数・列数を取得
    table = root.find('.//table')
    rows , cols = int(table.get('rows')) , int(table.get('cols'))
    table_x_min , table_y_min = int(table.get('x')) , int(table.get('y'))
    table_width , table_height = int(table.get('width')) , int(table.get('height'))

    # numpy[m行n列のセルの画像を格納]
    cells = root.findall(f'.//table/cell')
    cells_imgs = np.empty( (rows , cols) , dtype="object" )
    cell_count = 0
    for row in range(rows):
        for col in range(cols):
            cell_x_min , cell_y_min = int(cells[cell_count].get('x')) , int(cells[cell_count].get('y'))
            cell_width , cell_height = int(cells[cell_count].get('width')) , int(cells[cell_count].get('height'))
            cells_imgs[row , col] = input_rgb_img[cell_y_min : cell_y_min + cell_height , cell_x_min : cell_x_min + cell_width]
            cell_count += 1
    return cells_imgs

    



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



def ocr_space_api(input_file_path: str, api_key: str, language_parameter: str='eng', overlay: bool=False):
    """ OCR.space API を用いてOCRする関数
    parameters : 
        input_file_path : 入力ファイルのパス
        overlay : OCR.space overlay の必要性有無
        api_key: OCR.space の API キー
        language_parameter : 言語パラメータ
            利用可能な言語一覧 : https://ocr.space/OCRAPI
    return : 
        output_ocr_text : OCRされたテキストデータ（改行含む）
    """
    payload = {'isOverlayRequired': overlay,
               'apikey': api_key,
               'language': language_parameter, }
    with open(input_file_path, 'rb') as f:
        r = requests.post(
            'https://api.ocr.space/parse/image',
            files={input_file_path: f}, data=payload, )
    output_json = r.content.decode()
    # JSON文字列を解析
    output_data = json.loads(output_json)
    # ParsedTextキーの値を取得
    output_ocr_text: str = output_data['ParsedResults'][0]['ParsedText']
    return output_ocr_text



def remove_pipe_from_string(input_string):
    """ 文字「|」を削除する関数 """
    if not isinstance(input_string, str):
        raise TypeError("Input must be a string.")
    return input_string.replace("|", "")




def main():
    """ OCRの前処理・後処理を行うクラス・関数を含むモジュール """

if __name__ == "__main__":
    main()