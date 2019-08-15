# KithBot

Old prototype Shopify bot I wrote a while back. Only designed to work for
https://kith.com, though it could easily be modified to work on other Shopify
sites. It does not complete the purchasing process, and terminates before
submitting payment information and encountering the ReCAPTCHA that most sites
implement. The bot also does not have any search functionality; it simply takes
a Kith product URL and completes the checkout process up to the point of payment
submission.

This bot was meant to be a prototype for a larger, faster, fully functional bot
written in a lower level language and controlled by a GUI. While the bot
contains the core checkout functionality of any retail bot, it does not contain
many key features of commercial bots, and its speed is insufficient for
release-time, which is largely due to Python's own performance limitations.

Still, this rudimentary, incomplete bot provides an interesting look at retail
bot functionality, and exposes the core functionality of Shopify bots in
particular.

## Requirements

The following Python packages are required, and the versions last tested are
listed:
```
validate-email==1.3
phonenumbers==8.9.16
requests==2.20.0
python-dateutil==2.7.3
```
requests and dateutil are the most important packages; the remaining two are
merely used for user input validation, which could be commented out without
affecting the rest of the functionality to any significant degree.

## Running

The launch file is IOController.py. On any UNIX based system, you should be able
to make this file executable by running `chmod u+x ./IOController.py` in the
project root directory, which will allow you to run the bot with
`./IOController.py`. Otherwise, you can just run this file with your Python
interpreter to start the bot.

IOController has a colored, menu-based command line interface. The program
hasn't been tested on Windows, and the control characters used for the colors
and other text formats might cause unexpected behavior in a Windows prompt. Once
the IOController program is started, the process of running the bot should be
self-explanatory from the prompts and menus.
