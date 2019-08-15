from json import dump, load

_data_path = "data.json"

class NoDataError(Exception):
    pass

class InvalidDefaultError(Exception):
    pass

class InvalidUserError(Exception):
    pass

class InvalidAddressError(Exception):
    pass

class InvalidCreditCardError(Exception):
    pass

class DataManager:
    def __init__(self, data_path=_data_path):
        self.data_path = _data_path
        self.users = {}
        self.addresses = {}
        self.credit_cards = {}
        self.user_count = 0
        self.address_count = 0
        self.credit_card_count = 0

    def load_data(self):
        try:
            fp = open(self.data_path, "r")
        except IOError:
            raise NoDataError
        else:
            data = load(fp)
            self.user_count = data["user_count"]
            self.users = data["users"]
            self.address_count = data["address_count"]
            self.addresses = data["addresses"]
            self.credit_card_count = data["credit_card_count"]
            self.credit_cards = data["credit_cards"]
            fp.close()

    def save_data(self):
        data = {"user_count":self.user_count, "users":self.users,
                "address_count":self.address_count, "addresses":self.addresses,
                "credit_card_count":self.credit_card_count,
                "credit_cards":self.credit_cards}
        with open(self.data_path, "w") as fp:
            dump(data, fp)

    def add_user(self, email, first_name, last_name, username="",
                 default_address="", default_credit_card=""):
        self.user_count += 1
        if not username:
            username = "User" + str(self.user_count)
        self.users[username] = {"email":email, "first_name":first_name,
                                "last_name":last_name,
                                "default_address":default_address,
                                "default_credit_card":default_credit_card}
        return username

    def edit_user(self, username, email="", first_name="", last_name="",
                  default_address="", default_credit_card="", new_username=""):
        try:
            user = self.users[username]
        except KeyError:
            raise InvalidUserError
        if email:
            user["email"] = email
        if first_name:
            user["first_name"] = first_name
        if last_name:
            user["last_name"] = last_name
        if default_address:
            try:
                self.addresses[default_address]
            except KeyError:
                raise InvalidDefaultError
            user["default_address"] = default_address
        if default_credit_card:
            try:
                self.credit_cards[default_credit_card]
            except KeyError:
                raise InvalidDefaultError
            user["default_credit_card"] = default_credit_card
        if new_username:
            self.users[new_username] = self.users.pop(username)
            
    def add_address(self, address1, address2, city, country, province,
                    zipcode, phone, address_name=""):
        self.address_count += 1
        if not address_name:
            address_name = "Address" + str(self.address_count)
        self.addresses[address_name] = {"address1":address1,
                                        "address2":address2, "city":city,
                                        "country":country, "province":province,
                                        "zipcode":zipcode, "phone":phone}
        return address_name

    def edit_address(self, address_name, address1="", address2="", city="",
                     country="", province="", zipcode="", phone="",
                     new_address_name=""):
        try:
            address = self.addresses[address_name]
        except KeyError:
            raise InvalidAddressError
        if address1:
            address["address1"] = address1
        if address2:
            address["address2"] = address2
        if city:
            address["city"] = city
        if country:
            address["country"] = country
        if province:
            address["province"] = province
        if zipcode:
            address["zipcode"] = zipcode
        if phone:
            address["phone"] = phone
        if new_address_name:
            self.addresses[new_address_name] = self.addresses.pop(address_name)

    def add_credit_card(self, number, name, month, year, code, cc_name=""):
        self.credit_card_count += 1
        if not cc_name:
            cc_name = "Card" + str(self.credit_card_count)
        self.credit_cards[cc_name] = {"number":number, "name":name,
                                      "month":month, "year":year, "code":code}
        return cc_name

    def edit_credit_card(self, cc_name, number="", name="", month="", year="",
                         code="", new_cc_name=""):
        try:
            cc = self.credit_cards[cc_name]
        except KeyError:
            raise InvalidCreditCardError
        if number:
            cc["number"] = number
        if name:
            cc["name"] = name
        if month:
            cc["month"] = month
        if year:
            cc["year"] = year
        if code:
            cc["code"] = code
        if new_cc_name:
            self.credit_cards[new_cc_name] = self.credit_cards.pop(cc_name)

