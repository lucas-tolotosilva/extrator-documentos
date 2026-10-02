"""Automação Playwright para gerar as capturas de tela em /screenshots.

Pré-requisitos: backend rodando em :8000 e frontend (vite dev) em :5173.
"""

import time
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE_URL = "http://localhost:5173"
SCREENSHOTS_DIR = Path(__file__).parent.parent / "screenshots"
SAMPLES_DIR = Path(__file__).parent.parent / "samples"

DESKTOP = {"width": 1440, "height": 900}
MOBILE = {"width": 390, "height": 844}


def esperar(page, segundos=1.0):
    time.sleep(segundos)


def run():
    SCREENSHOTS_DIR.mkdir(exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport=DESKTOP, device_scale_factor=2)
        page = context.new_page()

        # 1. Tela de upload inicial
        page.goto(BASE_URL)
        page.wait_for_load_state("networkidle")
        esperar(page)
        page.screenshot(path=str(SCREENSHOTS_DIR / "01_upload_inicial.png"))
        print("01 ok")

        # 2. Upload de múltiplos documentos
        arquivos = [
            str(SAMPLES_DIR / "nota_fiscal_01.pdf"),
            str(SAMPLES_DIR / "nota_fiscal_02.pdf"),
            str(SAMPLES_DIR / "boleto_01.pdf"),
            str(SAMPLES_DIR / "boleto_02.pdf"),
            str(SAMPLES_DIR / "pedido_01.pdf"),
            str(SAMPLES_DIR / "pedido_02.pdf"),
            str(SAMPLES_DIR / "nota_fiscal_06.pdf"),
        ]
        page.locator('input[type="file"]').set_input_files(arquivos)
        esperar(page, 0.5)
        page.screenshot(path=str(SCREENSHOTS_DIR / "02_arquivos_selecionados.png"))
        print("02 ok")

        page.get_by_role("button", name="Extrair dados").click()
        page.wait_for_selector("text=documento(s) processado(s)", timeout=20000)
        esperar(page)
        page.screenshot(path=str(SCREENSHOTS_DIR / "03_resultado_extracao.png"))
        print("03 ok")

        # 4. Tela de revisão
        page.goto(f"{BASE_URL}/revisao")
        page.wait_for_load_state("networkidle")
        esperar(page)
        page.screenshot(path=str(SCREENSHOTS_DIR / "04_tela_revisao_lista.png"))
        print("04 ok")

        # 5. Expandir um card com baixa confiança (nota_fiscal_06 - ambígua)
        card_ambiguo = page.locator(".card-documento", has_text="nota_fiscal_06.pdf")
        card_ambiguo.locator(".card-documento-resumo").click()
        esperar(page)
        card_ambiguo.scroll_into_view_if_needed()
        page.screenshot(path=str(SCREENSHOTS_DIR / "05_revisao_campo_baixa_confianca.png"))
        print("05 ok")

        # 6. Dashboard
        page.goto(f"{BASE_URL}/dashboard")
        page.wait_for_load_state("networkidle")
        esperar(page, 1.5)
        page.screenshot(path=str(SCREENSHOTS_DIR / "06_dashboard.png"), full_page=True)
        print("06 ok")

        context.close()

        # ---------- MOBILE ----------
        context_mobile = browser.new_context(viewport=MOBILE, device_scale_factor=2, is_mobile=True)
        page_m = context_mobile.new_page()
        page_m.goto(BASE_URL)
        page_m.wait_for_load_state("networkidle")
        esperar(page_m)
        page_m.screenshot(path=str(SCREENSHOTS_DIR / "07_mobile_upload.png"))
        print("07 ok")

        context_mobile.close()
        browser.close()


if __name__ == "__main__":
    run()
