"""Portable font setup; no data access."""
import matplotlib.pyplot as plt
from matplotlib import font_manager

def setup_korean_font():
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in ['Apple SD Gothic Neo', 'Malgun Gothic', 'NanumGothic', 'Noto Sans CJK KR']:
        if name in available:
            plt.rcParams['font.family'] = name
            break
    plt.rcParams['axes.unicode_minus'] = False
