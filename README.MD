# gitlab-osint
omgg!!?? 3 osint tools in 2 days??? wow this guy must be a very handsome and tuff individual

## what it does

takes an email and checks if its linked to a gitlab account. uses the invite trick to find users.

shows:
- username and display name
- bio and location
- company and website
- followers/following counts
- public/private projects
- account creation date
- last activity
- job title and organization
- profile pic url

## setup

```bash
pip install -r requirements.txt
```

create a `.env` file:
```
GITLAB_TOKEN=your_token_here
PROJECT_ID=your_project_id_here
```

you need a gitlab personal access token. get one from https://gitlab.com/-/profile/personal_access_tokens

you also need a project id. create a project and the id is in the project settings.

## usage

```bash
python main.py
```

type the email when it asks

it saves results as json files in a `lookups` folder
