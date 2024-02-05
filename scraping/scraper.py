from utils import helpers
from selenium import webdriver

import time

XPATH_NRO_DOC = "//input[@id='txtNroDoc']"
XPATH_TXT_CAPTCHA = "//input[@id='txtCaptcha']"
XPATH_BTN_CONSULTAR = "//input[@id='btnConsultar']"
XPATH_RESULTADO = "//div[@id='divResultado']/descendant::table/tbody"

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


def session(path_driver, url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("user-agent=[user-agent string]")
    options.add_argument("executable_path=" + path_driver)
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    return driver


def run_scraper(
        driver,
        url,
        path_to_save_img,
        period,
        document_type,
        document_code,
        max_attempt=15,
):
    attempt = 1
    while attempt <= max_attempt:
        try:
            driver.get(url)
            time.sleep(2)

            if any(
                    [
                        not helpers.path_exist(driver, XPATH_NRO_DOC),
                        not helpers.path_exist(driver, XPATH_TXT_CAPTCHA),
                        not helpers.path_exist(driver, XPATH_BTN_CONSULTAR),
                        not helpers.screenshop(driver, path_to_save_img),
                    ]
            ):
                continue

            txt_captcha = helpers.get_txt_captcha(path_to_save_img)

            if txt_captcha:
                new_document_code = document_code
                if document_type == "RUC":
                    new_document_code = new_document_code[2:10]

                if helpers.buscador(
                        driver,
                        XPATH_NRO_DOC,
                        new_document_code,
                        XPATH_TXT_CAPTCHA,
                        txt_captcha,
                        XPATH_BTN_CONSULTAR,
                        XPATH_RESULTADO,
                ):
                    return helpers.get_content_by_rows(
                        driver, XPATH_RESULTADO, new_document_code, document_type, period
                    )
        finally:
            attempt += 1
    return None
