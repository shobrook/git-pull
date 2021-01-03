# git-pull

**git-pull** is a web scraper for Github. You can use it to scrape –– or, if you will, _pull_ –– data from a Github profile, repo, or file. It's parallelized and designed for anyone who wants to avoid using the Github API (e.g. due to the rate limit). Using it is very simple:

```python
from git_pull import GithubProfile

gh = GithubProfile("shobrook")
gh.scrape_follower_count() # >>> 168
```

Note that **git-pull** is _not_ a perfect replacement for the Github API. There's some stuff that it can't scrape (yet), like a repo's commit history or release count.

## Installation

You can install **git-pull** with `pip`:

```bash
$ pip install git-pull
```

## Usage

**git-pull** provides three objects –– `GithubProfile`, `Repo`, and `File` –– each with methods for scraping data. Below are descriptions and usage examples for each object.

#### `GithubProfile(username, num_threads=multiprocessing.cpu_count(), scrape_everything=False)`

This is the master object for scraping data from a Github profile. All it requires is the username of the Github user, and from there you can scrape social info for that user and their repos.

**Parameters:**

* **`username` _(str)_:** Github username
* **`num_threads` _(int, optional (default=multiprocessing.cpu_count()))_:** Number of threads to allocate for splitting up scraping work; default is # of cores in your machine's CPU
* **`scrape_everything` _(bool, optional (default=False))_:** If `True`, does a "deep scrape" and scrapes all social info and repo data for the user (i.e. it calls all the scraper methods listed below and stores the results in properties of the object); if `False`, you have to call individual scraper methods to get the data you want

**Methods:**

* **`scrape_name() -> str`:** Returns the name of the Github user
* **`scrape_avatar() -> str`:** Returns a URL for the user's profile picture
* **`scrape_follower_count() -> int`:** Returns the number of followers the user has
* **`scrape_contribution_graph() -> dict`:** Returns the contribution history for the user as a map of dates (as strings) to commit counts
* **`scrape_location() -> str`:** Returns the user's location, if available
* **`scrape_personal_site() -> str`:** Returns the URL of the user's website, if available
* **`scrape_workplace() -> str`:** Returns the name of the user's workplace, if available
* **`scrape_repos(scrape_everything=False) -> list`:** Returns list of `Repo` objects for each of the user's repos (both source and forked); if `scrape_everything=True`, then a "deep scrape" is performed for each repo
* **`scrape_repo(repo_name, scrape_everything=False) -> Repo`:** Returns a single `Repo` object for a given repo that the user owns

**Example:**

```python
from git_pull import GithubProfile

# If scrape_everything=True, then all scraped data is stored in object
# properties
gh = GithubProfile("shobrook", scrape_everything=True)
gh.name # >>> "Jonathan Shobrook"
gh.avatar # >>> "https://avatars1.githubusercontent.com/u/18684735?s=460&u=60f797085eb69d8bba4aba80078ad29bce78551a&v=4"
gh.repos # >>> [Repo("git-pull"), Repo("saplings"), ...]

# If scrape_everything=False, individual scraper methods have to be called, each
# of which both returns the scraped data and stores it in the object properties
gh = GithubProfile("shobrook", scrape_everything=False)
gh.name # >>> ''
gh.scrape_name() # >>> "Jonathan Shobrook"
gh.name # >>> "Jonathan Shobrook"
```

#### `Repo(name, owner, num_threads=multiprocessing.cpu_count(), scrape_everything=False)`

Use this object for scraping data from a Github repo.

**Parameters:**

* **`name` _(str)_:** Name of the repo to be scraped
* **`owner` _(str)_:** Username of the owner of the repo
* **`num_threads` _(int, (optional, default=multiprocessing.cpu_count()))_:** Number of threads to allocate for splitting up scraping work; default is # of cores in your machine's CPU
* **`scrape_everything` _(bool, (optional, default=False))_:** If `True`, scrapes all metadata for the repo and scrapes files; if `False`, you have to call individual scraper methods to get the data you want

**Methods:**

* **`scrape_topics() -> list`:** Returns list of topics/tags for the repo
* **`scrape_star_count() -> int`:** Returns number of stars the repo has
* **`scrape_fork_count() -> int`:** Returns number of times the repo has been forked
* **`scrape_fork_status() -> bool`:** Returns whether or not the repo is a fork of another one
* **`scrape_files(scrape_everything=False) -> list`:** Returns a list of `File` objects, each representing a file in the repo; files that aren't programs or documentation files (e.g. boilerplate) are not scraped
* **`scrape_file(file_path, file_type=None, scrape_everything=False) -> File`:** Returns a `File` object given a file path

**Example:**

```python
from git_pull import Repo

repo = Repo("git-pull", "shobrook", scrape_everything=True)
repo.topics # >>> ["web-scraper", "github", "github-api", "parallel", "scraper"]
repo.fork_status # >>> False
```

#### `File(path, repo, owner, scrape_everything=False)`

Use this object for scraping data from a single file inside a Github repo.

**Parameters:**

* **`path` _(str)_:** Absolute path of the file inside the repo
* **`repo` _(str)_:** Name of the repo containing the file
* **`owner` _(str)_:** Username of the repo's owner
* **`scrape_everything` _(bool, (optional, default=False))_:** If `True`, scrapes the blame history for the file and the file type (i.e. calls the methods listed below)

**Methods:**

* **`scrape_blames() -> dict`:** Returns the blame history for a file as a map of usernames (i.e. contributors) to `{"line_nums": [1, 2, ...], "committers": [...]}` dictionaries, where `"line_nums"` is a list of line numbers the user wrote and `"committers"` is a list of usernames of contributors the user pair programmed with, if any

**Example:**

```python
from git_pull import File

file = File("git_pull/git_pull.py", "git-pull", "shobrook", scrape_everything=True)
file.blames # >>> {"shobrook": {"line_nums": [1, 2, ...], "committers": []}}
file.raw_url # >>> "https://raw.githubusercontent.com/shobrook/git-pull/master/git_pull/git_pull.py"
file.type # >>> "Python"
```
