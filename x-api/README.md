# x-api — X (Twitter) API v2 MCP Server

Exposes the X API v2 as MCP tools, dynamically generated from the official OpenAPI spec. Currently exposes **131 tools** including tweet CRUD, user lookup, media upload, lists, bookmarks, follows, mutes, blocks, spaces, DMs, and more.

## Setup

### 1. Install the plugin

```bash
/plugin install x-api@indie-toolkit
```

### 2. Configure authentication

**Option A — Bearer Token** (simplest):

```bash
export X_BEARER_TOKEN="your_bearer_token"
export X_AUTH_MODE=bearer
```

**Option B — OAuth2 PKCE** (for user-level access):

```bash
export X_CLIENT_ID="your_oauth2_client_id"
export X_AUTH_MODE=oauth2
node x-api/dist/auth-cli.js
# Opens browser for OAuth authorization
# Tokens saved to ~/.x-mcp/tokens.json automatically
```

### 3. Run

Claude Code auto-starts the MCP server when the plugin is active.

Or manually:

```bash
cd x-api
npm run build
X_BEARER_TOKEN=your_token node dist/server.js
```

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `X_AUTH_MODE` | No | `bearer` | `bearer` or `oauth2` |
| `X_BEARER_TOKEN` | Yes (bearer) | — | X API Bearer Token |
| `X_CLIENT_ID` | Yes (oauth2) | — | OAuth2 Client ID from developer portal |
| `X_API_TOOL_ALLOWLIST` | No | all | Comma-separated operationIds to expose |

## Tool Allowlist

To expose only a subset of tools (reduces startup time and noise):

```bash
export X_API_TOOL_ALLOWLIST="getTweets,createTweet,getUser,getUsers"
```

## Tools

All 131 tools are auto-generated from the X API v2 OpenAPI spec. Key tool groups:

- **Tweets**: `createTweet`, `getTweet`, `deleteTweet`, `updateTweet`, `getTweets`, `hideReply`
- **Users**: `getUser`, `getUsers`, `getUserByUsername`, `getFollowing`, `getFollowers`, `followUser`, `unfollowUser`
- **Likes**: `likeTweet`, `unlikeTweet`, `getLikedTweets`
- **Retweets**: `retweet`, `unretweet`
- **Bookmarks**: `getBookmarks`, `bookmarkTweet`, `removeBookmark`
- **Lists**: `createList`, `getList`, `getListTweets`, `addListMember`, `followList`, `unfollowList`
- **Spaces**: `getSpace`, `getSpaces`, `searchSpaces`, `getSpaceBuyers`
- **DMs**: `createDmConversation`, `getDmConversations`, `getDmEvents`
- **Mutes/Blocks**: `muteUser`, `unmuteUser`, `getMutedUsers`, `blockUser`, `unblockUser`, `getBlockedUsers`
- **Search**: `tweetsSearchRecent`, `tweetsSearchAll`
- **Compliance**: `getComplianceJobs`, `createComplianceJob`

## File Structure

```text
x-api/
├── src/
│   ├── server.ts        # MCP server entry point
│   ├── auth-cli.ts      # OAuth2 PKCE login CLI
│   ├── openapi.ts       # OpenAPI spec parser
│   ├── x-client.ts      # HTTP client with error normalization
│   ├── types.ts         # Shared types
│   └── auth/
│       ├── store.ts     # Token persistence (~/.x-mcp/)
│       ├── bearer.ts   # Bearer token auth
│       └── oauth2.ts    # OAuth2 PKCE + auto-refresh
└── dist/                # Built by npm run build
```
