# git-pull

`git-pull` is a web scraper for Github. You can use it to scrape –– or, if you will, _pull_ –– data from a Github profile, repo, or file. It's parallelized and designed for anyone who wants to avoid using the Github API (e.g. due to the rate limit). Using it is very simple:

```python
from git_pull import GithubProfile

gh = GithubProfile("shobrook")
gh.scrape_follower_count()
>>> 168
```

Note that `git-pull` is _not_ a perfect replacement for the Github API. There's some data it can't scrape (yet).

## Installation

You can install `git-pull` with `pip`:

```bash
$ pip install git-pull
```

## Usage

`git-pull` provides three objects, `GithubProfile`, `Repo`, and `File`, each with methods for scraping particular data.

### `GithubProfile(username, num_threads=-1, scrape_everything=False)`

* `scrape_name()`
* `scrape_avatar()`
* `scrape_follower_count()`
* `scrape_contribution_graph()`
* `scrape_location()`
* `scrape_personal_site()`
* `scrape_workplace()`
* `scrape_repos(scrape_everything=False)`
* `scrape_repo(repo_name, scrape_everything=False)`

### `Repo(name, owner, num_threads=-1, scrape_everything=False)`

* `scrape_topics()`
* `scrape_star_count()`
* `scrape_fork_count()`
* `scrape_fork_status()`
* `scrape_files(scrape_everything=False)`
* `scrape_file(file_type, file_path, scrape_everything=False)`

### `File(path, type, owner, repo, scrape_everything=False)`

* `scrape_blames()`
