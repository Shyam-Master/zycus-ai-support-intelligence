# Profile and User Settings

## Overview
This document covers managing user profiles, preferences, and account settings.

## Common Issues

### Unable to update profile
If a user cannot update their profile information, it is often due to restrictive Role-Based Access Control (RBAC). 
- Verify the user has the `PROFILE_EDIT` permission.
- If settings are not saving, clear browser cache.

### Settings not saving
Users may report that their preferences (like dark mode or notification settings) revert after refreshing.
- Ensure the user is not in incognito mode blocking local storage.
- If it persists globally, it may be a database sync issue.

### User preference issues
For missing preference toggles, ensure the account is on a supported tier.
