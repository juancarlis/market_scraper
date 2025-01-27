from scrapers.dia_scraper import DiaScraper

if __name__ == "__main__":
    scraper = DiaScraper("leche descremada")
    data = scraper.fetch_products()
    scraper.save_to_file(data)
