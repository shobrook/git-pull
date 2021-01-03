# Standard Library
import urllib.parse
from collections import defaultdict
from datetime import datetime
from functools import partial
from multiprocessing import cpu_count

# Local Modules
import git_pull.utilities as utils
from git_pull.exceptions import InvalidUsernameError


class File(object):
    def __init__(self, path, repo, owner, scrape_everything=False):
        self.path = path
        self.type = utils.identify_file_type(path)
        self.repo, self.owner = repo, owner
        self.raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/master/{urllib.parse.quote(path.encode('utf-8'))}"
        self.blames = {}

        if scrape_everything:
            self.blames = self.scrape_blames()

    def scrape_blames(self):
        url = f"https://github.com/{self.owner}/{self.repo}/blame/master/{self.path}"
        tree = utils.get_parse_tree(url)

        author_to_line_nums = defaultdict(lambda: {"line_nums": set(), "committers": set()})
        for section in tree.find_all("div", "blame-hunk d-flex border-gray-light border-bottom"): # Commit blocks
            line_nums = [int(ln.get_text()) for ln in section.find_all("div", "blob-num blame-blob-num bg-gray-light js-line-number")]
            author_label = section.find("div", "AvatarStack-body")["aria-label"]

            split_author_label = author_label.split(" and ")
            if len(split_author_label) > 1: # Duet commit (pair programmers)
                author = split_author_label[0]
                committer = split_author_label[1].split(" (non-author committer)")[0]

                author_to_line_nums[author]["committers"].add(committer)
                author_to_line_nums[author]["line_nums"] |= set(line_nums)
            else: # Solo commit
                author_to_line_nums[author_label]["line_nums"] |= set(line_nums)

        self.blames = dict(author_to_line_nums)
        return self.blames

    def to_dict(self):
        return {
            "path": self.path,
            "type": self.type,
            # "owner": self.owner,
            # "repo": self.repo,
            "raw_url": self.raw_url,
            "blames": self.blames
        }


class Repo(object):
    def __init__(self, name, owner, num_threads=cpu_count(), scrape_everything=False):
        self.name, self.owner = name, owner
        self._threads = num_threads
        self._tree = utils.get_parse_tree(f"https://github.com/{owner}/{name}")

        self.files = set()
        self.topics = None
        self.star_count = None
        self.fork_count = None
        self.fork_status = None

        if scrape_everything:
            self.scrape_files(scrape_everything)
            self.scrape_topics()
            self.scrape_star_count()
            self.scrape_fork_count()
            self.scrape_fork_status()

    def scrape_files(self, scrape_everything=False):
        if self._threads > 0:
            files = utils.concurrent_exec(
                partial(self.scrape_file, scrape_everything=scrape_everything),
                utils.fetch_file_paths(self.name, self.owner),
                self._threads
            )
            self.files |= set(files)
        else:
            for file_path in utils.fetch_file_paths(self.name, self.owner):
                file = self.scrape_file(file_path, scrape_everything)
                self.files.add(file)

        return self.files

    def scrape_file(self, file_path, scrape_everything=False):
        return File(
            file_path,
            self.name,
            self.owner,
            scrape_everything
        )

    # @utils.safe_scrape
    # def scrape_maintenance_data(self):
    #     base_url = f"https://github.com/{self.owner}/{self.name}"
    #
    #     def get_count_container(extension, to_remove):
    #         tree = get_parse_tree(f"{base_url}/{extension})
    #         count = tree.find('a', class_="btn-link selected")
    #
    #         if not count:
    #             return 0
    #
    #         return int(count.get_text().strip().replace(to_remove, '').replace(',', ''))
    #
    #     self.open_issues = get_count_container("issues?q=is%3Aopen+is%3Aissue", " Open")
    #     self.closed_issues = get_count_container("issues?q=is%3Aissue+is%3Aclosed", " Closed")
    #
    #     self.open_pulls = get_count_container("pulls?q=is%3Aopen+is%3Apr", " Open")
    #     self.closed_pulls = get_count_container("pulls?q=is%3Apr+is%3Aclosed", " Closed")

    @utils.safe_scrape
    def scrape_topics(self):
        containers = self._tree.find_all('a', "topic-tag topic-tag-link")
        self.topics = [tag.get_text().replace(' ', '').strip() for tag in containers]

        return self.topics

    @utils.safe_scrape
    def scrape_star_count(self):
        star_container = self._tree.find('a', "social-count js-social-count")
        self.star_count = int(star_container["aria-label"].split(" ")[0])

        return self.star_count

    @utils.safe_scrape
    def scrape_fork_count(self):
        fork_container = self._tree.find_all('a', "social-count")[2] # [-1]?
        self.fork_count = int(fork_container.get_text().replace(',', ''))

        return self.fork_count

    @utils.safe_scrape
    def scrape_fork_status(self):
        fork_icon = self._tree.find("svg", "octicon octicon-repo-forked text-gray mr-2")
        self.fork_status = bool(fork_icon)

        return self.fork_status

    def to_dict(self):
        return {
            "name": self.name,
            "owner": self.owner,
            "files": [file.to_dict() for file in self.files],
            "topics": self.topics,
            "star_count": self.star_count,
            "fork_count": self.fork_count,
            "fork_status": self.fork_status
            # "open_issues": self.open_issues,
            # "closed_issues": self.closed_issues,
            # "open_pulls": self.open_pulls,
            # "closed_pulls": self.closed_pulls
        }


class GithubProfile(object):
    def __init__(self, username, num_threads=cpu_count(), scrape_everything=False):
        self.username = username
        self._threads = num_threads
        self._tree = utils.get_parse_tree(f"https://github.com/{username}")

        if not self._tree.find_all("div", "js-yearly-contributions"):
            raise InvalidUsernameError(username)

        self.name = ''
        self.avatar = ''
        self.follower_count = ''
        self.contribution_graph = dict()
        self.location = ''
        self.personal_site = ''
        self.workplace = ''
        self.repos = set()

        if scrape_everything:
            self.scrape_name()
            self.scrape_avatar()
            self.scrape_follower_count()
            self.scrape_contribution_graph()
            self.scrape_location()
            self.scrape_personal_site()
            self.scrape_workplace()
            self.scrape_repos(scrape_everything)

    ## Social Info ##

    def scrape_name(self):
        self.name = utils.scrape_personal_info(
            parse_tree=self._tree,
            tag="span",
            id="p-name vcard-fullname d-block overflow-hidden"
        )
        return self.name

    def scrape_avatar(self):
        self.avatar_url = utils.scrape_personal_info(
            parse_tree=self._tree,
            tag="img",
            id="avatar avatar-user width-full border bg-white",
            callback=lambda t: t["src"]
        )
        return self.avatar_url

    def scrape_follower_count(self):
        link_element = self._tree.find("a", "link-gray no-underline no-wrap")
        self.follower_count = int(link_element.find("span", "text-bold text-gray-dark").get_text())
        return self.follower_count

    def scrape_contribution_graph(self):
        get_map = lambda parse_tree: {
            tile["data-date"]: int(tile["data-count"])
        for tile in parse_tree.find_all("rect", "day")}

        graph = get_map(self._tree)
        for link in self._tree.find_all('a', "js-year-link filter-item px-3 mb-2 py-2"):
            url = f"https://github.com{link['href']}"
            commit_overview = utils.get_parse_tree(url)
            graph = {**graph, **get_map(commit_overview)}

        self.contribution_graph = dict(sorted(
            graph.items(),
            key=lambda c: datetime.strptime(c[0], "%Y-%m-%d")
        ))
        return self.contribution_graph

    def scrape_location(self):
        self.location = utils.scrape_personal_info(self._tree, "span", "p-label")
        return self.location

    def scrape_personal_site(self):
        list_element = self._tree.find("li", attrs={"data-test-selector": "profile-website-url"})
        if list_element:
            link_element = list_element.find("a")
            self.personal_site = link_element["href"]

        return self.personal_site

    def scrape_workplace(self):
        self.workplace = utils.scrape_personal_info(self._tree, "span", "p-org")
        return self.workplace

    ## Repos ##

    def scrape_repos(self, scrape_everything=False):
        for repo_name in utils.fetch_repo_names(self.username):
            repo = GithubProfile.scrape_repo(repo_name, scrape_everything)
            self.repos.add(repo)

        return self.repos

    def scrape_repo(self, repo_name, scrape_everything=False):
        return Repo(repo_name, self.username, self._threads, scrape_everything)

    ## Misc. ##

    def to_dict(self):
        return {
            "name": self.name,
            "avatar_url": self.avatar_url,
            "follower_count": self.follower_count,
            "contribution_graph": self.contribution_graph,
            "location": self.location,
            "personal_site": self.personal_site,
            "workplace": self.workplace,
            "repos": [repo.to_dict() for repo in self.repos]
        }
