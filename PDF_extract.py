import streamlit as st
import fitz  # PyMuPDF
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import io

# Function to extract 12px text from a PDF
def extract_12px_text_from_pdf(uploaded_pdf):
    doc = fitz.open(stream=uploaded_pdf.read(), filetype="pdf")  # Open PDF from BytesIO stream
    text_blocks = []

    for page in doc:
        # Extract text along with its font size and position
        for text_instance in page.get_text("dict")["blocks"]:
            if text_instance['type'] == 0:  # Only deal with text blocks
                for line in text_instance["lines"]:
                    for span in line["spans"]:
                        font_size = span['size']
                        if font_size == 12:  # Filter for 12px text
                            text_blocks.append(span['text'])
    return "\n".join(text_blocks)

# Function to create a PDF with text placed in a specific block (2x4 grid)
def create_pdf_with_12px_text_in_block(text, block_position):
    # Create an in-memory file
    pdf_buffer = io.BytesIO()

    # Create PDF canvas
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4  # Get standard A4 dimensions

    # Define block dimensions (2 columns x 4 rows)
    block_width = width / 2  # Dividing the width into 2 blocks
    block_height = height / 4  # Dividing the height into 4 blocks

    # Set the font size to 12px
    c.setFont("Helvetica", 12)

    # Split the text into lines (wrap text if necessary)
    lines = text.split("\n")

    # Get the chosen block position (block_position is a tuple like (row, column))
    row, col = block_position

    # Calculate the (x, y) position of the block based on row and column
    x = col * block_width  # No margin, start at the left edge of the block
    y = height - (row + 1) * block_height  # No margin, start at the top edge of the block

    # Calculate the width of each line of text (for centering)
    line_widths = [c.stringWidth(line, "Helvetica", 12) for line in lines]
    max_line_width = max(line_widths)  # Find the longest line to determine the center
    offset_x = (block_width - max_line_width) / 2  # Horizontal offset to center the text

    # Adjust vertical position to start in the middle of the block
    total_text_height = len(lines) * 14  # Approximate total height of the text block
    offset_y = (block_height - total_text_height) / 2  # Vertical offset to center the text

    # Make the vertical position slightly higher
    y += offset_y - 10  # Adjust by 10 units to move the text up

    # Start placing the text at the calculated (x, y) position
    for line in lines:
        c.drawString(x + offset_x, y, line)  # Place text horizontally centered
        y -= 14  # Move to the next line (14px line spacing, adjust as needed)

    # Save the PDF to the in-memory file
    c.save()

    # Return the in-memory file buffer
    pdf_buffer.seek(0)
    return pdf_buffer

# Streamlit App UI
st.title('PDF Text Extractor and Generator')

st.write("Upload a PDF file, and the app will extract 12px text, then create a new PDF with the extracted text placed in a 2x4 grid.")

# Upload PDF file
uploaded_pdf = st.file_uploader("Upload a PDF", type="pdf")

# Choose block position (row, column)
block_row = st.selectbox("Select block row (0-3)", range(4), index=0)
block_col = st.selectbox("Select block column (0-1)", range(2), index=0)
block_position = (block_row, block_col)

if uploaded_pdf:
    # Extract 12px text from the uploaded PDF
    text_12px = extract_12px_text_from_pdf(uploaded_pdf)

    # Generate the new PDF with the extracted text
    generated_pdf = create_pdf_with_12px_text_in_block(text_12px, block_position)

    # Provide a download button for the generated PDF
    st.download_button(
        label="Download Generated PDF",
        data=generated_pdf,
        file_name="generated_pdf_with_12px_text.pdf",
        mime="application/pdf"
    )
