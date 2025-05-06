import time
import re
from instaloader import Instaloader, Hashtag, Profile
import pandas as pd
from itertools import islice


# ─── 1. AUTHENTICATE USING BROWSER SESSION ────────────────────────────────
L = Instaloader()

# Load from browser cookies: adjust browser name or cookiefile as needed
# For CLI: instaloader --load-cookies chrome
L.load_session_from_file(username='ll98150', filename='myinsta-session')  # Assumes session file exists

# ─── 2. COLLECT UNIQUE UPLOADERS VIA HASHTAGS ─────────────────────────────
hashtags = ['UKPersonalTrainer', 'UKNutritionCoach']
usernames = set()

for tag in hashtags:
    hashtag = Hashtag.from_name(L.context, tag)
    print(f'Collecting posts from hashtag: {tag}')
    for post in islice(hashtag.get_posts_resumable(), 200):
        usernames.add(post.owner_username)
        time.sleep(1)  # brief pause per post
        if len(usernames) >= 100:
            break
print(f'Collected {len(usernames)} unique usernames from hashtags: {hashtags}')
# ─── 3. FETCH PROFILE METADATA ────────────────────────────────────────────
records = []

for uname in sorted(usernames):
    try:
        profile = Profile.from_username(L.context, uname)
    except Exception:
        continue

    bio = profile.biography or ''
    # Extract email via regex
    email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', bio)
    email = email_match.group(0) if email_match else ''

    records.append({
        'username':        profile.username,
        'full_name':       profile.full_name,
        'profile_url':     f'https://www.instagram.com/{profile.username}/',
        'email':           email,
        'external_url':    profile.external_url or '',
        'expertise':       ','.join(profile.biography_hashtags),
        'bio_summary':     bio[:150] + '...' if len(bio) > 150 else bio
    })

    time.sleep(2)  # polite pause to mitigate rate limits

print(f'Fetched metadata for {len(records)} profiles')
# ─── 4. EXPORT TO CSV ───────────────────────────────────────────────────────
df = pd.DataFrame(records)
df.to_csv('UK Wellness Professionals.csv', index=False)
print(f'Successfully exported {len(df)} profiles to UK Wellness Professionals.csv')
