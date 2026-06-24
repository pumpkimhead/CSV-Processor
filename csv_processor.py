import pandas as pd
import re
import tkinter as tk
from tkinter import filedialog
import webbrowser
import sys
import os

def get_resource_path(relative_path):    
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, relative_path)


def center_window(window, width, height):
    screen_width  = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    x = (screen_width  - width)  // 2
    y = (screen_height - height) // 2

    window.geometry(f"{width}x{height}+{x}+{y}")


def safe_to_float(value):   
    try:
        return float(str(value).strip())
    except (ValueError, TypeError):
        return 0.0

def show_splash():
    splash = tk.Tk()
    splash.title("CSV Processor")
    splash.resizable(False, False)   
    splash.configure(bg="white")
    splash.overrideredirect(True)    
    center_window(splash, 500, 300)

    try:
        logo_image = tk.PhotoImage(file=get_resource_path("logo.png"))
        tk.Label(splash, image=logo_image, bg="white").pack(pady=(25, 10))
        splash.image = logo_image  
    except Exception:
        pass  

    tk.Label(splash, text="CSV Processor",            font=("Segoe UI", 20, "bold"), bg="white").pack()
    tk.Label(splash, text="Version 1.0",               font=("Segoe UI", 10),         bg="white").pack()
    tk.Label(splash, text="Created by Erick Lucas Martins", font=("Segoe UI", 10),   bg="white").pack(pady=(5, 0))
    tk.Label(splash, text="Loading…",                  font=("Segoe UI", 11),         bg="white").pack(pady=(25, 0))

    splash.after(3500, splash.destroy)
    splash.mainloop()

def show_complete(output_path):
    complete = tk.Tk()
    complete.title("CSV Processing Complete")
    complete.resizable(False, False)
    center_window(complete, 600, 320)

    complete.lift()
    complete.attributes("-topmost", True)
    complete.focus_force()

    frame = tk.Frame(complete, padx=20, pady=20)
    frame.pack(fill="both", expand=True)

    tk.Label(
        frame,
        text="✓ Processing Completed Successfully",
        font=("Segoe UI", 14, "bold")
    ).pack(pady=(0, 15))

    file_name = os.path.basename(output_path)
    tk.Label(frame, text=f"Output File:\n{file_name}", justify="center").pack()

    tk.Label(frame, text=f"\nLocation:\n{output_path}", justify="center", wraplength=540).pack()

    tk.Label(frame, text="\nThank you for using CSV Processor.", font=("Segoe UI", 10)).pack()
    tk.Label(frame, text="Created by Erick Lucas Martins",       font=("Segoe UI", 10, "bold")).pack(pady=(5, 0))

    tk.Button(
        frame,
        text="Visit GitHub",
        command=lambda: webbrowser.open("https://github.com/pumpkimhead"),
        width=20
    ).pack(pady=15)

    tk.Button(frame, text="Close", command=complete.destroy, width=20).pack()

    complete.mainloop()

# Tried to fix special cases in FEATURE before processing, my company cases.

def normalise_feature(row):
    feature = row["FEATURE"].strip()  
    note    = row["NOTE"].strip()

    if not feature:
        return row

    tokens = feature.split()

    first_word_is_feature = re.match(r"^feature$", tokens[0], re.IGNORECASE)
    last_word_is_4_digits = len(tokens) >= 2 and re.match(r"^\d{4}$", tokens[-1])

    if first_word_is_feature and last_word_is_4_digits:
        row["FEATURE"] = "UN"
        return row  

    tokens_upper = [token.upper() for token in tokens]

    if "B3" in tokens_upper:
        extra_words = [token for token in tokens if token.upper() != "B3"]
        note_parts = ["B3"] + extra_words
        
        row["FEATURE"] = "UN"
        row["NOTE"]    = " ".join(part for part in [note] + note_parts if part).strip()
        return row

    return row

def process_csv(input_path):    
    base, ext    = os.path.splitext(input_path)
    output_path  = base + "_output" + ext

    df = pd.read_csv(
        input_path,
        header=None,
        sep=",",
        engine="python",
        names=range(23),    
        usecols=range(23), 
    ).fillna("")            

    columns_to_remove = [1, *range(3, 13), *range(17, 23)]
    df = df.drop(columns=df.columns.intersection(columns_to_remove))

    df = df.iloc[2:].reset_index(drop=True)  
    df = df.fillna("").astype(str)            

    depth_part_a = df.iloc[:, 4].apply(safe_to_float)
    depth_part_b = df.iloc[:, 5].apply(safe_to_float)
    df.iloc[:, 5] = (depth_part_a + depth_part_b).astype(str)

    df = df.iloc[:, [0, 2, 3, 5, 1, 4]]

    number_of_rows = len(df)
    df.iloc[:, 0] = [str(n) for n in range(100, 100 + number_of_rows)]

    while df.shape[1] < 8:
        df[df.shape[1]] = ""

    df.columns = [
        "POINTS",
        "COORDINATE_1",
        "COORDINATE_2",
        "ELEVATION",
        "FEATURE",
        "DEPTH",
        "NOTE",
        "EXTRA FINAL NOTE",
    ]
    df = df.fillna("").astype(str)

    df = df.apply(normalise_feature, axis=1)

    row_index = 0  

    while row_index < len(df):
        feature = df.loc[row_index, "FEATURE"].strip()
        
        if not feature:
            row_index += 1
            continue
  
        next_index = row_index + 1
        while next_index < len(df) and df.loc[next_index, "FEATURE"].strip() == "":
            next_index += 1

        group_last_row = next_index - 1 

        has_b3_flag = "B3" in feature.upper()

        clean_feature = re.sub(r"\s*\bB3\b\s*", "", feature, flags=re.IGNORECASE).strip()
        df.loc[row_index, "FEATURE"] = clean_feature

        if has_b3_flag:
            for k in range(row_index, group_last_row + 1):
                current_note = df.loc[k, "NOTE"].strip()
                if "B3" not in current_note.upper():
                    df.loc[k, "NOTE"] = (current_note + " B3").strip()

        df.loc[group_last_row, "FEATURE"] = clean_feature + " EL"

        for target_row in (row_index, group_last_row):
            current_extra = df.loc[target_row, "EXTRA FINAL NOTE"].strip()
            if "UTT" not in current_extra.upper():
                df.loc[target_row, "EXTRA FINAL NOTE"] = (current_extra + " UTT").strip()

        row_index = group_last_row + 1

    df["FEATURE"] = df["FEATURE"].replace("", pd.NA).ffill()

    def merge_into_feature(row):        
        parts = [
            row["FEATURE"],
            row["DEPTH"],
            row["NOTE"],
            row["EXTRA FINAL NOTE"],
        ]
        non_empty_parts = [part.strip() for part in parts if part.strip()]
        return " ".join(non_empty_parts)

    df["FEATURE"] = df.apply(merge_into_feature, axis=1)
    df["DEPTH"]            = ""
    df["NOTE"]             = ""
    df["EXTRA FINAL NOTE"] = ""

    df.to_csv(output_path, index=False, header=False)

    return output_path

# Splash

def main():
    show_splash()
    root = tk.Tk()
    root.withdraw()  

    input_path = filedialog.askopenfilename(
        title="Select CSV File",
        filetypes=[("CSV Files", "*.csv")],
    )
    root.destroy()

    if not input_path:
        sys.exit()

    output_path = process_csv(input_path)

    show_complete(output_path)

if __name__ == "__main__":
    main()


# Created by Erick Lucas Martins