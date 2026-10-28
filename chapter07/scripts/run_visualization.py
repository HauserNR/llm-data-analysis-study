"""저장소 루트에서 .venv/bin/python chapter07/scripts/run_visualization.py"""
from pathlib import Path
import sys
import matplotlib

matplotlib.use("Agg")
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "chapter07"))
from src.visualization import prepare_visualization_data, setup_korean_font, create_all_figures


if __name__ == "__main__":
    print("사용 한글 폰트:", setup_korean_font())
    data = prepare_visualization_data(ROOT)
    print(create_all_figures(data, ROOT / "chapter07/images", ROOT / "chapter07/reports"))
