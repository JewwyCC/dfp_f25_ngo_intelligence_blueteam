# Bluesky Authentication Setup

## Quick Start

1. **Copy the template:**
   ```bash
   cp auth/bluesky/config/auth_template.json auth/bluesky/config/auth.json
   ```

2. **Get your Bluesky app password:**
   - Go to https://bsky.app/settings/app-passwords
   - Create a new app password
   - Copy the generated password

3. **Edit `auth/bluesky/config/auth.json`:**
   ```json
   {
     "bluesky": {
       "username": "your-handle.bsky.social",
       "password": "your-app-password-here"
     }
   }
   ```

4. **Verify the file is ignored by git:**
   ```bash
   git check-ignore auth/bluesky/config/auth.json
   ```
   This should output the file path, confirming it's ignored.

## Security Notes

- ✅ `auth.json` is in `.gitignore` and will NOT be committed
- ✅ Use app passwords, not your main account password
- ✅ Never share your auth.json file
- ❌ NEVER commit credentials to the repository

## Environment Variable Alternative

You can also use environment variables instead of the auth.json file:

```bash
export BLUESKY_USERNAME="your-handle.bsky.social"
export BLUESKY_PASSWORD="your-app-password"
```

The script will check environment variables first before looking for auth.json.
