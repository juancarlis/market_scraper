from playwright.sync_api import sync_playwright
import json
import time


class DiaScraper:
    BASE_URL = "https://diaonline.supermercadosdia.com.ar/"

    def __init__(self, search_term: str):
        self.search_term = search_term

    def fetch_products(self):
        product_list = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            page = browser.new_page()

            url = f"{self.BASE_URL}{self.search_term}"
            print(f"Loading URL: {url}")
            page.goto(url)

            # Espera 5s para que aparezca el popup ClubDia (igual que en test.py)
            time.sleep(5)

            # Cerrar el popup de ClubDia
            popup_btn = page.query_selector(
                "button.diaio-custom-clubdia-0-x-popup_clubdia__button"
            )
            if popup_btn:
                print("Se encontró el botón del popup. Hacemos click para cerrarlo.")
                popup_btn.click()
                try:
                    page.wait_for_selector(
                        "div.diaio-custom-clubdia-0-x-popup_clubdia__elements",
                        state="detached",
                        timeout=5000,
                    )
                    print("Popup cerrado correctamente.")
                except:
                    print("El popup no se cerró a tiempo o ya estaba cerrado.")

            # Esperar a que aparezcan los artículos
            page.wait_for_selector(
                "article.vtex-product-summary-2-x-element", timeout=10000
            )

            # Capturar todos los links de producto globalmente
            links = page.query_selector_all("a.vtex-product-summary-2-x-clearLink")
            link_hrefs = [
                f"{self.BASE_URL}{link.get_attribute('href').strip()}"
                for link in links
                if link.get_attribute("href")
            ]
            print(f"Found {len(link_hrefs)} product links.")

            # Obtener contenedores de productos
            product_containers = page.query_selector_all(
                "article.vtex-product-summary-2-x-element"
            )
            print(f"Found {len(product_containers)} product containers.")

            for idx, container in enumerate(product_containers):
                try:
                    # Extraer datos del producto
                    name_tag = container.query_selector(
                        "span.vtex-product-summary-2-x-productBrand"
                    )
                    price_tag = container.query_selector(
                        "span.diaio-store-5-x-sellingPriceValue"
                    )
                    discount_tag = container.query_selector(
                        "div.vtex-store-components-3-x-discountInsideContainer"
                    )
                    image_tag = container.query_selector(
                        "img.vtex-product-summary-2-x-imageNormal"
                    )

                    name = name_tag.inner_text().strip() if name_tag else "No name"
                    price = price_tag.inner_text().strip() if price_tag else "No price"
                    discount = (
                        discount_tag.inner_text().strip()
                        if discount_tag
                        else "No discount"
                    )
                    image = (
                        image_tag.get_attribute("src").strip()
                        if image_tag
                        else "No image"
                    )

                    # Asociar el enlace global al producto (por índice)
                    link = link_hrefs[idx] if idx < len(link_hrefs) else "No link"

                    print(f"Extracted product: {name}, {price}, {discount}, {link}")
                    product_list.append(
                        {
                            "name": name,
                            "price": price,
                            "discount": discount,
                            "image": image,
                            "link": link,
                        }
                    )
                except Exception as e:
                    print(f"Error extracting product: {e}")

            browser.close()
        return product_list

    def save_to_file(self, data, file_name="products_dia.json"):
        """Guarda la lista de productos en un archivo JSON."""
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {file_name}")
