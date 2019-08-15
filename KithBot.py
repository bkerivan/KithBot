from requests import Session
from requests.packages.urllib3 import disable_warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from Product import Product
from IOFormat import TextFormats, colorize

disable_warnings(InsecureRequestWarning)

bot_user_agent = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:57.0) Gecko/20100101 Firefox/57.0"
ups_ground = "shopify-UPS%20GROUND%20(5-7%20business%20days)-10.00"
card_vault_url = "https://elb.deposit.shopifycs.com/sessions"

class SoldOutError(Exception):
    pass

class CartError(Exception):
    pass

class KithBot:
    def __init__(self, user, address, credit_card):
        self.base_url = "https://kith.com"
        self.session = Session()
        self.browser_info = {}
        self.set_user_agent(bot_user_agent)
        self.set_browser_dimensions(1054, 663)
        self.cart = []
        self.user = user
        self.address = address
        self.credit_card = credit_card
        self.initialize_checkout_data()

    def set_user_agent(self, user_agent):
        self.browser_info["user_agent"] = user_agent
        self.session.headers.update({"User-Agent":user_agent})

    def set_browser_dimensions(self, width, height):
        self.browser_info["width"] = str(width)
        self.browser_info["height"] = str(height)

    def add_to_cart(self, product_url, variant_title, quantity):
        product = Product(self.session, product_url)
        product.load_product_data()
        product.add_to_cart(variant_title, quantity)
        self.cart.insert(0, (product, variant_title, quantity))

    def change_cart_quantity(self, product, variant, new_quantity): 
        products = [(p.title, v) for p, v, q in self.cart]
        try:
            pos = products.index((product, variant))
        except ValueError:
            raise CartError
        r = self.session.post(self.base_url + "/cart/change.js",
                              data={"quantity":new_quantity,
                                    "line":pos + 1})
        if r.status_code != 200:
            r.raise_for_status()
        if not new_quantity:
            p = self.cart[pos][0] 
            q = self.cart[pos][2]
            self.cart.remove((p, variant, q))
        else:
            self.cart[pos][2] = new_quantity

    def remove_from_cart(self, product, variant):
        self.change_cart_quantity(product, variant, 0)
        
    def debug_show_cart(self):
        r = self.session.get(self.base_url + "/cart.js")
        if r.status_code != 200:
            r.raise_for_status()
        print(r.text.encode("utf-8"))

    def get_authenticity_token(self, html, data_step):
        start = html.index('data-step="{}"'.format(data_step))
        start = html.index("authenticity_token", start)
        return html[start:].split('value="')[1].split('"')[0]

    def get_cart_price(self, html):
        return html.split('data-checkout-payment-due-target="')[1].split('"')[0]

    def get_payment_gateway(self, html):
        start = html.index('data-gateway-group="direct"')
        return html[start:].split('data-select-gateway="')[1].split('"')[0]

    def get_sold_out_product(self, html):
        product = html.split('<span class="product__description__name order-summary__emphasis">')[1].split("<")[0] 
        variant = html.split('<span class="product__description__variant order-summary__small-text">')[1].split("<")[0]
        return product, variant

    def initialize_checkout_data(self):
        initiate = {"updates[]":"1", "checkout":"Check Out"}
        contact_info = {"_method":"patch", "authenticity_token":"", "button":"",
                        "checkout[buyer_accepts_marketing]":{"0":"0", "1":"1"},
                        "checkout[client_details][browser_height]":
                        self.browser_info["height"],
                        "checkout[client_details][browser_width]":
                        self.browser_info["width"],
                        "checkout[client_details][javascript_enabled]":"0",
                        "checkout[email]":self.user["email"],
                        "checkout[shipping_address][address1]":
                        self.address["address1"],
                        "checkout[shipping_address][address2]":
                        self.address["address2"],
                        "checkout[shipping_address][city]":
                        self.address["city"],
                        "checkout[shipping_address][country]":
                        self.address["country"],
                        "checkout[shipping_address][first_name]":
                        self.user["first_name"],
                        "checkout[shipping_address][last_name]":
                        self.user["last_name"],
                        "checkout[shipping_address][phone]":
                        self.address["phone"],
                        "checkout[shipping_address][province]":
                        self.address["province"],
                        "checkout[shipping_address][zip]":
                        self.address["zipcode"],
                        "previous_step":"contact_information",
                        "step":"shipping_method", "utf8":u'\u2713'}
        shipping_method = {"_method":"patch", "authenticity_token":"",
                           "button":"",
                           "checkout[client_details][browser_height]":
                           self.browser_info["height"],
                           "checkout[client_details][browser_width]":
                           self.browser_info["width"],
                           "checkout[client_details][javascript_enabled]":"0",
                           "checkout[shipping_rate][id]":ups_ground,
                           "previous_step":"shipping_method",
                           "step":"payment_method",
                           "utf8":u'\u2713'}
        payment_method = {"credit_card":{"number":self.credit_card["number"],
                                         "name":self.credit_card["name"],
                                         "month":int(self.credit_card["month"]),
                                         "year":
                                         2000 + int(self.credit_card["year"]),
                                         "verification_value":
                                         self.credit_card["code"]}}
        submit_payment = {"utf8":u'\u2713', "_method":"patch",
                          "authenticity_token":"",
                          "previous_step":"payment_method", "step":"", "s":"",
                          "checkout[payment_gateway]":"",
                          "checkout[credit_card][vault]":"false",
                          "checkout[different_billing_address]":"false",
                          "checkout[billing_address][first_name]":
                          self.user["first_name"],
                          "checkout[billing_address][last_name]":
                          self.user["last_name"],
                          "checkout[billing_address][address1]":
                          self.address["address1"],
                          "checkout[billing_address][address2]":
                          self.address["address2"],
                          "checkout[billing_address][city]":
                          self.address["city"],
                          "checkout[billing_address][country]":
                          self.address["country"],
                          "checkout[billing_address][province]":
                          self.address["province"],
                          "checkout[billing_address][zip]":
                          self.address["zipcode"],
                          "checkout[billing_address][phone]":
                          self.address["phone"],
                          "checkout[remember_me]":"false",
                          "checkout[remember_me]":"0",
                          "checkout[vault_phone]":"",
                          "checkout[total_price]":"",
                          "complete":"1",
                          "checkout[client_details][browser_width]":
                          self.browser_info["width"],
                          "checkout[client_details][browser_height]":
                          self.browser_info["height"],
                          "checkout[client_details][javascript_enabled]":"0"}
        self.checkout_data = {"initiate":initiate, "contact_info":contact_info,
                              "shipping_method":shipping_method,
                              "payment_method":payment_method,
                              "submit_payment":submit_payment}
        
    def check_out(self):
        r = self.session.post(self.base_url + "/cart",
                              data=self.checkout_data["initiate"])
        if r.status_code != 200:
            r.raise_for_status()
        if "stock_problems" in r.text.encode("utf-8"):
            product, variant = self.get_sold_out_product(r.text.encode("utf-8"))
            self.remove_from_cart(product, variant)
            raise SoldOutError
        checkout_url = r.url
        authenticity_token = self.get_authenticity_token(r.text.encode("utf-8"),
                                                         "contact_information")
        self.checkout_data["contact_info"]["authenticity_token"] = authenticity_token
        r = self.session.post(checkout_url,
                              data=self.checkout_data["contact_info"])
        if r.status_code != 200:
            r.raise_for_status()
        authenticity_token = self.get_authenticity_token(r.text.encode("utf-8"),
                                                         "shipping_method")
        self.checkout_data["shipping_method"]["authenticity_token"] = authenticity_token
        r = self.session.post(checkout_url,
                              data=self.checkout_data["shipping_method"])
        if r.status_code != 200:
            r.raise_for_status()
#        print("[DEBUG]: URL: {}".format(r.url))
        r = self.session.get(r.url)
        if r.status_code != 200:
            r.raise_for_status()
        payment_gateway = self.get_payment_gateway(r.text.encode("utf-8"))
        self.checkout_data["submit_payment"]["checkout[payment_gateway]"] = payment_gateway
#        print("[DEBUG]: Payment Gateway: {}".format(payment_gateway))
        price = self.get_cart_price(r.text.encode("utf-8"))
        self.checkout_data["submit_payment"]["checkout[total_price]"] = price
#        print("[DEBUG]: Cart Price: ${:,.2f}".format(float(price) / 100))
        authenticity_token = self.get_authenticity_token(r.text.encode("utf-8"),
                                                         "payment_method")
        self.checkout_data["submit_payment"]["authenticity_token"] = authenticity_token
#        print("[DEBUG]: Authenticity Token: {}".format(authenticity_token))
        r = self.session.post(card_vault_url,
                              json=self.checkout_data["payment_method"])
        if r.status_code != 200:
            r.raise_for_status()
        data = r.json()
        self.checkout_data["submit_payment"]["s"] = data["id"]
#        print("[DEBUG]: s = {}".format(data["id"]))
#        r = self.session.post(checkout_url,
#                              data=self.checkout_data["submit_payment"])
#        if r.status_code != 200:
#            r.raise_for_status()

    def cop(self, product_url, variant_title, quantity=1): 
        self.add_to_cart(product_url, variant_title, quantity)
        try:
            self.check_out()
        except SoldOutError:
            raise SoldOutError
        for p, v, q in self.cart:
            print(colorize("$Copped {} -- {} ({})$".format(p.title, v, q),
                           TextFormats.GREEN + TextFormats.BOLD))
            self.remove_from_cart(p.title, v)

    def cop_first_available_variant(self, product_url, quantity=1):
        product = Product(self.session, product_url)
        product.load_product_data()
        variant_titles = product.get_variant_titles()
        for variant_title in variant_titles:
            product.add_to_cart(variant_title, quantity)
            self.cart.insert(0, (product, variant_title, quantity))
            try:
                self.check_out()
            except SoldOutError:
                continue
            else:
                break
        if self.cart:
            for p, v, q in self.cart:
                print(colorize("$Copped {} -- {} ({})$".format(p.title, v, q),
                               TextFormats.GREEN + TextFormats.BOLD))
                self.remove_from_cart(p.title, v)
        else:
            raise SoldOutError

    def close(self):
        self.session.close()

