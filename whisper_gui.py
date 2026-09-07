import tkinter as tk
from tkinter import filedialog, messagebox
import whisper
import os
import threading
import json
import re
from pathlib import Path

# 強制指向 Homebrew
os.environ["PATH"] += os.pathsep + "/opt/homebrew/bin"

def format_time(seconds):
    hours, minutes = divmod(int(seconds), 3600)
    minutes, secs = divmod(minutes, 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

class WhisperAppModern:
    def __init__(self, root):
        self.root = root
        self.root.title("多語言語音判讀器")
        self.root.geometry("650x700") # 稍微拉長高度以容納按鈕區
        self.root.configure(bg="#f4f4f9")
        self.raw_text = ""
        self.is_processing = False

        # 標題
        tk.Label(root, text="多語言語音判讀器", font=("Helvetica", 18, "bold"), bg="#f4f4f9", fg="#333").pack(pady=15)

        # 說明區
        frame_help = tk.LabelFrame(root, text=" 支援語系說明 ", bg="#ffffff", padx=10, pady=10)
        frame_help.pack(fill="x", padx=20, pady=5)
        help_text = (
            "可自動偵測 99 種語言：包含 中文(繁/簡)、英文、日文、韓文、\n"
            "越南語、泰語、馬來語、印尼語、西班牙語等世界主要語種。"
        )
        tk.Label(frame_help, text=help_text, justify="left", bg="#ffffff").pack(anchor="w")

        # 開始辨識按鈕
        self.btn_select = tk.Label(root, text="📂 選擇影片並開始辨識", bg="#333333", fg="white", 
                                    font=("Arial", 12, "bold"), padx=15, pady=8, cursor="hand2")
        self.btn_select.pack(pady=15)
        self.btn_select.bind("<Button-1>", lambda e: self.process_video())

        self.status_label = tk.Label(root, text="待機中...", bg="#f4f4f9", fg="#666")
        self.status_label.pack()

        # 結果顯示區
        self.text_area = tk.Text(root, height=12, width=75, font=("Consolas", 10), bg="#ffffff")
        self.text_area.pack(pady=10, padx=20)

        # 下載按鈕容器
        self.frame_buttons = tk.Frame(root, bg="#f4f4f9")
        self.frame_buttons.pack(pady=10)

        # 下載 SRT 按鈕
        self.btn_save_srt = tk.Label(self.frame_buttons, text="💾 下載保存 SRT", bg="#555555", fg="#aaaaaa", 
                                      font=("Arial", 12, "bold"), padx=15, pady=8)
        self.btn_save_srt.pack(side=tk.LEFT, padx=10)

        # 下載 JSON 按鈕
        self.btn_save_json = tk.Label(self.frame_buttons, text="💾 下載保存 JSON", bg="#555555", fg="#aaaaaa", 
                                       font=("Arial", 12, "bold"), padx=15, pady=8)
        self.btn_save_json.pack(side=tk.LEFT, padx=10)

    def process_video(self):
        if self.is_processing: return
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.mov *.avi *.mkv")])
        if not file_path: return
        
        self.is_processing = True
        self.status_label.config(text="正在分析語音，這可能需要幾分鐘...", fg="#d9534f")
        threading.Thread(target=self.run_whisper, args=(file_path,), daemon=True).start()

    def run_whisper(self, file_path):
        try:
            model = whisper.load_model("small") #
            res = model.transcribe(file_path, verbose=False)
            
            self.raw_text = ""
            for i, s in enumerate(res['segments']):
                self.raw_text += f"{i+1}\n{format_time(s['start'])} --> {format_time(s['end'])}\n{s['text'].strip()}\n\n"
            
            self.root.after(0, self.update_ui)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("錯誤", f"詳細錯誤訊息: {str(e)}"))

    def update_ui(self):
        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, self.raw_text)
        self.status_label.config(text="辨識完成！請檢查文字並下載。", fg="#28a745")
        self.is_processing = False
        
        # 啟用並美化 SRT 下載按鈕
        self.btn_save_srt.config(bg="#333333", fg="white", cursor="hand2")
        self.btn_save_srt.bind("<Button-1>", lambda e: self.save_file("srt"))
        
        # 啟用並美化 JSON 下載按鈕
        self.btn_save_json.config(bg="#333333", fg="white", cursor="hand2")
        self.btn_save_json.bind("<Button-1>", lambda e: self.save_file("json"))

    def save_file(self, mode):
        if mode == "srt":
            file_path = filedialog.asksaveasfilename(defaultextension=".srt", filetypes=[("SRT files", "*.srt")])
            if file_path:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(self.raw_text)
                messagebox.showinfo("成功", "SRT 檔案已保存！")
        
        elif mode == "json":
            file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
            if file_path:
                # 解析 SRT 格式為 JSON
                data = []
                blocks = re.split(r'\n\n+', self.raw_text.strip())
                for block in blocks:
                    lines = block.split('\n')
                    if len(lines) >= 3:
                        data.append({"index": lines[0], "time": lines[1], "text": " ".join(lines[2:])})
                
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                messagebox.showinfo("成功", "JSON 檔案已保存！")

if __name__ == "__main__":
    root = tk.Tk()
    app = WhisperAppModern(root)
    root.mainloop()
