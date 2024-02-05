import os
import numpy as np
import pandas as pd
import cv2
import re
import pytesseract

from PIL import Image
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

pytesseract.pytesseract.tesseract_cmd = (
    r"C:/Users/alinrob/AppData/Local/Programs/Tesseract-OCR/tesseract.exe"
)
tessdata_dir_config = (
    r'--tessdata-dir "D:/proyectos/webscraping-susalud/data/tessdata-main"'
)


HEAD = [
    "PERÍODO",
    "TIPO DOCUMENTO",
    "CÓDIGO DOCUMENTO",
    "NOMBRE DE IAFAS",
    "REGIMEN",
    "FECHA DE INICIO",
    "FECHA DE FIN",
    "TIPO DE PLAN DE SALUD",
    "ESTADO",
]


def get_txt_captcha(path, scale=150):

    if os.path.exists(path):
        image = Image.open(path).convert("RGB")
        os.remove(path)
        imageArray = np.array(image)
        imageArray = imageArray[:, :, ::-1].copy()
        imageArray = cv2.bitwise_not(imageArray)

        # Cambiar el tamaño a 150%
        width = int(imageArray.shape[1] * scale / 100)
        height = int(imageArray.shape[0] * scale / 100)
        dim = (width, height)
        imageArray = cv2.resize(imageArray, dim, interpolation=cv2.INTER_AREA)

        # Convertir a blanco y negro
        imageArray = cv2.cvtColor(imageArray, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(imageArray, 127, 255, cv2.THRESH_BINARY)
        txt = pytesseract.image_to_string(thresh, config=tessdata_dir_config)
        txt = re.sub(r"[^a-zA-Z0-9]", "", txt)
        if len(txt) > 1:
            return txt
    return None


def screenshop(driver, path_to_save, ubicacion=(57.5, 310, 175, 355)):
    try:
        driver.save_screenshot(path_to_save)
        img = Image.open(path_to_save)
        img = img.crop(ubicacion)
        img.save(path_to_save)
        return True
    except:
        return False


def path_exist(driver, xpath):
    try:
        driver.find_element(By.XPATH, xpath)
        return True
    except NoSuchElementException:
        return False


def buscador(
    driver,
    xpath_nro_documento,
    cod_documento,
    xpath_txt_captcha,
    txt_captcha,
    xpath_btn_consultar,
    xpath_resultado,
):
    try:
        driver.find_element(By.XPATH, xpath_nro_documento).send_keys(cod_documento)
        driver.find_element(By.XPATH, xpath_txt_captcha).send_keys(txt_captcha)
        driver.find_element(By.XPATH, xpath_btn_consultar).click()
        if path_exist(driver, xpath_resultado):
            return True
        return False
    except:
        return False


def get_content_by_rows(
    driver, xpath_resultado, cod_documento, tipo_documento, periodo
):
    try:
        content = []
        tabla_elemento = driver.find_element(By.XPATH, xpath_resultado)
        filas = tabla_elemento.find_elements(By.TAG_NAME, "tr")
        for idx, fila in enumerate(filas):
            if idx > 0:
                tds = fila.find_elements(By.TAG_NAME, "td")
                th = fila.find_element(By.TAG_NAME, "th").text
                datos_fila = [td.text for td in tds]
                datos_fila.insert(0, th)
                datos_fila.insert(0, cod_documento)
                datos_fila.insert(0, tipo_documento)
                datos_fila.insert(0, periodo)
                content.append(datos_fila)

        return pd.DataFrame(content, columns=HEAD)
    except:
        return None

