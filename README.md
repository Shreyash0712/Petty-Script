# Petty GitHub Script

Tired of people who follow you on GitHub just to get a follow back, and then immediately unfollow you? This automated script keeps track of your followers and automatically unfollows anyone who decides to hit that unfollow button on you. It also rewards loyalty by automatically following back any new followers you get!

## How it works
1. Runs automatically every 8 hours via GitHub Actions.
2. Checks your current followers against a saved list (`followers.json`).
3. If someone from the saved list is no longer following you, it automatically unfollows them.
4. If someone new starts following you, it automatically follows them back.
5. Updates the saved list with your current followers.

## Setup Instructions

1. **Create a Personal Access Token (PAT)**
   - Go to [GitHub Developer Settings](https://github.com/settings/tokens).
   - Generate a new **Classic** Personal Access Token.
   - Give it a descriptive name (e.g., "Petty Script Token").
   - Check the `user:follow` scope (this is required to follow/unfollow users).
   - Generate and copy the token.

2. **Add the Token to Repository Secrets**
   - Go to this repository's **Settings** on GitHub.
   - Navigate to **Secrets and variables** -> **Actions**.
   - Click **New repository secret**.
   - Name the secret exactly `USER_PAT`.
   - Paste the token you copied in the Secret field and click Add secret.

3. **Run the First Workflow**
   - Go to the **Actions** tab in this repository.
   - Select **Unfollow Traitors** from the left sidebar.
   - Click **Run workflow** -> **Run workflow**.
   - The first run will just fetch your current followers and create a `followers.json` file. 

That's it! The script will now run automatically every day and take care of the rest. 🚀
