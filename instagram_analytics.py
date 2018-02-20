"""
Module Main user interface
"""

from typing import Union, List
from ig_access import IGAccess, IGAccessException


class InstagramAnalytics:
    """
    Class to handle user interactions with bot

    Attributes:
        access - IGAccess object used to gather data
    """
    chromedriver_location: str
    quiet: bool

    def __init__(self, chromedriver_location: str='', quiet: bool=False) -> None:
        """
        Initialize a new Instagram Analytics object.

        Create a new IGAccess object using chromedriver_location and whether or not to print out progress
        """
        self.access = IGAccess(chromedriver_location, not quiet)

    def run(self, username: str, password: str, accounts: Union[List, str]) -> None:
        """
        Login using username and password, and gather and output data for each account in accounts
        """
        if isinstance(accounts, str):
            accounts = list(accounts)

        if not self.access.is_account(username):
            raise IGAccessException('%s isn\'t a username on Instagram' % username)

        self.access.login(username, password)

        for account in accounts:
            account = account.strip()
            if not self.access.is_account(account):
                raise IGAccessException('%s isn\'t an account on Instagram' % account)

            if not self.access.is_private(account):
                raise IGAccessException('%s isn\'t a public Instagram account' % account)

            # Get data
            self.access.collect_posts_data(account)
            self.access.collect_follow_data(account)
            self.access.collect_follow_diff()

        # Output and finish
        self.access.output_data()
        self.access.logout(username)
        self.access.tear_down()


if __name__ == '__main__':
    import configparser

    # Initialising the parser
    cparser = configparser.ConfigParser()
    cparser.read('userconfig.ini')
    cparser.optionxform = str

    user = cparser.get('USER', 'username')
    passw = cparser.get('USER', 'password')
    cloc = cparser.get('CHROMEDRIVER', 'driver_location')
    accs = cparser.get('ACCOUNTS', 'accounts')
    quiet = cparser.get('SETTINGS', 'quiet')

    if cloc == 'ENTER_CHROMEDRIVER_LOCATION':
        cloc = ''

    if quiet == 'False':
        quiet = False
    elif quiet == 'True':
        quiet = True

    ia = InstagramAnalytics(cloc, quiet)
    ia.run(user, passw, accs.split(','))
