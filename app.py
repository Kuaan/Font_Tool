import streamlit as st
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="Waveshare Font Tool", layout="wide")

st.title("🖨️ ePaper 取模工具")
st.caption("專為 Waveshare 1bit 顯示驅動設計，輸出 42 Bytes C 語言數組")

# 側邊欄設定
with st.sidebar:
    st.header("⚙️ 字體設定")
    uploaded_ttf = st.file_uploader("1. 上傳字體 (.ttf)", type="ttf")
    font_size = st.number_input("2. 字體大小 (Font Size)", value=18, min_value=10, max_value=21)
    y_offset = st.slider("3. 垂直微調 (Y Offset)", -5, 5, 0)
    x_offset_manual = st.slider("4. 水平微調 (X Offset)", -5, 5, 0)

# 主要輸入區
input_text = st.text_input("輸入要轉換的文字 (例如：設定溫度)", "設定")

if uploaded_ttf and input_text:
    # 暫存字體檔
    with open("temp_font.ttf", "wb") as f:
        f.write(uploaded_ttf.getbuffer())
    
    try:
        font = ImageFont.truetype("temp_font.ttf", font_size)
        results = []
        preview_imgs = []

        for char in input_text:
            # 建立 16x21 畫布 (1 為白色背景)
            img = Image.new('1', (16, 21), color=1)
            draw = ImageDraw.Draw(img)
            
            # 計算置中
            bbox = draw.textbbox((0, 0), char, font=font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            x = (16 - w) // 2 - bbox[0] + x_offset_manual
            y = (21 - h) // 2 - bbox[1] + y_offset
            
            # 繪製文字 (0 為黑色)
            draw.text((x, y), char, font=font, fill=0)
            preview_imgs.append(img.resize((80, 105), resample=Image.NEAREST)) # 放大預覽

            # 轉換為 42 Bytes 代碼
            data = []
            for row in range(21):
                byte1, byte2 = 0, 0
                for col in range(8):
                    if img.getpixel((col, row)) == 0: byte1 |= (1 << (7 - col))
                    if img.getpixel((col + 8, row)) == 0: byte2 |= (1 << (7 - col))
                data.append(f"0x{byte1:02X}")
                data.append(f"0x{byte2:02X}")
            
            hex_str = ", ".join(data)
            results.append(f'/*-- 文字: {char} --*/\n{{"{char}",\n{hex_str}}},')

        # 顯示預覽與代碼
        cols = st.columns(len(input_text))
        for i, col in enumerate(cols):
            col.image(preview_imgs[i], caption=input_text[i])

        st.subheader("📋 C 語言代碼 (貼進 Font12CN_Table)")
        st.code("\n\n".join(results), language="c")

    except Exception as e:
        st.error(f"發生錯誤: {e}")
else:
    st.info("💡 請在左側上傳 .ttf 字體檔開始轉換。")
