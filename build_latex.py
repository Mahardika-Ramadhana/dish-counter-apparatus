import os
import glob
import re
import subprocess
import mistletoe
from mistletoe.latex_renderer import LaTeXRenderer

def remove_emojis(text):
    # Hapus karakter non-ascii / emoji yang mengganggu pdflatex
    return text.encode('ascii', 'ignore').decode('ascii')

def main():
    base_dir = "learning"
    files = [
        "README.md",
        "BIG_PICTURE.md",
        "ARCHITECTURE.md",
        "EXECUTION_FLOW.md",
        "GLOSSARY.md"
    ]
    masterclass_files = glob.glob(os.path.join(base_dir, "files", "*.md"))
    masterclass_files.sort()
    all_files = [os.path.join(base_dir, f) for f in files] + masterclass_files
    
    big_md = "# DICA Masterclass - Buku Panduan Lengkap\n\n"
    for fpath in all_files:
        if not os.path.exists(fpath):
            continue
        with open(fpath, "r", encoding="utf-8") as f:
            big_md += f"\\clearpage\n\n"
            big_md += f.read() + "\n\n"
            
    # Hapus emoji
    big_md = remove_emojis(big_md)
    
    with LaTeXRenderer() as renderer:
        rendered = renderer.render(mistletoe.Document(big_md))
        
    out_path = os.path.join(base_dir, "masterclass.tex")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(rendered)
        
    print(f"Successfully wrote {out_path}")
    
    # Compile
    print("Compiling PDF...")
    subprocess.run(["pdflatex", "-shell-escape", "-interaction=nonstopmode", "masterclass.tex"], cwd=base_dir)
    subprocess.run(["pdflatex", "-shell-escape", "-interaction=nonstopmode", "masterclass.tex"], cwd=base_dir)
    
if __name__ == "__main__":
    main()
