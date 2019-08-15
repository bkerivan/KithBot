from urlparse import urlparse
from json import loads
from dateutil.parser import parse

class InvalidVariantError(Exception):
    pass

class Product:
    def __init__(self, session, url):
        self.session = session
        self.url = url
        urlparts = urlparse(url)
        self.base_url = "https://" + urlparts.netloc
        self.carted = False

    def load_product_data(self):
        r = self.session.get(self.url + ".json", verify=False)
        if r.status_code != 200:
            r.raise_for_status()
        json_data = loads(r.text)
        self.id = json_data["product"]["id"]
        self.title = json_data["product"]["title"]
        self.product_handle = json_data["product"]["handle"]
        self.last_update = parse(json_data["product"]["updated_at"])
        self.variants = {}
        for v in json_data["product"]["variants"]:
            self.variants[v["title"]] = {"id":v["id"], "price":v["price"],
                                         "sku":v["sku"],
                                         "last_update":parse(v["updated_at"])}

    def get_variant_titles(self):
        return self.variants.keys()

    def add_to_cart(self, variant_title, quantity):
        add_url = self.base_url + "/cart/add.js"
        try:
            variant = self.variants[variant_title]
        except KeyError:
            raise InvalidVariantError
        r = self.session.post(add_url,
                              data={"id":variant["id"], "quantity":quantity})
        if r.status_code != 200:
            r.raise_for_status()
        self.carted = True
