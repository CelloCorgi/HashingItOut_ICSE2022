# Using PyGitHub (https://pygithub.readthedocs.io/en/latest/introduction.html) - pip install PyGithub
from github import Github, GithubException
from time import time, sleep
# This is a local python file
import search_terms as st
import csv

def make_github_connection():
    with open("/Users/madelineendres/bin/gitAccessToken", 'r') as f:
        gitToken = f.read()[:-1]
    return Github(gitToken)

def time_wait(gh):
    # This makes sure I don't go over GitHub REST API's rate limit
    remaining_q = gh.rate_limiting[0]
    time_left = gh.rate_limiting_resettime - int(time())
    print(remaining_q, time_left)
    if time_left <=0: return 5
    if remaining_q <= 10: return time_left + 5
    return time_left / remaining_q

def add_users(gh, language_name, writer):
    sleep(time_wait(gh))
    users = gh.search_users(query='language:{}'.format(language_name))
    for user in users:
        if user.email is None: continue
        print(user, user.email)
        writer.writerow({
            'username': user.login,
            'email': user.email,
            'location': user.location,
            'search_language': language_name,
            'public_repos': user.public_repos,
            'bio': user.bio,
            'company': user.company,
            'contributions': user.contributions,
            'followers': user.followers,
            'name': user.name})
        sleep(time_wait(gh))

def get_repos(gh, language_name, writer):
    sleep(time_wait(gh))
    repos = gh.search_repositories(query='stars:>=25 language:{}'.format(language_name), sort='stars')

    # Take the top 100 repos from each?
    counter = 0
    for repo in repos:
        print(repo.name)
        if counter == 100: break
        sleep(time_wait(gh))
        try:
            users = repo.get_contributors()
            counter += 1
            counter2 = 0
            for user in users:
                if counter2 == 25: break
                print(user, user.email, repo.name, counter, counter2, flush=True)
                counter2 += 1
                sleep(time_wait(gh))
                if user.email is None: continue
                writer.writerow({
                    'username': user.login,
                    'email': user.email,
                    'location': user.location,
                    'search_language': language_name,
                    'public_repos': user.public_repos,
                    'bio': user.bio,
                    'company': user.company,
                    'contributions': user.contributions,
                    'followers': user.followers,
                    'name': user.name,
                    'url': repo.url})
        except Exception:
            print("Unable to process {} because too many contributors".format(repo.url))


if __name__ == "__main__":
    gh = make_github_connection()
    print("GitHub Rate Limit: {}".format(gh.get_rate_limit()))
    
    # Get the developer profiles from each of the top languages
    with open('github_devs_topLanguages.csv', 'w', newline='') as csvfile1:
        header = ['username', 'email', 
                'location', 'search_language', 
                'public_repos', 'bio', 
                'company', 'contributions', 
                'followers', 'name']
        writer1 = csv.DictWriter(csvfile1, fieldnames=header)
        writer1.writeheader()
        for language in st.popular_langs + st.other_langs:
            add_users(gh, language, writer1)

    # And also go through the top 100 projects for each language, and get the top 25 developer profiles from each one
    # Note: This does not work for the linux kernel because there are too many developers
    with open('github_topProjectsee.csv', 'a', newline='') as csvfile2:
        header = ['username', 'email', 
                'location', 'search_language', 
                'public_repos', 'bio', 
                'company', 'contributions', 
                'followers', 'name', 'url']
        writer2 = csv.DictWriter(csvfile2, fieldnames=header)
        writer2.writeheader()
        for language in st.popular_langs + st.other_langs:
            get_repos(gh, language, writer2)