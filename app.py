import io
import qrcode
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="QR Code Generator", page_icon="📱")

st.title("QR Code Generator")
st.caption("Generate a plain text QR code with header and footer labels")

with st.form("qr_form"):
    top_text = st.text_input("Top Text (Header)", value="SCAN ME")
    qr_data = st.text_area(
        "QR Code Text (Raw Text Content)",
        value="Type your plain text content here...",
    )
    bottom_text = st.text_input("Bottom Text (Footer)", value="ToolSphere")

    st.subheader("Layout & Sizing")
    col1, col2 = st.columns(2)
    with col1:
        box_size = st.slider("QR Code Size", 5, 25, 10)
        top_gap = st.slider("Top Text Gap", 0, 30, 5)
    with col2:
        font_size = st.slider("Text Font Size", 12, 72, 32)  # Increased font limit
        bottom_gap = st.slider("Bottom Text Gap", 0, 30, 5)

    submit_button = st.form_submit_button("Generate QR Code")

if submit_button or qr_data:
    # 1. Generate QR Code Matrix
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=2,  # Compact QR border
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    qr_img = qr.make_image(
        fill_color="black", back_color="white"
    ).convert("RGB")
    qr_width, qr_height = qr_img.size

    # Load Font
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    # Calculate Text Bounding Boxes for Exact Height Calculations
    dummy_img = Image.new("RGB", (1, 1))
    dummy_draw = ImageDraw.Draw(dummy_img)

    top_text_h = (
        dummy_draw.textbbox((0, 0), top_text, font=font)[3] if top_text else 0
    )
    bottom_text_h = (
        dummy_draw.textbbox((0, 0), bottom_text, font=font)[3]
        if bottom_text
        else 0
    )

    # Calculate Compact Canvas Dimensions
    top_padding = (top_text_h + top_gap) if top_text else 10
    bottom_padding = (bottom_text_h + bottom_gap) if bottom_text else 10

    total_width = qr_width
    total_height = qr_height + top_padding + bottom_padding

    # Create Canvas & Paste QR Code
    canvas = Image.new("RGB", (total_width, total_height), "white")
    canvas.paste(qr_img, (0, top_padding))

    draw = ImageDraw.Draw(canvas)

    # 2. Render Top Text (Positioned close above QR)
    if top_text:
        bbox = draw.textbbox((0, 0), top_text, font=font)
        text_w = bbox[2] - bbox[0]
        x = (total_width - text_w) // 2
        y = top_padding - bbox[3] - top_gap
        draw.text((x, max(0, y)), top_text, fill="black", font=font)

    # 3. Render Bottom Text (Positioned close below QR)
    if bottom_text:
        bbox = draw.textbbox((0, 0), bottom_text, font=font)
        text_w = bbox[2] - bbox[0]
        x = (total_width - text_w) // 2
        y = top_padding + qr_height + bottom_gap
        draw.text((x, y), bottom_text, fill="black", font=font)

    # 4. Display Result
    st.image(canvas, caption="Generated QR Code", use_container_width=False)

    buf = io.BytesIO()
    canvas.save(buf, format="PNG")
    byte_im = buf.getvalue()

    st.download_button(
        label="Download PNG",
        data=byte_im,
        file_name="qr_code.png",
        mime="image/png",
    )