import streamlit as st
import numpy as np
import cv2
import base64
import pandas as pd


def st_upload_img_to_path(input_file_path: str = "input_img.jpg"):
    """
    streamlitで画像の入力フォーム設置とnp画像を取得する関数
    使い方 : 
        input_rgb_img: np.ndarray = st_upload_img_to_path(input_file_path)
        if isinstance(input_rgb_img,  np.ndarray): 
    """ 
    uploaded_file = st.file_uploader("画像またはPDFをアップロードしてください", type=["jpg", "jpeg", "png"])
    st.markdown(f"<p><br></p>", unsafe_allow_html=True)
    if uploaded_file:
        # アップロードされたファイルをディレクトリに保存
        with open(input_file_path, "wb") as file:
            file.write(uploaded_file.getbuffer())
        input_rgb_img: np.ndarray = cv2.cvtColor(cv2.imread(input_file_path) , cv2.COLOR_BGR2RGB)
    else:
        input_rgb_img = None
    return input_rgb_img

def display_free_size_img(img_np):
    with st.expander("表示画像のサイズを調整"):
       img_size = st.slider("", min_value=10, max_value=600, value=300, step=30)
    st.image(img_np, width=img_size)
    st.write("<p><br></p>", unsafe_allow_html=True)


def df_to_csv_local_url(df: pd.DataFrame , output_csv_path: str = "output.csv"):
    """ データフレーム型の表をcsv形式でダウンロードできるURLを生成する関数 """
    # csvの生成＆ローカルディレクトリ上に保存（「path_or_buf」を指定したら、戻り値は「None」）
    df.to_csv(path_or_buf=output_csv_path, index=False, header=False, encoding='utf-8-sig')
    # ダウロードできるaタグを生成
    csv = df.to_csv(index=False, header=False, encoding='utf-8-sig')
    b64 = base64.b64encode(csv.encode('utf-8-sig')).decode()  # some strings <-> bytes conversions necessary here
    csv_local_href = f'<a href="data:file/csv;base64,{b64}" download={output_csv_path}>CSVでダウンロード</a>'
    return csv_local_href


def main():
    """ streamlitアプリで利用できる便利なクラス・関数を含むモジュール """

if __name__ == "__main__":
    main()