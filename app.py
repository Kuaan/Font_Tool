import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import math

st.set_page_config(page_title="Universal Font Tool", layout="wide")

st.title("🛠️ 通用嵌入式字體取模工具")
st.caption("支援自定義長寬、逐行掃描、MSB First 格式")

with st.sidebar:
    st.header("📐 尺寸與字體")
    uploaded_ttf = st.file_uploader("1. 上傳字體 (.ttf)", type="ttf")
    
    col1, col2 = st.columns(2)
    target_w = col1.number_input("畫布寬度 (px)", value=16, min_value=8, step=8)
    target_h = col2.number_input("畫布高度 (px)", value=21, min_value=8, step=1)
    
    font_size = st.slider("字體大小", 10, target_h + 5, target_h - 3)
    y_offset = st.slider("垂直微調", -10, 10, 0)
    x_offset = st.slider("水平微調", -10, 10, 0)

input_text = st.text_input("輸入文字", "設定")

if uploaded_ttf and input_text:
    with open("temp_font.ttf", "wb") as f:
        f.write(uploaded_ttf.getbuffer())
    
    try:
        font = ImageFont.truetype("temp_font.ttf", font_size)
        results = []
        
        # 每行需要的位元組數 (例如 16px 寬需 2 bytes, 24px 需 3 bytes)
        bytes_per_row = math.ceil(target_w / 8)
        
        st.write(f"當前設定：{target_w}x{target_h}，每個字佔用 {bytes_per_row * target_h} Bytes")
        
        preview_cols = st.columns(len(input_text))
        
        for i, char in enumerate(input_text):
            # 建立畫布
            img = Image.new('1', (target_w, target_h), color=1)
            draw = ImageDraw.Draw(img)
            
            # 置中計算
            bbox = draw.textbbox((0, 0), char, font=font)
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
            draw.text(((target_w - w)//2 - bbox[0] + x_offset, 
                       (target_h - h)//2 - bbox[1] + y_offset), 
                      char, font=font, fill=0)
            
            # 顯示預覽
            preview_cols[i].image(img.resize((target_w*4, target_h*4), resample=Image.NEAREST), caption=char)

            # 取模核心邏輯
            data = []
            for row in range(target_h):
                for b in range(bytes_per_row):
                    byte_val = 0
                    for bit in range(8):
                        pixel_x = b * 8 + bit
                        if pixel_x < target_w: # 防止超過邊界
                            if img.getpixel((pixel_x, row)) == 0:
                                byte_val |= (1 << (7 - bit))
                    data.append(f"0x{byte_val:02X}")
            
            results.append(f'/*-- {char} --*/\n{{"{char}",\n{", ".join(data)}}},')

        st.subheader("📋 產出的 C 語言數組")
        st.code("\n\n".join(results), language="c")

    except Exception as e:
        st.error(f"錯誤: {e}")
