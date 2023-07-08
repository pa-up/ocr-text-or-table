from ocr.asprise_ocr import *
import pandas as pd
import base64
import io
import xml.etree.ElementTree as ET
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload
# Googleドライブ APIの認識
from google.oauth2 import service_account


def df_to_csv_local_url(df: pd.DataFrame , output_csv_path: str = "output.csv"):
    """ データフレーム型の表をcsv形式でダウンロードできるURLを生成する関数 """
    # csvの生成＆ローカルディレクトリ上に保存（「path_or_buf」を指定したら、戻り値は「None」）
    df.to_csv(path_or_buf=output_csv_path, index=False, header=False, encoding='utf-8-sig')
    # ダウロードできるaタグを生成
    csv = df.to_csv(index=False, header=False, encoding='utf-8-sig')
    b64 = base64.b64encode(csv.encode('utf-8-sig')).decode()  # some strings <-> bytes conversions necessary here
    csv_local_href = f'<a href="data:file/csv;base64,{b64}" download={output_csv_path}>CSVでダウンロード</a>'
    return csv_local_href



class ManipulateGoogleDriveAPI:
    """ GoogleDriveのAPIを用いて操作するクラス """
    def __init__(self , json_file_path: str = 'static/json/google_drive_api.json') -> None:
        self.json_file_path = json_file_path
        # jsonファイルの定義
        self.credentials = service_account.Credentials.from_service_account_file(
            self.json_file_path, scopes=['https://www.googleapis.com/auth/drive']
        )
        # Googleドライブ APIのビルド
        self.service = build('drive', 'v3', credentials=self.credentials)

    def download_drive_file(self, file_id: str, output_file_path: str):
        """
        Googleドライブ上のファイルを取得する関数
        parameters:
            file_id : 「リンクを共有」で取得したURL「https://drive.google.com/file/d/{file_id}/view」から取得可能
            output_file_path : ダウンロードしたファイルの保存先のパス
            json_file_path : GCPのAPIを利用可能にするjsonファイルのパス
        """
        # ファイルIDを指定してダウンロード
        request = self.service.files().get_media(fileId=file_id)
        fh = open(output_file_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        fh.close()

    def upload_drive_file(self, input_file_path: str, language_parameter = None):
        """
        Googleドライブ上にファイルをアップロードする関数
        parameters:
            file_id : 「リンクを共有」で取得したURL「https://drive.google.com/file/d/{file_id}/view」から取得可能
            destination : ダウンロードしたファイルの保存先のパス
            json_file_path : GCPのAPIを利用可能にするjsonファイルのパス
        """
        MIME_TYPE = 'application/vnd.google-apps.document'
        media_body = MediaFileUpload(input_file_path, mimetype=MIME_TYPE, resumable=True)
        body = {
            'name': "output.pdf",
            'mimeType': MIME_TYPE
        }
        # ファイルIDを指定してダウンロード
        if language_parameter == None:  # OCRしない場合
            output = self.service.files().create(body=body,media_body=media_body).execute()
        else:  # OCRする場合
            output = self.service.files().create(body=body,media_body=media_body,ocrLanguage=language_parameter,).execute()
        file_id = output.get('id')
        return file_id

    def drive_ocr(self, input_file_path: str, output_txt_path: str, output_pdf_path: str = "", language_parameter: str = "ja"):
        """ GoogleDriveのAPIでOCRするモジュール """
        # ファイルをOCRした状態でアップロード
        file_id = self.upload_drive_file(input_file_path, language_parameter)
        
        # ファイルをPDF形式でダウンロード
        if output_pdf_path != "":
            request = self.service.files().export_media(
                fileId=file_id,
                mimeType = "application/pdf"
            )
            fh = io.FileIO(output_pdf_path, "wb")
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            fh.close()

        # ファイルをテキスト形式でダウンロード
        request = self.service.files().export_media(
            fileId=file_id,
            mimeType = "text/plain"
        )
        fh = io.FileIO(output_txt_path, "wb")
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        fh.close()

        # Google Drive上のファイル削除
        self.service.files().delete(fileId=file_id).execute()
        
        # テキストの取得
        with open(output_txt_path) as f:
            ocr_text_list = f.read().splitlines()[1:]
            ocr_text = '\n'.join(ocr_text_list)
            return ocr_text
        

def main():
    """ 便利なクラス・関数を含むモジュール """

if __name__ == "__main__":
    main()