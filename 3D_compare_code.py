
import numpy as np

import struct
import plotly.graph_objects as go
from pathlib import Path
from tkinterdnd2 import TkinterDnD, DND_FILES
import sys
import tkinter as tk



def get_file_path():
    # 드래그 앤 드롭 창 생성
    root = TkinterDnD.Tk()
    root.withdraw()  # 창을 최소화한 상태로 시작

    # 파일 경로를 저장할 변수 생성
    file_path = None

    # 드롭 이벤트 처리 함수
    def on_drop(event):
        nonlocal file_path
        file_path = event.data  # 드롭된 파일의 경로 저장
        root.quit()  # 경로 저장 후 창 닫기
        root.destroy()

    def on_close():
        sys.exit()
    # 드래그 앤 드롭 설정
    root.drop_target_register(DND_FILES)
    root.dnd_bind('<<Drop>>', on_drop)
    root.protocol("WM_DELETE_WINDOW", on_close)  # 창 닫기 이벤트 처리
    # 드래그 앤 드롭 안내 라벨 생성
    label = tk.Label(root, text="Drag a file here", width=40, height=10)
    label.pack(padx=20, pady=20)

    root.deiconify()  # 창을 화면에 보이게 함
    root.mainloop()  # 이벤트 루프 실행

    # 창이 닫힌 후 경로 반환
    return file_path



def read_dat(path: str) -> np.ndarray:
    with open(path, 'rb') as f:
        width, height = struct.unpack('<2i', f.read(8))
        data = np.fromfile(f, dtype='<f4', count=width * height)
    return data.reshape((height, width))


img_0_path = get_file_path()
img_1_path = get_file_path()
# Load the two uploaded height‑map files


img0 = read_dat(img_0_path)
img1 = read_dat(img_1_path)

# ---- 3. Build 3‑D overlay figure ----
fig = go.Figure()

# Surface #0
fig.add_trace(go.Surface(
    z=img0,
    colorscale="Viridis",
    name="tip0",
    opacity=1.0
))
# Surface #1
fig.add_trace(go.Surface(
    z=img1,
    colorscale="Reds",
    name="tip1",
    opacity=0.5
))

# --- Sliders ---
alphas = [round(a,1) for a in np.linspace(0,1,11)]          # 0.0 … 1.0
scales = [0.25, 0.5, 0.75, 1.0]                             # Z‑scale

# Slider A – tip0 opacity
steps0 = [
    dict(method="restyle",
         args=["opacity", a, [0]],     # only trace 0
         label=f"{a:.1f}")
    for a in alphas
]

# Slider B – tip1 opacity
steps1 = [
    dict(method="restyle",
         args=["opacity", a, [1]],     # only trace 1
         label=f"{a:.1f}")
    for a in alphas
]

# Slider C – Z scale (both surfaces)
steps_scale = [
    dict(method="update",
         args=[{"z": [img0 * s, img1 * s]}],
         label=f"{s:.2f}")
    for s in scales
]

fig.update_layout(
    title="Solder Tip Height‑Map Overlay (Opacity & Z‑Scale Control)",
    scene=dict(aspectmode="data"),
    sliders=[
        dict(active=len(alphas)-1, x=0.15, y=0.05,
             currentvalue={"prefix": "Tip0 α: "}, steps=steps0),
        dict(active=5, x=0.15, y=0.00,
             currentvalue={"prefix": "Tip1 α: "}, steps=steps1),
        dict(active=len(scales)-1, x=0.15, y=0.10,
             currentvalue={"prefix": "Z‑Scale: "}, steps=steps_scale)
    ]
)

fig.show()

# # ---- 4. Save to HTML so the user can open locally ----
# html_path = Path("solder_overlay_full.html")
# fig.write_html(html_path, include_plotlyjs="cdn")