import copy
import os
import platform
import sys
from time import sleep

from selenium import webdriver


class Reader:
    css_selectors = {
        'chatlist': '[aria-label^="Chat"]',
    }

    MAX_WAITS = 30

    def __init__(self):
        self.driver = webdriver.Chrome(executable_path=self._driver_path())
        self.driver.get("https://web.whatsapp.com/")

        # Will hold contacts: [texts and media]
        self.chats = {}

        # Wait till we have logged in
        while True:
            try:
                e = self.driver.find_element_by_id('pane-side')
                a = self.driver.find_element_by_css_selector('[data-testid="alert-notification"]')
                if e is not None and a is not None:
                    sleep(1)
                    break
            except:
                pass

            sleep(1)

    def _driver_path(self):
        _platform = platform.platform().lower()
        _ostype = platform.system().lower()

        if _ostype == 'linux' or _ostype == 'windows':
            return 'drivers/%s/chromedriver' % _ostype
        elif _platform.startswith('macos'):
            return 'drivers/macos/chromedriver'
        else:
            print('Unsupported OS (%s/%s)' % (_platform, _ostype))
            sys.exit(-1)

    def _scroll(self, selector):
        p = self.driver.find_element_by_css_selector(selector)
        self.driver.execute_script(str.format("arguments[0].scrollTop = arguments[0].scrollTop + {}", p.size['height']), p)
        sleep(1)

    def _scroll_backwards(self, selector, limit_pages):
        waits = 0
        pages = 0
        while True:
            try:
                # Get the current text
                p0 = self.driver.find_element_by_css_selector(selector)
                _text = copy.copy(p0.text[:128])

                # If we are at the top of the chat, return
                if 'messages are end-to-end encrypted. no one outside of this chat, not even whatsapp, can read or listen to them. click to learn more' in _text.lower():
                    return

                # Scroll back
                self.driver.execute_script(str.format("p = document.querySelector('{}'); p.scrollIntoView();", selector))

                # Let it settle
                sleep(1)

                # TODO if stuck, i.e. too many times trying here w/same text, bail
                p1 = self.driver.find_element_by_css_selector(selector)
                if p1.text[:128] == _text:
                    # It is the same text, sleep a little, and continue
                    sleep(5)
                    if self.MAX_WAITS is not None:
                        waits += 1
                        if waits <= self.MAX_WAITS:
                            continue
                        else:
                            return
                else:
                    waits = 0

                pages += 1
                if limit_pages is not None and pages > limit_pages:
                    return
            except:
                print('Warning: problem scrolling backwards: %s' % sys.exc_info()[1])
                return

    def _scroll_to_top(self, element):
        try:
            self.driver.execute_script("arguments[0].scrollTop = 0", element)
            sleep(1)
        except:
            print(print('Warning: problem scrolling to top: %s' % sys.exc_info()[1]))
            return

    def _scan(self, limit_pages):
        # Get all top level list items in chats list (contacts)
        contacts_elements = self.driver.find_element_by_css_selector(self.css_selectors['chatlist']) \
            .find_elements_by_css_selector("div > div > div:nth-child(2) > div:nth-child(1) > div:nth-child(1) > span")

        contacts_elements.reverse()

        # TODO contact elements is returning mutiple inne elements whose leaf is our text of interest, need to grab jusp one

        names = []
        for e_idx in range(len(contacts_elements)):
            e = contacts_elements[e_idx]

            try:
                try:
                    cname = e.text.split('\n')[0]
                except:
                    cname = e.text
            except:
                print(print('Warning: problem reading contact name: %s' % sys.exc_info()[1]))

            try:
                if len(cname) == 0 or cname in self.chats:
                    continue

                # click it
                e.click()

                names.append(cname)

                # Scroll and grab texts
                # TODO grab img urls too
                selector = '.copyable-area > div > div[aria-label^="Message list"]'
                chat_body = self.driver.find_element_by_css_selector(selector)
                self._scroll_backwards(selector, limit_pages)

                self.chats[cname] = chat_body.text

                with open(os.path.join('data/', cname + ".json"), 'w') as f:
                    f.write(self.chats[cname])
            except:
                print(print('Warning: problem scanning chat of "%s": (%s)' % (cname, sys.exc_info()[1])))
                if cname in self.chats and len(self.chats[cname]) > 0:
                    with open(os.path.join('data/', cname + ".json"), 'w') as f:
                        f.write(self.chats[cname])
                        print('\t recovered %s lines.' % len(self.chats[cname]))
                else:
                    print('\t recovered no lines.')

        return names

    def _scan_names(self, limit_pages):
        names = set()
        while True:
            ns = self._scan(limit_pages)
            curlen = len(names)
            names.update(ns)
            if len(names) > curlen:
                self._scroll('#pane-side')
            else:
                break

        return list(names)

    def _parse_into_csv(self):
        # TODO make the jumble a readable thing
        pass

    def export(self, limit_pages=None):
        self._scroll_to_top(self.driver.find_element_by_id('pane-side'))
        self._scan_names(limit_pages)
        self._scroll_to_top(self.driver.find_element_by_id('pane-side'))

    def close(self):
        self.driver.close()


if __name__ == '__main__':
    r = Reader()
    r.export()
    r.close()
