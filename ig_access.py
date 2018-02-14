"""
Module for IG Access
"""
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from typing import List
import time


class IGAccess:
    """
    Represent an IG Access class

    === Attributes ===
    username      - user's username
    password      - user's password
    show_progress - whether or not to print progress to user
    driver        - selenium webdriver object
    followers     - list of followers
    following     - list of following
    data          - dictionary of collected data, keys:
                    > num_followers
                    > num_following
                    > followers
                    > following
                    > not_followed_back
                    > not_following_back
                    > following_verified
                    > followed_by_verified
                    > num_posts
                    > data_per_post - list of dictionaries for each post, keys:
                        > url
                        > likes
                        > liked_by
                        > comments
                    > total_likes
                    > avg_likes
    """
    username: str
    password: str
    show_progress: bool

    def __init__(self, username: str, password: str, show_progress: bool=False) -> None:
        """
        Initialize a new IG Check class
        """
        self.username, self.password, self.show_progress = username, password, show_progress
        self.data = {}
        self.driver = None

    def login(self, chromedriver_location: str) -> None:
        """
        Log into Instagram
        """
        if self.show_progress:
            print('Logging in')

        if chromedriver_location == 'ENTER_CHROMEDRIVER_LOCATION':  # User put chromedriver.exe into PATH.
            self.driver = webdriver.Chrome()
        else:
            self.driver = webdriver.Chrome(chromedriver_location)
        self.driver.get('https://www.instagram.com/accounts/login/')

        time.sleep(0.5)

        self.driver.find_element_by_name('username').send_keys(self.username)
        self.driver.find_element_by_name('password').send_keys(self.password)

        waiting_animation = ['\\', '|', '/', '-']

        # Prompt user to click 'Log in' button
        print('PROMPT: Click \'Log in\' -', end='')
        logged_in = False

        animation_index = 0
        # Loop until user clicks 'Log in'
        while not logged_in:
            try:
                self.driver.find_element_by_class_name('coreSpriteDesktopNavProfile')
                logged_in = True
                print('\rPROMPT: Click \'Log in :)\n')
            except NoSuchElementException:
                print('\rPROMPT: Click \'Log in\' %s' % waiting_animation[animation_index % 4], end='', flush=True)
                animation_index += 1
                time.sleep(1)

    def logout(self) -> None:
        """
        Logout of Instagram and exit
        """
        if self.show_progress:
            print('\nLogging out')

        # Go to user's profile and click logout
        self.driver.get('https://www.instagram.com/%s' % self.username)
        self.driver.find_element_by_class_name('coreSpriteMobileNavSettings').click()
        self.driver.find_element_by_xpath('/html/body/div[4]/div/div[2]/div/ul/li[4]').click()

        time.sleep(0.5)

        # Close browser
        self.driver.close()

    def collect_follow_data(self) -> None:
        """
        Collect data about user's followers and following
        """
        if self.show_progress:
            print('Getting user\'s followers')
        # Get list of user's followers
        self.driver.get('https://www.instagram.com/%s' % self.username)
        followers = self._get_followers()

        if self.show_progress:
            print('Getting user\'s following')
        # Get list of users user's following
        self.driver.get('https://www.instagram.com/%s' % self.username)
        following = self._get_following()

        # Add to self.data
        self.data['num_followers'] = len(followers)
        self.data['num_following'] = len(following)
        self.data['followers'] = followers
        self.data['following'] = following

    def collect_follow_diff(self) -> None:
        """
        Collect data list about the difference between user's followers and following and append it to self.data
        """
        if self.show_progress:
            print('Analysing follower/following data')

        followers = self.data['followers']
        following = self.data['following']

        not_followed_back = [user for user in following if user not in followers]
        not_following_back = [user for user in followers if user not in following]

        following_verified = [user for user in following if '(Verified)' in user]
        followed_by_verified = [user for user in followers if '(Verified)' in user]

        # Append gathered data into self.data
        self.data['not_followed_back'] = not_followed_back
        self.data['not_following_back'] = not_following_back
        self.data['following_verified'] = following_verified
        self.data['followed_by_verified'] = followed_by_verified

    def collect_likes_data(self) -> None:
        """
        Collect data on how many user's liked pictures
        """
        self.driver.get('https://www.instagram.com/%s' % self.username)

        if self.show_progress:
            print('Getting data per post')

        num_of_posts = int(self.driver.find_element_by_xpath(
            '//*[@id="react-root"]/section/main/article/header/section/ul/li[1]/span').text.split(' ')[0])

        if self.show_progress:
            print('Progress:')
            print('\t[' + (' ' * 40) + ']' + ' 0%', end='', flush=True)

        data_per_post = []
        for i in range(num_of_posts):
            row = i // 3 + 1
            img_index = i % 3 + 1

            img_xpath = '//*[@id="react-root"]/section/main/article/div[2]/div/div[%d]/div[%d]' % (row, img_index)

            try:
                img = self.driver.find_element_by_xpath(img_xpath)
            except NoSuchElementException:
                # implies no more images in this row
                continue

            # Hover over image and get likes/comments data
            ActionChains(self.driver).move_to_element(img).perform()
            snapshot_index = 2
            snapshot_data = self.driver.find_element_by_xpath(img_xpath + '/a/div[2]').text.split('\n')

            # If Post has multiple images, it's snapshot will be in a higher index
            while 'Post' in snapshot_data:
                snapshot_index += 1
                snapshot_data = \
                    self.driver.find_element_by_xpath(img_xpath + '/a/div[%d]' % snapshot_index).text.split('\n')

            likes = int(snapshot_data[0])
            comments = int(snapshot_data[2])

            img.click()

            time.sleep(1)

            users_who_liked = self._get_likes_from_post(i, num_of_posts, likes)

            post_data = {
                'url': self.driver.current_url,
                'likes': len(users_who_liked),
                'liked_by': users_who_liked,
                'comments': comments
            }

            data_per_post.append(post_data)

            # Close iframe
            self.driver.find_element_by_xpath('/html/body/div[4]/div/button').click()

        print(data_per_post)

        total_likes = sum([data['likes'] for data in data_per_post])
        avg_likes = len(data_per_post) / total_likes

        # Add collected data to self attribute
        self.data['data_per_post'] = data_per_post
        self.data['total_likes'] = total_likes
        self.data['avg_likes'] = avg_likes

    def output_data(self) -> None:
        """
        Output self.data to [USERNAME]_data.json
        Updates data if already present.
        """
        import json
        from json.decoder import JSONDecodeError

        if self.show_progress:
            print('\nWriting data to %s_data.json' % self.username)

        with open('%s_data.json' % self.username, 'w+') as f:
            try:
                data = json.load(f)
            except JSONDecodeError:  # file is empty
                data = {}

            for key in self.data:
                data[key] = self.data[key]

            json.dump(data, f, indent=4)

    # ===== PRIVATE HELPER METHODS =====

    def _get_followers(self) -> List[str]:
        """
        Return a list of user's followers
        """
        # Get number of followers and click followers link
        followers_link = self.driver.find_element_by_partial_link_text('followers')
        num_of_followers = int(followers_link.text.split(' ')[0])
        followers_link.click()

        time.sleep(1)

        return self._get_list_of_users(num_of_followers)

    def _get_following(self) -> List[str]:
        """
        Return a list of users user is following
        """
        # Get number of following and click following link
        following_link = self.driver.find_element_by_partial_link_text('following')
        num_following = int(following_link.text.split(' ')[0])
        following_link.click()

        time.sleep(1)

        return self._get_list_of_users(num_following)

    def _get_list_of_users(self, num_users: int) -> List[str]:
        """
        Return a list of users with len(num_users) from the current iframe window
        """
        # Find the current iframe
        dialog = self.driver.find_element_by_xpath('/html/body/div[4]/div/div[2]/div/div[2]')

        if self.show_progress:
            print('Progress:', flush=True)
            print('\t[' + (' ' * 40) + ']' + ' 0%', end='')

        # Keep scrolling down the iframe until all users are showing
        list_of_users = self._clean_list(self.driver.find_element_by_class_name('_b9n99').text)
        while len(list_of_users) < num_users:
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", dialog)
            list_of_users = self._clean_list(self.driver.find_element_by_class_name('_b9n99').text)

            if self.show_progress:
                percent_comp = len(list_of_users) / num_users
                fill_bar = round(40 * percent_comp)
                print('\r\t[' + ('#' * fill_bar) + (' ' * (40 - fill_bar)) + '] ' +
                      str(round(percent_comp * 100, 3)) + '%', end='', flush=True)

            time.sleep(0.5)

        print('\n')

        return list_of_users

    def _get_likes_from_post(self, i: int, num_of_posts: int, num_of_likes: int):
        """
        Get number of likes and user who likes post from current iframe
        """
        # Get the number of likes and click on the likes link
        like_obj = self.driver.find_element_by_xpath(
            '/html/body/div[4]/div/div[2]/div/article/div[2]/section[2]/div/a')
        like_obj.click()

        time.sleep(0.5)

        # Keep scrolling down the iframe until all users are showing
        dialog = self.driver.find_element_by_xpath('/html/body/div[4]/div/div[2]/div/article/div[2]/div[2]')
        list_of_users = self._clean_list(self.driver.find_element_by_class_name('_b9n99').text)
        update_delay = 0
        while len(list_of_users) < num_of_likes:
            last_count = len(list_of_users)  # Keep track of whether list was updated

            # Scroll and get updated list_of_users
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", dialog)
            list_of_users = self._clean_list(self.driver.find_element_by_class_name('_b9n99').text)

            if self.show_progress:
                percent_comp = i / num_of_posts
                percent_comp += (len(list_of_users) / num_of_likes) / num_of_posts
                fill_bar = round(40 * percent_comp)
                print('\r\t[' + ('#' * fill_bar) + (' ' * (40 - fill_bar)) + '] ' +
                      str(round(percent_comp * 100, 3)) + '%', end='', flush=True)

            time.sleep(0.5)

            if len(list_of_users) == last_count:
                update_delay += 0.5  # list hasn't been updated in ~ 0.5 seconds
            else:
                update_delay = 0

            if update_delay == 10:  # list hasn't been updated for > 10 seconds
                if not len(list_of_users) + 1 == num_of_likes:  # Sometimes the like count is off by 1
                    print('\nTIMEOUT ERROR: Page hasn\'t refreshed for 10 seconds, loop stopped at getting user'
                          ' %d of %d\n\tprogram will skip this post and move-on' % (last_count, num_of_likes))
                elif self.show_progress:
                    percent_comp = (i + 1) / num_of_posts
                    fill_bar = round(40 * percent_comp)
                    print('\r\t[' + ('#' * fill_bar) + (' ' * (40 - fill_bar)) + '] ' +
                          str(round(percent_comp * 100, 3)) + '%', end='', flush=True)
                break

        return list_of_users

    @staticmethod
    def _clean_list(raw_string: str) -> List[str]:
        """
        Returns a list of cleaned followers from list of followers and junk
        """
        return_list = []
        raw_list = raw_string.split('\n')

        # Loop through raw list of users and pick out users
        for i in range(len(raw_list)):
            # If the line is followed by a line containing Following or Follow, it's a username line
            if i == 0 or raw_list[i-1] in ['Following', 'Follow']:
                name = raw_list[i]
                # Add a (Verified) tag if the account is verified
                try:
                    if raw_list[i+1] == 'Verified':
                        name += ' (Verified)'
                except IndexError:  # Internet is slow and page isn't loading fully
                    pass
                return_list.append(name)

        return return_list

if __name__ == '__main__':
    import configparser

    parser = configparser.ConfigParser()
    parser.read('userconfig.ini')
    parser.optionxform = str

    username = parser.get('USER', 'username')
    password = parser.get('USER', 'password')
    chromedriver_location = parser.get('CHROMEDRIVER', 'driver_location')

    iga = IGAccess(username, password, True)

    iga.login(chromedriver_location)

    # iga.collect_follow_data()
    #
    # iga.collect_follow_diff()
    # data = iga.data
    #
    # print('\n%d people don\'t follow you back:' % len(data['not_followed_back']))
    # for user in data['not_followed_back']:
    #     print('\t%s' % user)
    #
    # print('\nYou don\'t follow %d back:' % len(data['not_following_back']))
    # for user in data['not_following_back']:
    #     print('\t%s' % user)
    #
    # print('\n You follow %d Verified users:' % len(data['following_verified']))
    # for user in data['following_verified']:
    #     print('\t%s' % user)
    #
    # print('\n%d Verified users follow you:' % len(data['followed_by_verified']))
    # for user in data['followed_by_verified']:
    #     print('\t%s' % user)

    iga.collect_likes_data()

    iga.output_data()

    time.sleep(5)
    iga.logout()
