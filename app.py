import io
import urllib.request
import qrcode
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="QR Code Generator", page_icon="📱")

st.title("QR Code Generator")
st.caption("Generate a plain text QR code with header and footer labels")


# Helper function to get scalable TTF font on any platform (Windows, Linux, Streamlit Cloud)
@st.cache_resource
def load_scalable_font():
    font_url = "https://github.com/google/fonts/raw/main/ofl/opensans/OpenSans%5Bwdth%2Cwght%5D.ttf"
    try:
        # Try local fonts first
        return "arial.ttf"
    except Exception:
        pass

    # Download a standard TTF font if local font is missing
    font_bytes = urllib.request.urlopen(font_url).read()
    return io.BytesIO(font_bytes)


font_source = load_scalable_font()

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
        # Default font size set to 28
        font_size = st.slider("Text Font Size", 12, 72, 28)
        bottom_gap = st.slider("Bottom Text Gap", 0, 30, 5)

    submit_button = st.form_submit_button("Generate QR Code")

if submit_button or qr_data:
    # 1. Generate QR Code Matrix
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=box_size,
        border=2,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    qr_img = qr.make_image(
        fill_color="black", back_color="white"
    ).convert("RGB")
    qr_width, qr_height = qr_img.size

    # Load scalable font with the selected size
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except Exception:
        font = ImageFont.truetype(font_source, font_size)

    # Calculate Text Dimensions
    dummy_draw = ImageDraw.Draw(Image.new("RGB", (1, 1)))

    top_bbox = dummy_draw.textbbox((0, 0), top_text, font=font) if top_text else (0, 0, 0, 0)
    bottom_bbox = dummy_draw.textbbox((0, 0), bottom_text, font=font) if bottom_text else (0, 0, 0, 0)

    top_text_w = top_bbox[2] - top_bbox[0]
    top_text_h = top_bbox[3] - top_bbox[1]

    bottom_text_w = bottom_bbox[2] - bottom_bbox[0]
    bottom_text_h = bottom_bbox[3] - bottom_bbox[1]

    # Keep a clear border around the complete exported QR image.
    canvas_padding = 24
    text_width = max(top_text_w, bottom_text_w)
    total_width = max(qr_width, text_width) + (canvas_padding * 2)

    top_section = (top_text_h + top_gap) if top_text else 0
    bottom_section = (bottom_text_h + bottom_gap) if bottom_text else 0
    qr_y = canvas_padding + top_section
    total_height = (
        canvas_padding + top_section + qr_height + bottom_section + canvas_padding
    )

    # Create White Canvas
    canvas = Image.new("RGB", (total_width, total_height), "white")

    # Center QR Code Horizontally
    qr_x = (total_width - qr_width) // 2
    canvas.paste(qr_img, (qr_x, qr_y))

    draw = ImageDraw.Draw(canvas)

    # 2. Render Top Text
    if top_text:
        x = (total_width - top_text_w) // 2
        y = canvas_padding - top_bbox[1]
        draw.text((x - top_bbox[0], y), top_text, fill="black", font=font)

    # 3. Render Bottom Text
    if bottom_text:
        x = (total_width - bottom_text_w) // 2
        y = qr_y + qr_height + bottom_gap - bottom_bbox[1]
        draw.text((x - bottom_bbox[0], y), bottom_text, fill="black", font=font)

    # 4. Display & Download
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