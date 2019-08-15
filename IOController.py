#!/usr/bin/env python2.7

# TODO: credit card expiration date validation, handle KeyboardInterrupt,
#       allow deletion of characters in methods that use getch(),
#       condense functionality into separate functions and classes,
#       prefix ALL "private" functions and helper classes with underscores,
#       find ways to make all lines < 80 columns without impeding performance,
#       organize class methods in most logical layout,
#       change "credit_card" to "cc" in variable names where applicable

from __future__ import print_function

from base64 import b64decode
from validate_email import validate_email
from phonenumbers import AsYouTypeFormatter, parse, NumberParseException
from time import time

from util import getch
from DataManager import DataManager, NoDataError, InvalidDefaultError
from IOMenu import IOMenu
from IOFormat import TextFormats, colorize
from KithBot import KithBot, SoldOutError

import sys

_b64_banner = """
ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICBfX19fX19fX19fCiAgICAgICAgICAgICAg
ICAgICAgICAgICBfX19fX18vIF9fX19fX19fIFxfX19fX18KICAgICAgICAgICAgICAgICAgICAg
ICBfLyAgICAgIF9fX19fX19fX19fXyAgICAgIFxfCiAgICAgICAgICAgICAgICAgICAgIF8vX19f
X19fX19fX19fICAgIF9fX19fX19fX19fX1xfCiAgICAgICAgICAgICAgICAgICAgLyAgX19fX19f
X19fX18gXCAgLyBfX19fX19fX19fXyAgXAogICAgICAgICAgICAgICAgICAgLyAgL1hYWFhYWFhY
WFhYXCBcLyAvWFhYWFhYWFhYWFhcICBcCiAgICAgICAgICAgICAgICAgIC8gIC8jIyMjIyMjIyMj
IyMvICAgIFwjIyMjIyMjIyMjIyNcICBcCiAgICAgICAgICAgICAgICAgIHwgIFxYWFhYWFhYWFhY
WC8gXyAgXyBcWFhYWFhYWFhYWFgvICB8CiAgICAgICAgICAgICAgICBfX3xcX19fX18gICBfX18g
ICAvLyAgXFwgICBfX18gICBfX19fXy98X18KICAgICAgICAgICAgICAgIFtfICAgICAgIFwgICAg
IFwgIFggICAgWCAgLyAgICAgLyAgICAgICBfXQogICAgICAgICAgICAgICAgX198ICAgICBcIFwg
ICAgICAgICAgICAgICAgICAgIC8gLyAgICAgfF9fCiAgICAgICAgICAgICAgICBbX19fXyAgXCBc
IFwgICBfX19fX19fX19fX18gICAvIC8gLyAgX19fX10KICAgICAgICAgICAgICAgICAgICAgXCAg
XCBcIFwvfHwufHwufHwufHwufHxcLyAvIC8gIC8KICAgICAgICAgICAgICAgICAgICAgIFxfIFwg
XCAgfHwufHwufHwufHwufHwgIC8gLyBfLwogICAgICAgICAgICAgICAgICAgICAgICBcIFwgICB8
fC58fC58fC58fC58fCAgIC8gLwogICAgICAgICAgICAgICAgICAgICAgICAgXF8gICB8fF98fF98
fF98fF98fCAgIF8vCiAgICAgICAgICAgICAgICAgICAgICAgICAgIFwgICAgIC4uLi4uLi4uICAg
ICAvCiAgICAgICAgICAgICAgICAgICAgICAgICAgICBcX19fX19fX19fX19fX19fXy8gCgogICAg
ICAgICAgICAgICAgICAgICAgICAgICAg4pW74pSPIOKVu+KVuuKUs+KVuOKVuyDilbvilI/ilJMg
4pSP4pSB4pST4pW64pSz4pW4CiAgICAgICAgICAgICAgICAgICAgICAgICAgICDilKPilLvilJPi
lIMg4pSDIOKUo+KUgeKUq+KUo+KUu+KUk+KUgyDilIMg4pSDIAogICAgICAgICAgICAgICAgICAg
ICAgICAgICAg4pW5IOKVueKVuSDilbkg4pW5IOKVueKUl+KUgeKUm+KUl+KUgeKUmyDilbkgCgo=
"""

class InvalidMenuError(Exception):
    pass

class IOController:
    def __init__(self):
        self.data = DataManager()
        self.bot = None
        self.menus = {}
        self.current_menu = ""
        self.previous_menu = ""
        self.prompt = colorize("$BOT$ > ",
                               TextFormats.BLUE + TextFormats.UNDERLINE)

    def _initialize_menus(self):
        main_menu = IOMenu()
        main_menu.add_option("Users")
        main_menu.add_option("Addresses")
        main_menu.add_option("Credit Cards")
        main_menu.add_option("Log In")
        main_menu.add_option("Exit", 99)
        self.menus["main_menu"] = main_menu
        user_menu = IOMenu()
        user_menu.add_option("Edit Username")
        user_menu.add_option("Edit Email Address")
        user_menu.add_option("Edit First Name")
        user_menu.add_option("Edit Last Name")
        user_menu.add_option("Set Default Address")
        user_menu.add_option("Set Default Credit Card")
        user_menu.add_option("Previous Menu", 99)
        self.menus["user_menu"] = user_menu
        address_menu = IOMenu()
        address_menu.add_option("Edit Address Name")
        address_menu.add_option("Edit Address Line 1")
        address_menu.add_option("Edit Address Line 2")
        address_menu.add_option("Edit City")
        address_menu.add_option("Edit Country")
        address_menu.add_option("Edit Province/State")
        address_menu.add_option("Edit ZIP Code")
        address_menu.add_option("Edit Phone Number")
        address_menu.add_option("Previous Menu", 99)
        self.menus["address_menu"] = address_menu
        credit_card_menu = IOMenu()
        credit_card_menu.add_option("Edit Credit Card Name")
        credit_card_menu.add_option("Edit Credit Card Number")
        credit_card_menu.add_option("Edit Cardholder Name")
        credit_card_menu.add_option("Edit Expiration Month")
        credit_card_menu.add_option("Edit Expiration Year")
        credit_card_menu.add_option("Edit Security Code")
        credit_card_menu.add_option("Previous Menu", 99)
        self.menus["credit_card_menu"] = credit_card_menu
        bot_menu = IOMenu()
        bot_menu.add_option("Purchase Product")
        bot_menu.add_option("Log Out", 99)
        self.menus["bot_menu"] = bot_menu

    def _initialize_selection_menus(self):
        user_selection_menu = IOMenu()
        if self.data.user_count:
            for user in self.data.users:
                user_selection_menu.add_option(user)
        user_selection_menu.add_option("Add New User")
        user_selection_menu.add_option("Previous Menu",
                                       99 if self.data.user_count < 99
                                          else self.data.user_count + 100)
        self.menus["user_selection_menu"] = user_selection_menu
        address_selection_menu = IOMenu()
        if self.data.address_count:
            for address in self.data.addresses:
                address_selection_menu.add_option(address)
        address_selection_menu.add_option("Add New Address")
        address_selection_menu.add_option("Previous Menu",
                                          99 if self.data.user_count < 99
                                             else self.data.user_count + 100)
        self.menus["address_selection_menu"] = address_selection_menu
        cc_selection_menu = IOMenu()
        if self.data.credit_card_count:
            for cc in self.data.credit_cards:
                cc_selection_menu.add_option(cc)
        cc_selection_menu.add_option("Add New Credit Card")
        cc_selection_menu.add_option("Previous Menu",
                                     99 if self.data.credit_card_count < 99
                                        else self.data.credit_card_count + 100)
        self.menus["cc_selection_menu"] = cc_selection_menu

    def _update_selection_menu(self, menu_title, new_entry):
        if menu_title not in ["user_selection_menu", "address_selection_menu",
                              "cc_selection_menu"]:
            raise InvalidMenuError
        try:
            menu = self.menus[menu_title]
        except KeyError:
            raise InvalidMenuError
        obj = ""
        count = 0
        if menu_title == "user_selection_menu":
            obj = "User"
            count = self.data.user_count
        elif menu_title == "address_selection_menu":
            obj = "Address"
            count = self.data.address_count
        else:
            obj = "Credit Card"
            count = self.data.credit_card_count
        menu.remove_option("Add New {}".format(obj))
        menu.remove_option("Previous Menu")
        menu.add_option(new_entry)
        menu.add_option("Add New {}".format(obj))
        menu.add_option("Previous Menu", 99 if count < 99 else count + 100)

    def display_banner(self):
        print(b64decode(_b64_banner))

    def display_warning(self, warning):
        print(colorize("$[*]$ {}".format(warning),
                       TextFormats.RED + TextFormats.BOLD))

    def display_error(self, error):
        print(colorize("$[!]$ {}".format(error),
                       TextFormats.RED + TextFormats.BOLD))

    def display_processing(self, processing):
        print(colorize("$[-]$ {}".format(processing),
                       TextFormats.BLUE + TextFormats.BOLD))

    def display_success(self, success):
        print(colorize("$[*]$ {}".format(success),
                       TextFormats.GREEN + TextFormats.BOLD))

    def display_notice(self, notice):
        print(colorize("$[*]$ {}".format(notice),
                       TextFormats.YELLOW + TextFormats.BOLD))

    def display_menu(self, menu):
        print("\n{}\n".format(menu))

    def get_boolean_response(self, prompt):
        answer = "x"
        while answer.upper() not in ['Y', 'N', "YES", "NO"]:
            answer = raw_input(prompt + " ")
        return True if answer.upper() in ['Y', "YES"] else False

    def _input_digit(self):
        c = 'x'
        while not c.isdigit():
            if c == '\r':
                return ''
            c = getch()
        sys.stdout.write(c)
        sys.stdout.flush()
        return c

    def __input_digits(self, min_count=None, max_count=None):
        digits = ""

        if min_count == None and max_count == None:
            min_count = 0

        if max_count != None:
            for i in range(max_count):
                c = self._input_digit()
                if min_count != None:
                    if len(digits) >= min_count and not c:
                        break
                while not c:
                    c = self._input_digit()
                digits += c
        else:
            c = 'x'
            while c:
                c = self._input_digit()
                if len(digits) < min_count:
                    while not c:
                        c = self._input_digit()
                digits += c

        sys.stdout.write('\n')
        return digits

    def _input_digits(self, prompt, color=(TextFormats.CYAN
                                           + TextFormats.UNDERLINE),
                      min_count=None, max_count=None):
        sys.stdout.write(colorize("${}:$ ".format(prompt), color))
        sys.stdout.flush()
        return self.__input_digits(min_count, max_count)

    def _input_phone_number(self, prompt, color=(TextFormats.CYAN
                                                 + TextFormats.UNDERLINE)):
        formatter = AsYouTypeFormatter("US")
        c = 'x'
        print(colorize("${}:$".format(prompt), color))
        while not c.isdigit():
            c = getch()
        while c != '\r':
            while not c.isdigit() and c != '\r':
                c = getch()
            if c == '\r':
                break
            phone_number = formatter.input_digit(c)
            print(phone_number, end='\r')
            c = 'x'
        sys.stdout.write('\n')
        try:
            parse(phone_number, "US")
        except NumberParseException:
            phone_number = self._input_phone_number("Enter valid geographical"
                                                    + " phone number",
                                                    TextFormats.YELLOW)
        return phone_number

    def _validate_credit_card_number(self, number):
        # Luhn algorithm from Rosetta Code
        r = [int(c) for c in number][::-1]
        return (sum(r[0::2])
                + sum(sum(divmod(d * 2, 10)) for d in r[1::2])) % 10 == 0

    def _input_credit_card_number(self, prompt,
                                  color=(TextFormats.CYAN
                                         + TextFormats.UNDERLINE)):
        number = self._input_digits(prompt, color, min_count=12,
                                    max_count=19)
        if not self._validate_credit_card_number(number):
            number = self._input_digits("Enter a valid credit card number",
                                        TextFormats.YELLOW, 12, 19)
        return number

    def input_new_address(self):
        address1 = raw_input(colorize("$Address Line 1:$ ",
                                      TextFormats.CYAN
                                      + TextFormats.UNDERLINE))
        address2 = raw_input(colorize("$Address Line 2:$ ",
                                      TextFormats.CYAN
                                      + TextFormats.UNDERLINE))
        city = raw_input(colorize("$City:$ ",
                                  TextFormats.CYAN + TextFormats.UNDERLINE))
        country = raw_input(colorize("$Country:$ ",
                                     TextFormats.CYAN + TextFormats.UNDERLINE))
        province = raw_input(colorize("$Province/State:$ ",
                                      TextFormats.CYAN
                                      + TextFormats.UNDERLINE))
        zipcode = self._input_digits("ZIP Code", max_count=5) 
        phone = self._input_phone_number("Phone Number")
        address_name = ""
        if self.get_boolean_response(colorize("$Specify address name? (y/n)$",
                                              TextFormats.YELLOW)):
            address_name = raw_input(colorize("$Address Name:$ ",
                                              TextFormats.CYAN
                                              + TextFormats.UNDERLINE))
        print("")
        return self.data.add_address(address1, address2, city, country,
                                     province, zipcode, phone, address_name) 


    def input_new_credit_card(self):
        number = self._input_credit_card_number("Card Number")    
        name = raw_input(colorize("$Cardholder Name:$ ",
                                  TextFormats.CYAN + TextFormats.UNDERLINE))
        month = self._input_digits("Expiration Month (2 digits)", max_count=2)
        year = self._input_digits("Expiration Year (2 digits)", max_count=2)
        code = self._input_digits("Security Code (3 or 4 digits)", min_count=3,
                                  max_count=4)
        cc_name = ""
        if self.get_boolean_response(colorize("$Specify credit card name? "
                                              + "(y/n)$",
                                              TextFormats.YELLOW)):
            cc_name = raw_input(colorize("$Credit Card Name:$ ",
                                         TextFormats.CYAN
                                         + TextFormats.UNDERLINE))
        print("")
        return self.data.add_credit_card(number, name, month, year, code,
                                         cc_name)
         
    def input_new_user(self):
        email = raw_input(colorize("$Email Address:$ ",
                                   TextFormats.CYAN + TextFormats.UNDERLINE))
        while not validate_email(email):
            email = raw_input(colorize("$Enter a valid email address:$ ",
                                       TextFormats.YELLOW))
        first_name = raw_input(colorize("$First Name:$ ",
                                        TextFormats.CYAN
                                        + TextFormats.UNDERLINE))
        last_name = raw_input(colorize("$Last Name:$ ",
                                       TextFormats.CYAN
                                       + TextFormats.UNDERLINE))
        username = ""
        if self.get_boolean_response(colorize("$Specify username? (y/n)$",
                                              TextFormats.YELLOW)):
            username = raw_input(colorize("$Username:$ ",
                                          TextFormats.CYAN
                                          + TextFormats.UNDERLINE))
        print("") 
        default_address = ""
        if not self.data.address_count:
            default_address = self.input_new_address()
        else:
            sys.stdout.write(colorize("$Select Address:$", TextFormats.CYAN))
            default_address = self.handle_menu("address_selection_menu")
            if default_address == "Add New Address":
                default_address = self.input_new_address()
            elif default_address == "Previous Menu":
                default_address = self.menus["address_selection_menu"].options[0][1]
                self.display_notice("Default address set to {}".format(default_address))
        default_cc = ""
        if not self.data.credit_card_count:
            default_cc = self.input_new_credit_card()
        else:
            sys.stdout.write(colorize("$Select Credit Card:$",
                                      TextFormats.CYAN))
            default_cc = self.handle_menu("cc_selection_menu")
            if default_cc == "Add New Credit Card":
                default_cc = self.input_new_credit_card()
            elif default_cc == "Previous Menu":
                default_cc = self.menus["cc_selection_menu"].options[0][1]
                self.display_notice("Default credit card set to {}".format(default_cc))
        return self.data.add_user(email, first_name, last_name, username,
                                  default_address, default_cc)
 
    def read_cmd(self):
        return raw_input(self.prompt)

    def read_menu_option(self, menu, allow_exit=True):
        cmd = ""
        while (cmd not in [str(num) for num, opt in menu.options]
               and cmd != "exit"):
            cmd = self.read_cmd()
            if cmd == "exit":
                if not allow_exit:
                    continue
                if self.menus["main_menu"] == menu:
                    return menu.get_option_number("Exit")
                else:
                    return menu.get_option_number("Previous Menu")
        return int(cmd)

    def handle_menu(self, menu_title):
        self.previous_menu = self.current_menu
        self.current_menu = menu_title
        menu = self.menus[self.current_menu]
        self.display_menu(menu)
        number = self.read_menu_option(menu) 
        return menu.get_option_title(number) 

    def handle_user_menu(self, username):
        option = ""
        user = self.data.users[username]
        while option != "Previous Menu":
            sys.stdout.write('\n')
            print(colorize("${}$".format(username),
                           TextFormats.CYAN + TextFormats.BOLD))
            print(colorize("\t$Email:$ {}".format(user["email"]),
                           TextFormats.BLUE + TextFormats.UNDERLINE))
            print(colorize("\t$First Name:$ {}".format(user["first_name"]),
                           TextFormats.BLUE + TextFormats.UNDERLINE))
            print(colorize("\t$Last Name:$ {}".format(user["last_name"]),
                           TextFormats.BLUE + TextFormats.UNDERLINE))
            print(colorize("\t$Default Address:$ {}".format(user["default_address"]),
                           TextFormats.BLUE + TextFormats.UNDERLINE))
            print(colorize("\t$Default Credit Card:$ {}".format(user["default_credit_card"]),
                           TextFormats.BLUE + TextFormats.UNDERLINE))
            option = self.handle_menu("user_menu")
            if option == "Edit Username":
                new_username = raw_input(colorize("$New Username:$ ",
                                                  TextFormats.BLUE
                                                  + TextFormats.UNDERLINE))
                self.data.edit_user(username, new_username=new_username)
                self._initialize_selection_menus()
                username = new_username
            elif option == "Edit Email Address":
                new_email = raw_input(colorize("$New Email Address:$ ",
                                               TextFormats.BLUE
                                               + TextFormats.UNDERLINE))
                self.data.edit_user(username, email=new_email)
            elif option == "Edit First Name":
                new_first_name = raw_input(colorize("$New First Name:$ ",
                                                    TextFormats.BLUE
                                                    + TextFormats.UNDERLINE))
                self.data.edit_user(username, first_name=new_first_name)
            elif option == "Edit Last Name":
                new_last_name = raw_input(colorize("$New Last Name:$ ",
                                                   TextFormats.BLUE
                                                   + TextFormats.UNDERLINE))
                self.data.edit_user(username, last_name=new_last_name)
            elif option == "Set Default Address":
                new_default_address = self.handle_menu("address_selection_menu")
                if new_default_address == "Add New Address":
                    new_default_address = self.input_new_address()
                    self._update_selection_menu("address_selection_menu",
                                                new_default_address)
                if new_default_address != "Previous Menu":
                    self.data.edit_user(username,
                                        default_address=new_default_address)
            elif option == "Set Default Credit Card":
                new_default_cc = self.handle_menu("cc_selection_menu")
                if new_default_cc == "Add New Credit Card":
                    new_default_cc = self.input_new_credit_card()
                    self._update_selection_menu("cc_selection_menu",
                                                new_default_cc)
                if new_default_cc != "Previous Menu":
                    self.data.edit_user(username,
                                        default_credit_card=new_default_cc)
        self.data.save_data()

    def handle_user_selection_menu(self):
        option = ""
        while option != "Previous Menu":
            option = self.handle_menu("user_selection_menu")
            if option == "Add New User":
                option = self.input_new_user()
                self._update_selection_menu("user_selection_menu", option) 
            elif option != "Previous Menu":
                self.handle_user_menu(option)

    def handle_address_menu(self, address_name):
        option = ""
        address = self.data.addresses[address_name]
        while option != "Previous Menu":
            sys.stdout.write('\n')
            print(colorize("${}$".format(address_name),
                           TextFormats.CYAN + TextFormats.BOLD))
            print(colorize("\t$Line 1:$ {}".format(address["address1"]),
                           TextFormats.BLUE + TextFormats.UNDERLINE))
            print(colorize("\t$Line 2:$ {}".format(address["address2"]),
                           TextFormats.BLUE + TextFormats.UNDERLINE))
            print(colorize("\t$City:$ {}".format(address["city"]),
                           TextFormats.BLUE + TextFormats.UNDERLINE))
            print(colorize("\t$Country:$ {}".format(address["country"]),
                           TextFormats.BLUE + TextFormats.UNDERLINE))
            print(colorize("\t$Province/State:$ {}".format(address["province"]),
                           TextFormats.BLUE + TextFormats.UNDERLINE))
            print(colorize("\t$ZIP Code:$ {}".format(address["zipcode"]),
                           TextFormats.BLUE + TextFormats.UNDERLINE))
            print(colorize("\t$Phone Number:$ {}".format(address["phone"]),
                           TextFormats.BLUE + TextFormats.UNDERLINE))
            option = self.handle_menu("address_menu")
            if option == "Edit Address Name":
                new_address_name = raw_input(colorize("$New Address Name:$ ",
                                                      TextFormats.BLUE
                                                      + TextFormats.UNDERLINE))
                self.data.edit_address(address_name,
                                       new_address_name=new_address_name)
                self._initialize_selection_menus()
                address_name = new_address_name
            elif option == "Edit Address Line 1":
                new_address1 = raw_input(colorize("$New Address Line 1:$ ",
                                                  TextFormats.BLUE
                                                  + TextFormats.UNDERLINE))
                self.data.edit_address(address_name, address1=new_address1)
            elif option == "Edit Address Line 2":
                new_address2 = raw_input(colorize("$New Address Line 2:$ ",
                                                  TextFormats.BLUE
                                                  + TextFormats.UNDERLINE))
                self.data.edit_address(address_name, address2=new_address2)
            elif option == "Edit City":
                new_city = raw_input(colorize("$New City:$ ",
                                              TextFormats.BLUE
                                              + TextFormats.UNDERLINE))
                self.data.edit_address(address_name, city=new_city)
            elif option == "Edit Country":
                new_country = raw_input(colorize("$New Country:$ ",
                                                 TextFormats.BLUE
                                                 + TextFormats.UNDERLINE))
                self.data.edit_address(address_name, country=new_country)
            elif option == "Edit Province/State":
                new_province = raw_input(colorize("$New Province/State:$ ",
                                                  TextFormats.BLUE
                                                  + TextFormats.UNDERLINE))
                self.data.edit_address(address_name, province=new_province)
            elif option == "Edit ZIP Code":
                new_zipcode = self._input_digits("New ZIP Code",
                                                 TextFormats.BLUE
                                                 + TextFormats.UNDERLINE,
                                                 max_count=5)
                self.data.edit_address(address_name, zipcode=new_zipcode)
            elif option == "Edit Phone Number":
                new_phone = self._input_phone_number("New Phone Number",
                                                     TextFormats.BLUE
                                                     + TextFormats.UNDERLINE)
                self.data.edit_address(address_name, phone=new_phone)
        self.data.save_data()


    def handle_address_selection_menu(self):
        option = ""
        while option != "Previous Menu":
            option = self.handle_menu("address_selection_menu")
            if option == "Add New Address":
                option = self.input_new_address()
                self._update_selection_menu("address_selection_menu", option)
            elif option != "Previous Menu":
                self.handle_address_menu(option)

    def handle_credit_card_menu(self, cc_name):
        option = ""
        cc = self.data.credit_cards[cc_name]
        while option != "Previous Menu":
            sys.stdout.write('\n')
            print(colorize("${}$".format(cc_name),
                           TextFormats.CYAN + TextFormats.BOLD))
            print(colorize("\t$Card Number:$ {}".format(cc["number"]),
                           TextFormats.BLUE + TextFormats.UNDERLINE))
            print(colorize("\t$Cardholder Name:$ {}".format(cc["name"]),
                           TextFormats.BLUE + TextFormats.UNDERLINE))
            print(colorize("\t$Expiration Date:$ {}/{}".format(cc["month"],
                                                               cc["year"]),
                           TextFormats.BLUE + TextFormats.UNDERLINE))
            print(colorize("\t$Security Code:$ {}".format(cc["code"]),
                           TextFormats.BLUE + TextFormats.UNDERLINE))
            option = self.handle_menu("credit_card_menu")
            if option == "Edit Credit Card Name":
                new_cc_name = raw_input(colorize("$New Credit Card Name:$ ",
                                                 TextFormats.BLUE
                                                 + TextFormats.UNDERLINE))
                self.data.edit_credit_card(cc_name, new_cc_name=new_cc_name)
                self._initialize_selection_menus()
                cc_name = new_cc_name
            elif option == "Edit Credit Card Number":
                new_number = self._input_credit_card_number("New Credit Card Number",
                                                            TextFormats.BLUE
                                                            +
                                                            TextFormats.UNDERLINE)
                self.data.edit_credit_card(cc_name, number=new_number)
            elif option == "Edit Cardholder Name":
                new_name = raw_input(colorize("$New Cardholder Name:$ ",
                                              TextFormats.BLUE
                                              + TextFormats.UNDERLINE))
                self.data.edit_credit_card(cc_name, name=new_name)
            elif option == "Edit Expiration Month":
                new_month = self._input_digits("New Expiration Month",
                                               TextFormats.BLUE
                                               + TextFormats.UNDERLINE,
                                               max_count=2)
                self.data.edit_credit_card(cc_name, month=new_month)
            elif option == "Edit Expiration Year":
                new_year = self._input_digits("New Expiration Year",
                                              TextFormats.BLUE
                                              + TextFormats.UNDERLINE,
                                              max_count=2)
                self.data.edit_credit_card(cc_name, year=new_year)
            elif option == "Edit Security Code":
                new_code = self._input_digits("New Security Code",
                                              TextFormats.BLUE
                                              + TextFormats.UNDERLINE,
                                              min_count=3, max_count=4)
                self.data.edit_credit_card(cc_name, code=new_code)
        self.data.save_data()

    def handle_credit_card_selection_menu(self):
        option = ""
        while option != "Previous Menu":
            option = self.handle_menu("cc_selection_menu")
            if option == "Add New Credit Card":
                option = self.input_new_credit_card()
                self._update_selection_menu("cc_selection_menu", option)
            elif option != "Previous Menu":
                self.handle_credit_card_menu(option)

    def handle_login(self):
        print(colorize("$Log in as:$", TextFormats.CYAN))
        username = self.handle_menu("user_selection_menu")
        if username == "Add New User":
            username = self.input_new_user()
        if username != "Previous Menu":
            user = self.data.users[username]
            address = self.data.addresses[user["default_address"]]
            credit_card = self.data.credit_cards[user["default_credit_card"]]
            self.bot = KithBot(user, address, credit_card)
            old_prompt = self.prompt
            self.prompt = colorize("${}@BOT$ > ".format(username),
                                   TextFormats.BLUE + TextFormats.UNDERLINE)
            option = ""
            while option != "Log Out":
                option = self.handle_menu("bot_menu")
                if option == "Purchase Product":
                    self.display_warning("This functionality is in debug "
                                         + "phase. It will not complete the "
                                         + "checkout process and purchase "
                                         + "the item.")
                    product_url = raw_input(colorize("$Product URL:$ ",
                                                     TextFormats.CYAN
                                                     + TextFormats.UNDERLINE))
                    variant = raw_input(colorize("$Variant/Size "
                                                 + "(blank for first "
                                                 + "available variant):$ ",
                                                 TextFormats.CYAN
                                                 + TextFormats.UNDERLINE))
                    start = time()
                    try:
                        if variant:
                            self.bot.cop(product_url, variant)
                        else:
                            self.bot.cop_first_available_variant(product_url)
                    except SoldOutError:
                        print(colorize("\n$OUT OF STOCK$",
                                       TextFormats.RED + TextFormats.BOLD))
                        continue
                    end = time()
                    print("[DEBUG]: {} seconds to proceed to payment method".format(end - start))
            self.bot.close()
            self.bot = None
            self.prompt = old_prompt

    def handle_main_menu(self):
        option = ""
        while option != "Exit":
            option = self.handle_menu("main_menu")
            if option == "Users":
                self.handle_user_selection_menu()
            elif option == "Addresses":
                self.handle_address_selection_menu()
            elif option == "Credit Cards":
                self.handle_credit_card_selection_menu()
            elif option == "Log In":
                self.handle_login()

    def begin_session(self):
        self._initialize_menus()
        self.display_banner() 
        no_data = False
        try:
            self.data.load_data()
        except NoDataError:
            no_data = True
        else:
            self._initialize_selection_menus()
            if not self.data.user_count:
                no_data = True
        if no_data:
            self.display_notice("No users found")
            print(colorize("$Add new user:$", TextFormats.YELLOW))
            user = self.input_new_user()
            self.data.save_data()
            self._initialize_selection_menus()
        self.handle_main_menu()

if __name__ == "__main__":
    io = IOController()
    io.begin_session()
