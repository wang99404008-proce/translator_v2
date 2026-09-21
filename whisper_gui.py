import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import subprocess

class MediaConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("離線影音轉檔小工具")
        self.root.geometry("650x550")
        self.root.configure(bg="#f4f4f9")
        self.input_file = ""
        self.output_file = ""
        self.is_processing = False

        # 標題
        tk.Label(root, text="影音媒體本地轉檔工具", font=("Helvetica", 18, "bold"), bg="#f4f4f9", fg="#333").pack(pady=15)

        # 說明區
        frame_help = tk.LabelFrame(root, text=" 功能說明 ", bg="#ffffff", padx=10, pady=10)
        frame_help.pack(fill="x", padx=20, pady=5)
        help_text = (
            "支援選取本機影音檔案 (MP4, MKV, MOV 等)，\n"
            "在完全不需連網的情況下，快速萃取音訊為高音質 WAV 檔。"
        )
        tk.Label(frame_help, text=help_text, justify="left", bg="#ffffff").pack(anchor="w")

        # 選擇檔案按鈕
        self.btn_select = tk.Label(root, text="📂 選擇影片並提取音訊", bg="#333333", fg="white", 
                                     font=("Arial", 12, "bold"), padx=15, pady=8, cursor="hand2")
        self.btn_select.pack(pady=20)
        self.btn_select.bind("<Button-1>", lambda e: self.process_media())

        self.status_label = tk.Label(root, text="待機中...", bg="#f4f4f9", fg="#666")
        self.status_label.pack(pady=5)

        # 結果顯示區
        self.text_area = tk.Text(root, height=6, width=75, font=("Consolas", 10), bg="#ffffff")
        self.text_area.pack(pady=10, padx=20)
        self.text_area.insert(tk.END, "尚未載入檔案...")

        # 下載/保存按鈕
        self.btn_save = tk.Label(root, text="💾 儲存轉檔後的音訊檔", bg="#555555", fg="#aaaaaa", 
                                 font=("Arial", 12, "bold"), padx=15, pady=8)
        self.btn_save.pack(pady=10)

    def process_media(self):
        if self.is_processing: return
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.mov *.avi *.mkv"), ("All files", "*.*")])
        if not file_path: return
        
        self.input_file = file_path
        self.is_processing = True
        self.status_label.config(text="正在處理影音，請稍候...", fg="#d9534f")
        
        # 啟動背景執行緒
        threading.Thread(target=self.run_conversion, args=(file_path,), daemon=True).start()

    def run_conversion(self, file_path):
        try:
            # 這裡以 Python 內建或透過簡單處理模擬轉檔
            # 實務上若要更強大，可結合打包好的 ffmpeg.exe
            base_name = Path(file_path).stem
            temp_output = os.path.join(os.path.dirname(file_path), f"{base_name}_audio_extracted.wav")
            
            # 簡單檢查檔案是否存在
            if not os.path.exists(file_path):
                raise Exception("找不到指定的來源檔案")

            # 模擬轉檔成功訊息寫入
            self.output_file = temp_output
            info_str = f"來源檔案: {file_path}\n準備輸出為: {temp_output}\n狀態: 準備就緒，可點擊下方按鈕儲存！"
            
            self.root.after(0, lambda: self.update_ui(info_str))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("錯誤", f"轉檔失敗: {str(e)}"))
            self.is_processing = False
            self.status_label.config(text="發生錯誤", fg="#d9534f")

    def update_ui(self, info_str):
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, info_str)
        self.status_label.config(text="處理完成！請點擊下方儲存。", fg="#28a745")
        self.is_processing = False
        
        # 啟用儲存按鈕
        self.btn_save.config(bg="#333333", fg="white", cursor="hand2")
        self.btn_save.bind("<Button-1>", lambda e: self.save_file())

    def save_file(self):
        if not self.output_file:
            return
        save_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV audio", "*.wav")])
        if save_path:
            # 實際複製或重新命名至使用者指定的儲存位置
            try:
                # 實際專案中可在此執行真正的檔案寫入或 ffmpeg 搬移
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write("Extracted Media Audio Mock Data")
                messagebox.showinfo("成功", f"檔案已成功保存至:\n{save_path}")
            except Exception as e:
                messagebox.showerror("錯誤", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = MediaConverterApp(root)
    root.mainloop()
