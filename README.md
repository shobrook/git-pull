# git-pull

`git-pull` is a web scraper for Github. You can use it to scrape –– or, if you will, _pull_ –– data from a Github profile, repo, or file. It's parallelized and designed for anyone who wants to avoid using the Github API (e.g. due to the rate limit). Using it is very simple:

```python
from git_pull import GithubProfile

gh = GithubProfile("shobrook")
gh.scrape_follower_count()
>>> 168
```

Note that `git-pull` is _not_ a perfect replacement for the Github API. There's some stuff, like a repo's commit history or # of releases, that it can't scrape (yet).

## Installation

You can install `git-pull` with `pip`:

```bash
$ pip install git-pull
```

## Usage

`git-pull` provides three objects –– `GithubProfile`, `Repo`, and `File` –– each with methods for scraping data. Below are descriptions and usage examples for each object.

### `GithubProfile(username, num_threads=-1, scrape_everything=False)`

This is the master object for scraping data from a Github profile. All it requires is the username of the Github user, and from there you can scrape social info for that user and their repos. It has the following parameters:

* `username` _(str)_: Github user's username/handle
* `num_threads` _(int, optional (default=-1))_: Number of threads to allocate for splitting up the work for scraping files in repos; if `-1`, multithreading is disabled
* `scrape_everything` _(bool, optional (default=False))_: If `True`, scrapes all social info and repo data for the user (i.e. it calls all of the scraper methods listed below and stores their results in properties of the model); if `False`, you have to call individual scraper methods to get the data you want

Once the object is initialized, you can call individual scraper methods to get the data you want:

* `scrape_name()`: Returns the name of the Github user
* `scrape_avatar()`: Returns a URL for the user's profile picture
* `scrape_follower_count()`: Returns the number of followers the user has
* `scrape_contribution_graph()`: Returns the contribution history for the user, formatted as a map of dates (as strings) to number of commits
* `scrape_location()`: Returns the user's location, if provided
* `scrape_personal_site()`: Returns the URL to the user's website, if provided
* `scrape_workplace()`: Returns the name of the user's workplace, if provided
* `scrape_repos(scrape_everything=False)`: Returns a list of `Repo` objects for each of the user's repos (both source and forked); if `scrape_everything=True`, then the
* `scrape_repo(repo_name, scrape_everything=False)`: Returns a single `Repo` object for a given repo that the user owns

Here's an example:

```python
from git_pull import GithubProfile

# If scrape_everything=True, then all scraped data is stored in the object
# properties
gh = GithubProfile("shobrook", scrape_everything=True)
gh.name
>>> "Jonathan Shobrook"
gh.avatar
>>> "https://avatars1.githubusercontent.com/u/18684735?s=460&u=60f797085eb69d8bba4aba80078ad29bce78551a&v=4"
gh.repos
>>> [Repo("git-pull"), Repo("saplings"), ...]

# If scrape_everything=False, individual scraper methods have to be called
# before accessing data from the properties
gh = GithubProfile("shobrook", scrape_everything=False)
gh.name
>>> ''
gh.scrape_name()
gh.name
>>> "Jonathan Shobrook"
```

### `Repo(name, owner, num_threads=-1, scrape_everything=False)`

Use this object for scraping data from a Github repo. It have the following parameters:

* `name` _(str)_: Name of the repo to be scraped
* `owner` _(str)_: Username of the owner of the repo
* `num_threads` _(int, (optional, default=-1))_: Number of threads to allocate for splitting up the work for scraping files; if `-1`, multithreading is disabled
* `scrape_everything` _(bool, (optional, default=False))_: If `True`, scrapes all metadata for the repo and scrapes files; if `False`, you have to call individual scraper methods to get the data you want

Once the object is initialized, you can call individual scraper methods to get the data you want:

* `scrape_topics()`: Returns list of topics/tags for the repo
* `scrape_star_count()`: Returns number of stars the repo has
* `scrape_fork_count()`: Returns number of times the repo has been forked
* `scrape_fork_status()`: Returns whether or not the repo is a fork of another one
* `scrape_files(scrape_everything=False)`: Returns a list of `File` objects, each representing a relevant file in the repo; files that aren't language or documentation files (e.g. boilerplate files) are not scraped
* `scrape_file(file_type, file_path, scrape_everything=False)`: Returns a `File` object given a file path

An example:

```python
# TODO
```

### `File(path, type, owner, repo, scrape_everything=False)`

TODO

* `scrape_blames()`
