import os
from tkinter import Tk, filedialog
from PyPDF2 import PdfReader, PdfWriter

# === CONFIGURATION ===
x = 221 # First page to keep (1-based index)
y = 228# Last page to keep (inclusive)

# === FILE SELECTION ===
Tk().withdraw()  # Hide the root Tk window
input_pdf_path = filedialog.askopenfilename(title="Select PDF file", filetypes=[("PDF files", "*.pdf")])

if not input_pdf_path:
    print("No file selected. Exiting.")
    exit()

# === PROCESSING ===
reader = PdfReader(input_pdf_path)
writer = PdfWriter()

# Convert to 0-based indices
x_idx = x - 1
y_idx = y

# Extract only the required pages
for i in range(x_idx, min(y_idx, len(reader.pages))):
    writer.add_page(reader.pages[i])

# Create new filename
base, ext = os.path.splitext(input_pdf_path)
output_pdf_path = f"{base} pg {x}-{y}{ext}"

# Save the new PDF
with open(output_pdf_path, "wb") as f:
    writer.write(f)

print(f"Trimmed PDF saved as '{output_pdf_path}' with pages {x} to {y}.")
