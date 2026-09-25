import io
import qrcode
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="QR Code Generator", page_icon="📱")

st.title("QR Code Generator")
st.caption("Generate a plain text QR code with top and bottom labels")

# Sidebar / Main Inputs
with st.form("qr_form"):
    top_text = st.text_input("Top Text (Header)", value="SCAN ME")
    qr_data = st.text_area(
        "QR Code Text (Raw Text Content)",
        value="Type your plain text content here...",
    )
    bottom_text = st.text_input("Bottom Text (Footer)", value="ToolSphere")

    col1, col2 = st.columns(2)
    with col1:
        box_size = st.slider("QR Box Size", 5, 20, 10)
    with col2:
        font_size = st.slider("Text Font Size", 12, 36, 20)

    submit_button = st.form_submit_button("Generate QR Code")

if submit_button or qr_data:
    # 1. Generate QR Code Image
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    qr_img = qr.make_image(
        fill_color="black", back_color="white"
    ).convert("RGB")
    qr_width, qr_height = qr_img.size

    # 2. Setup Canvas Margins for Top & Bottom Text
    top_padding = font_size + 10 if top_text else 5
    bottom_padding = font_size + 10 if bottom_text else 5

    total_width = qr_width
    total_height = qr_height + top_padding + bottom_padding

    # Create white canvas
    canvas = Image.new("RGB", (total_width, total_height), "white")
    canvas.paste(qr_img, (0, top_padding))

    draw = ImageDraw.Draw(canvas)

    # Try loading default font
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    # 3. Render Top Text
    if top_text:
        bbox = draw.textbbox((0, 0), top_text, font=font)
        text_w = bbox[2] - bbox[0]
        x = (total_width - text_w) // 2
        y = (top_padding - (bbox[3] - bbox[1])) // 2
        draw.text((x, y), top_text, fill="black", font=font)

    # 4. Render Bottom Text
    if bottom_text:
        bbox = draw.textbbox((0, 0), bottom_text, font=font)
        text_w = bbox[2] - bbox[0]
        x = (total_width - text_w) // 2
        y = qr_height + top_padding + 5
        draw.text((x, y), bottom_text, fill="black", font=font)

    # 5. Display Image & Download Button in Streamlit
    st.image(canvas, caption="Generated QR Code", use_container_width=False)

    buf = io.BytesIO()
    canvas.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.download_button(
        label="Download QR Code PNG",
        data=byte_im,
        file_name="qr_code_with_text.png",
        mime="image/png",
    )