# Standard Library
import re
import os
import random
from multiprocessing.dummy import Pool as ThreadPool

# Third Party
import requests
from yaml import load, Loader
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait

# Local Modules
from git_pull.exceptions import DeniedRequest

PATH_TO_RESOURCES = os.path.abspath("resources")

CHROME_OPTIONS = Options()
# CHROME_OPTIONS.add_argument("--disable-extensions")
# CHROME_OPTIONS.add_argument("--disable-gpu")
# CHROME_OPTIONS.add_argument("--no-sandbox") # Linux only
CHROME_OPTIONS.add_argument("--headless")

LANGUAGES = load(
    open(os.path.join(PATH_TO_RESOURCES, "languages.yml"), "r"),
    Loader=Loader
).items()
VENDOR_PATTERNS = load(
    open(os.path.join(PATH_TO_RESOURCES, "vendor.yml"), "r"),
    Loader=Loader
)
DOC_PATTERNS = load(
    open(os.path.join(PATH_TO_RESOURCES, "documentation.yml"), "r"),
    Loader=Loader
)["Files"]
USER_AGENTS = list(load(
    open(os.path.join(PATH_TO_RESOURCES, "useragents.yml"), "r"),
    Loader=Loader
))


def get_parse_tree(url):
    response = requests.get(url, headers={"User-Agent": random.choice(USER_AGENTS)})
    tree = BeautifulSoup(response.text, "lxml")

    # Checks if Github denied the request
    if any(h1.get_text() == "Whoa there!" for h1 in tree.find_all("h1")):
        raise DeniedRequest("Github denied your request for:", url)

    return tree


def get_dynamic_content(driver, xpath, delay=10):
    """
    Helper method for scraping dynamic content from a Selenium webdriver. It
    waits for a particular piece of content to load before scraping, and
    returns an empty list if it waits too long.

    Parameters
    ----------
    driver : ...
        Selenium webdriver instance with a webpage loaded on it
    xpath : ...
        XPATH specifying where to find the dynamic content
    delay : int
        how long (in seconds) to wait for the content to load before aborting

    Returns
    -------
    list of Selenium elements
    """

    try:
        return WebDriverWait(driver, delay).until(lambda d: d.find_elements_by_xpath(xpath))
    except TimeoutException:
        return []


def safe_scrape(func):
    """
    Decorator that wraps scraper functions in a try/except.
    """

    def wrapper(self):
        try:
            return func(self)
        except:
            return None

    return wrapper


# @safe_scrape
def scrape_personal_info(parse_tree, tag, id, callback=None):
    target = parse_tree.find(tag, id)
    if not callback:
        return target.text if target else "N/A"

    return callback(target)


def concurrent_exec(func, iterable, num_threads):
    """
    Executes a function on a list of inputs in parallel by dividing the work
    among multiple threads.

    Parameters
    ----------
    func : ...
        function to execute
    iterable : list
        list of arguments to map the function to
    num_threads : int
        number of threads to allocate

    Returns
    -------
    iterator of function outputs corresponding to each input
    """

    pool = ThreadPool(num_threads)
    map_of_items = pool.map(func, iterable)
    pool.close()
    pool.join()

    return map_of_items


def get_next_page_url(tree):
    buttons = tree.find_all("a", "btn btn-outline BtnGroup-item")
    for button in buttons:
        if button.get_text() == "Next":
            return button["href"]

    return ""


def fetch_repo_names(owner):
    def process_repo_list(tree):
        links = tree.find_all("div", "d-inline-block mb-1")
        for link in links:
            yield link.a.get_text().replace(' ', '').strip()

    # Loads the first page of repos
    url = f"https://github.com/{owner}?page=1&tab=repositories"
    tree = get_parse_tree(url)
    yield from process_repo_list(tree)

    if tree.find_all("div", "paginate-container"):
        while url := get_next_page_url(tree):
            tree = get_parse_tree(url)
            yield from process_repo_list(tree)


def identify_file_type(file_path):
    for language, attrs in LANGUAGES:
        if file_path.lower().endswith(tuple(attrs["extensions"])):
            return language

    for doc_pattern in DOC_PATTERNS:
        if re.search(doc_pattern, file_path):
            return "Documentation"

    return ""


def fetch_file_paths(repo_name, owner):
    # TODO: Find a way to force dynamic content to load without using Selenium

    # driver = webdriver.Remote(SERVICE.service_url, OPTIONS) # Linux only
    driver = webdriver.Chrome(
        executable_path=os.path.join(PATH_TO_RESOURCES, "chromedriver"),
        chrome_options=CHROME_OPTIONS
    ) # OS X only
    driver.get(f"https://github.com/{owner}/{repo_name}/find/master")

    files = get_dynamic_content(
        driver,
        '//span[@class="d-inline-block  js-tree-browser-result-path"]'
    )
    file_paths = []
    for path in files:
        path = path.text
        is_code = False

        for language, attrs in LANGUAGES:
            if path.lower().endswith(tuple(attrs["extensions"])):
                is_vendor_code = False

                for vendor_pattern in VENDOR_PATTERNS:
                    if re.search(vendor_pattern, path):
                        is_vendor_code = True
                        break

                if not is_vendor_code:
                    is_code = True
                    file_paths.append(path)
                    break

        if not is_code:
            for doc_pattern in DOC_PATTERNS:
                if re.search(doc_pattern, path):
                    file_paths.append(path)
                    break

    driver.close()

    return file_paths
