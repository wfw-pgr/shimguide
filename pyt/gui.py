import tkinter as tk
from tkinter import filedialog

def execute1(file1, file2, file3):
    # ここに実行したい処理を書く
    print("実行1:", file1, file2, file3)

def choose_file(entry):
    file_path = filedialog.askopenfilename()
    entry.delete(0, tk.END)
    entry.insert(0, file_path)

def create_gui():
    root = tk.Tk()
    root.title("ファイル選択 GUI")

    # ファイル1
    label1 = tk.Label(root, text="ファイル1:")
    entry1 = tk.Entry(root, width=40)
    button1 = tk.Button(root, text="参照", command=lambda: choose_file(entry1))

    # ファイル2
    label2 = tk.Label(root, text="ファイル2:")
    entry2 = tk.Entry(root, width=40)
    button2 = tk.Button(root, text="参照", command=lambda: choose_file(entry2))

    # ファイル3
    label3 = tk.Label(root, text="ファイル3:")
    entry3 = tk.Entry(root, width=40)
    button3 = tk.Button(root, text="参照", command=lambda: choose_file(entry3))

    # 実行ボタン
    execute_button = tk.Button(root, text="実行", command=lambda: execute1(entry1.get(), entry2.get(), entry3.get()))

    # レイアウト
    label1.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
    entry1.grid(row=0, column=1, padx=5, pady=5)
    button1.grid(row=0, column=2, padx=5, pady=5)

    label2.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
    entry2.grid(row=1, column=1, padx=5, pady=5)
    button2.grid(row=1, column=2, padx=5, pady=5)

    label3.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
    entry3.grid(row=2, column=1, padx=5, pady=5)
    button3.grid(row=2, column=2, padx=5, pady=5)

    execute_button.grid(row=3, column=0, columnspan=3, pady=10)

    root.mainloop()

# GUIの作成
create_gui()
