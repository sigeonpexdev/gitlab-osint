import os
import asyncio
import httpx
import time
import re
import json
import urllib.parse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

def save_lookup(email, data):
    try:
        os.makedirs("lookups", exist_ok=True)
        n = re.sub(r'[^a-zA-Z0-9]', '_', email)
        p = f"lookups/gitlab_{n}_{int(time.time())}.json"
        with open(p, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"[+] saved {p}")
    except:
        pass

async def probe_gitlab(email):
    target_email = email.strip()
    
    GITLAB_TOKEN = os.getenv("GITLAB_TOKEN", "").strip()
    PROJECT_ID = os.getenv("PROJECT_ID", "").strip()

    if not all([GITLAB_TOKEN, PROJECT_ID]):
        return None, "missing gitlab secrets (set GITLAB_TOKEN, PROJECT_ID in .env)"

    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
    invite_url = f"https://gitlab.com/api/v4/projects/{PROJECT_ID}/invitations"
    members_url = f"https://gitlab.com/api/v4/projects/{PROJECT_ID}/members/all"
    
    async with httpx.AsyncClient(headers=headers, timeout=15.0) as client:
        try:
            before_members = await client.get(members_url)
            before_ids = {m["id"] for m in before_members.json()} if before_members.status_code == 200 else set()

            post_res = await client.post(invite_url, json={"email": target_email, "access_level": 10})
            
            if post_res.status_code not in [201, 409]:
                return None, f"GitLab API error: {post_res.status_code}"

            await asyncio.sleep(1.5)

            after_members = await client.get(members_url)
            target_user = None
            
            if after_members.status_code == 200:
                for m in after_members.json():
                    if m["id"] not in before_ids:
                        target_user = m
                        break

            target_invite = None
            if not target_user:
                invites_res = await client.get(invite_url)
                if invites_res.status_code == 200:
                    for inv in invites_res.json():
                        if inv.get("invite_email") == target_email:
                            target_invite = inv
                            break

            if target_user:
                delete_member_url = f"https://gitlab.com/api/v4/projects/{PROJECT_ID}/members/{target_user['id']}"
                await client.delete(delete_member_url)
            elif target_invite:
                safe_email = urllib.parse.quote(target_email)
                await client.delete(f"{invite_url}/{safe_email}")

            if target_user:
                profile_res = await client.get(f"https://gitlab.com/api/v4/users/{target_user['id']}")
                final_data = profile_res.json() if profile_res.status_code == 200 else target_user
                return final_data, "found"
            elif target_invite:
                return target_invite.get("user") or target_invite, "found"
            
            return None, "not found"
            
        except Exception as e:
            return None, str(e)

def main():
    cls()
    
    email = input("[?] email: ").strip()
    print(f"[*] checking {email} on gitlab")
    
    data, status = asyncio.run(probe_gitlab(email))
    
    if not data and status == "not found":
        print("[-] no gitlab account found")
        return
    elif not data:
        print(f"[!] {status}")
        return
    
    print("[+] gitlab account found")
    save_lookup(email, data)
    
    print(f"\nUsername: {data.get('username', 'N/A')}")
    print(f"Display Name: {data.get('name', 'N/A')}")
    
    if data.get('email'):
        print(f"Email: {data.get('email')}")
    if data.get('bio'):
        print(f"Bio: {data.get('bio')}")
    if data.get('location'):
        print(f"Location: {data.get('location')}")
    if data.get('company'):
        print(f"Company: {data.get('company')}")
    if data.get('website_url'):
        print(f"Website: {data.get('website_url')}")
    if data.get('twitter'):
        print(f"Twitter: @{data.get('twitter')}")
    
    print(f"Followers: {data.get('followers', 0)}")
    print(f"Following: {data.get('following', 0)}")
    print(f"Public Repos: {data.get('public_projects', 0)}")
    print(f"Private Repos: {data.get('private_projects', 0)}")
    
    if data.get('created_at'):
        print(f"Created: {data.get('created_at')}")
    if data.get('last_activity_on'):
        print(f"Last Active: {data.get('last_activity_on')}")
    
    if data.get('job_title'):
        print(f"Job Title: {data.get('job_title')}")
    if data.get('organization'):
        print(f"Organization: {data.get('organization')}")
    
    if data.get('state'):
        print(f"Account State: {data.get('state')}")
    
    if data.get('is_admin'):
        print("Admin: yes")
    if data.get('confirmed_at'):
        print(f"Confirmed: {data.get('confirmed_at')}")
    
    if data.get('web_url'):
        print(f"\nProfile: {data.get('web_url')}")
    if data.get('avatar_url'):
        print(f"Avatar: {data.get('avatar_url')}")
    
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] stopped")
    except Exception as e:
        print(f"[!] {e}")
