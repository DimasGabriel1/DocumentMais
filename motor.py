from playwright.sync_api import sync_playwright
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from datetime import datetime
import pyautogui
import time
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


# ---------------------- CONFIGURAÇÃO ----------------------
LINK_DESKTOP = ""
LINK_MOBILE = ""
LINK_HIBRIDO = ""


Tempo = 10
NUM_PRINTS = 4
INTERVALO = 0.5


LIMITE_DIFERENCA_DESKTOP = 15000
LIMITE_DIFERENCA_MOBILE = 2900


TEMPO_INATIVIDADE = 10
TEMPO_ESTABILIZACAO = 3
TEMPO_ESPERA_SCROLL = 3.0


# ---------------------- PASTAS ----------------------
def criar_pastas():
    for p in ["prints/desktop", "prints/mobile", "pdf", "capa", "final", "GAM"]:
        os.makedirs(p, exist_ok=True)


# ---------------------- CAPA ----------------------
def gerar_capa_temporaria(dados):
    caminho_orig = "capa/CAPA.png"
    caminho_temp = "capa/_CAPA_TEMP.png"
    if not os.path.exists(caminho_orig):
        return None


    img = Image.open(caminho_orig).copy()
    draw = ImageDraw.Draw(img)
    largura, altura = img.size


    try:
        f_bold = ImageFont.truetype("fonts/OpenSans-Bold.ttf", 45)
        f_reg = ImageFont.truetype("fonts/OpenSans-Regular.ttf", 45)
    except:
        f_bold = ImageFont.load_default()
        f_reg = ImageFont.load_default()


    campos = [
        ("Cliente:", dados["cliente"]),
        ("CNPJ:", dados["cnpj"]),
        ("PI:", dados["pi"]),
        ("Campanha:", dados["campanha"]),
    ]


    margem_dir = largura - 200
    y = 750
    espacamento = 65


    for tit, val in campos:
        if not val:
            continue
        txt_v = f" {val}"
        bt = draw.textbbox((0, 0), tit, font=f_bold)
        bv = draw.textbbox((0, 0), txt_v, font=f_reg)
        x_ini = margem_dir - ((bt[2] - bt[0]) + (bv[2] - bv[0]))
        draw.text((x_ini, y), tit, fill="black", font=f_bold)
        draw.text((x_ini + (bt[2] - bt[0]), y), txt_v, fill="black", font=f_reg)
        y += espacamento


    img.save(caminho_temp)
    return caminho_temp


# ---------------------- GAM ----------------------
def gerar_gam_temporario(periodo):
    pasta = "GAM"
    arqs = sorted([f for f in os.listdir(pasta) if f.lower().endswith(".png") and not f.startswith("_")])
    if not arqs:
        return None


    caminho_orig = os.path.join(pasta, arqs[0])
    caminho_temp = "GAM/_GAM_TEMP.png"


    img_orig = Image.open(caminho_orig).convert("RGB")
    largura, altura = img_orig.size
    alt_tarja = int(altura * 0.20)


    nova_img = Image.new("RGB", (largura, altura + alt_tarja), color="white")
    nova_img.paste(img_orig.resize((largura, altura), Image.LANCZOS), (0, alt_tarja))
    draw = ImageDraw.Draw(nova_img)


    try:
        f_bold = ImageFont.truetype("fonts/OpenSans-Bold.ttf", 55)
        f_reg = ImageFont.truetype("fonts/OpenSans-Regular.ttf", 40)
    except:
        f_bold = ImageFont.load_default()
        f_reg = ImageFont.load_default()


    tit = "Comprovante de Veiculação de Banner"
    per_txt = f"Período de veiculação: {periodo}"
    m_dir = largura - 50
    bt = draw.textbbox((0, 0), tit, font=f_bold)
    bp = draw.textbbox((0, 0), per_txt, font=f_reg)


    draw.text((m_dir - (bt[2] - bt[0]), int(alt_tarja * 0.17)), tit, fill="black", font=f_bold)
    draw.text((m_dir - (bp[2] - bp[0]), int(alt_tarja * 0.65)), per_txt, fill="black", font=f_reg)


    nova_img.save(caminho_temp)
    return caminho_temp


# ---------------------- FINAL ----------------------
def gerar_final_temporario():
    caminho_orig = "final/FINAL.png"
    caminho_temp = "final/_FINAL_TEMP.png"
    if not os.path.exists(caminho_orig):
        return None


    img = Image.open(caminho_orig).copy()
    draw = ImageDraw.Draw(img)
    try:
        f_reg = ImageFont.truetype("fonts/OpenSans-Regular.ttf", 25)
    except:
        f_reg = ImageFont.load_default()


    meses = {
        1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
        5: "maio", 6: "junho", 7: "julho", 8: "agosto",
        9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
    }
    agora = datetime.now()
    txt_data = f"Fortaleza, {agora.strftime('%d')} de {meses[agora.month]} de {agora.year}"
    draw.text((130, img.size[1] - 300), txt_data, fill="black", font=f_reg)
    img.save(caminho_temp)
    return caminho_temp


# PDF
def gerar_pdf_unico(dados_capa, prestacao):
    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    nome_pdf = f"pdf/relatorio_{timestamp}.pdf"
    c = canvas.Canvas(nome_pdf)
    elementos = []

    if prestacao and dados_capa:
        capa = gerar_capa_temporaria(dados_capa)
        if capa:
            elementos.append(capa)
        gam = gerar_gam_temporario(dados_capa["periodo"])
        if gam:
            elementos.append(gam)


    for p in ["prints/desktop", "prints/mobile"]:
        if os.path.exists(p):
            arqs = sorted([f for f in os.listdir(p) if f.lower().endswith(".png")])
            for f in arqs:
                elementos.append(os.path.join(p, f))


    if prestacao:
        final = gerar_final_temporario()
        if final:
            elementos.append(final)
    else:
        
        final = None


    if not elementos:
        print("ERRO: Nenhum arquivo encontrado.")
        return


    for img_path in elementos:
        imagem = ImageReader(img_path)
        w, h = imagem.getSize()
        c.setPageSize((w, h))
        c.drawImage(imagem, 0, 0, width=w, height=h)
        c.showPage()
        if "_TEMP" in img_path:
            try:
                os.remove(img_path)
            except:
                pass


    c.save()
    print("PDF gerado:", nome_pdf)


def capturar_prints(page, tipo):
    page.evaluate(
        "window.lastScrollTime = 0; window.addEventListener('scroll', () => { window.lastScrollTime = Date.now(); });"
    )
    cont = 0
    frames = []
    u_mud = time.time()
    time.sleep(1.5)
    lim = LIMITE_DIFERENCA_MOBILE if tipo == "mobile" else LIMITE_DIFERENCA_DESKTOP
    lim_calc = lim / 16


    while cont < NUM_PRINTS:
        agora = page.evaluate('Date.now()')
        u_scr = page.evaluate('window.lastScrollTime') or 0
        if (agora - u_scr) / 1000.0 < TEMPO_ESPERA_SCROLL:
            u_mud = time.time()
            time.sleep(0.5)
            continue


        tela = pyautogui.screenshot()
        img_np = np.array(tela)
        altura_total = img_np.shape[0]


        if tipo == "mobile":
            topo = int(altura_total * 0.10)
            f_at = cv2.cvtColor(img_np[topo:, :600], cv2.COLOR_RGB2GRAY)
        else:
            topo = int(altura_total * 0.15)
            f_at = cv2.cvtColor(img_np[topo:, :], cv2.COLOR_RGB2GRAY)


        f_at_reduzido = cv2.resize(f_at, (0, 0), fx=0.25, fy=0.25)
        salv = True
        for f in frames:
            if np.sum(cv2.absdiff(f, f_at_reduzido)) < lim_calc:
                salv = False
                break


        if salv:
            ts = datetime.now().strftime("%d-%m-%Y_%H-%M-%S_%f")
            cam = f"prints/{tipo}/{ts}.png"
            tela.save(cam)
            frames.append(f_at_reduzido)
            cont += 1
            u_mud = time.time()
            print(f"[{tipo.upper()}] Print {cont} salvo!")


        if (time.time() - u_mud) > TEMPO_INATIVIDADE:
            break
        time.sleep(INTERVALO)


# NAVEGADOR
def abrir_navegador(playwright, link, tipo):
    args_rapidos = [
        "--start-maximized",
        "--disable-extensions",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--no-sandbox",
        "--no-first-run",
        "--no-zygote",
        "--disable-notifications"
    ]
    browser = playwright.chromium.launch(
        executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        headless=False,
        args=args_rapidos
    )
    if tipo == "mobile":
        ctx = browser.new_context(
            viewport={"width": 390, "height": 844},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)",
            is_mobile=True
        )
    else:
        ctx = browser.new_context(no_viewport=True)
    page = ctx.new_page()
    try:
        page.goto(link, wait_until="domcontentloaded", timeout=90000)
    except:
        print("Aviso: Site demorou muito, tentando mesmo assim...")
    time.sleep(Tempo)
    capturar_prints(page, tipo)
    browser.close()



def executar(link_desktop="", link_mobile="", link_hibrido="", prestacao=True, dados_capa=None):
    global LINK_DESKTOP, LINK_MOBILE, LINK_HIBRIDO
    LINK_DESKTOP = link_desktop
    LINK_MOBILE = link_mobile
    LINK_HIBRIDO = link_hibrido
    criar_pastas()
    with sync_playwright() as p:
        if LINK_DESKTOP.strip():
            abrir_navegador(p, LINK_DESKTOP, "desktop")
        if LINK_MOBILE.strip():
            abrir_navegador(p, LINK_MOBILE, "mobile")
        if LINK_HIBRIDO.strip():
            abrir_navegador(p, LINK_HIBRIDO, "desktop")
            abrir_navegador(p, LINK_HIBRIDO, "mobile")
    gerar_pdf_unico(dados_capa, prestacao)
    print("Processo finalizado!")