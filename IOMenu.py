from IOFormat import TextFormats, colorize

class IOMenu:
    def __init__(self):
        self.options = []
        self.option_count = 0

    def add_option(self, option, number=None):
        self.option_count += 1
        if number == None:
            number = self.option_count
        self.options.append((number, option))

    def remove_option(self, option):
        self.options.remove((self.get_option_number(option), option))
        self.option_count -= 1

    def get_option_title(self, number):
        for option in self.options:
            if option[0] == number:
                return option[1]

    def get_option_number(self, title):
        for option in self.options:
            if option[1] == title:
                return option[0]

    def __str__(self):
        menu = ""
        for option in self.options:
            menu += colorize("$[{:<2}]$ {}\n".format(option[0], option[1]),
                             TextFormats.CYAN + TextFormats.BOLD)
        return menu

