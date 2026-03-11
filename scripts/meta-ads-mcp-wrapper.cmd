@echo off
REM Meta Ads MCP Wrapper — Sets environment variables before launching MCP server
REM Update these values with your actual credentials from .env.agents

set META_ACCESS_TOKEN=INSERT_YOUR_ACCESS_TOKEN
set META_APP_ID=INSERT_YOUR_APP_ID
set META_APP_SECRET=INSERT_YOUR_APP_SECRET
set META_AD_ACCOUNT_ID=INSERT_YOUR_AD_ACCOUNT_ID

REM Launch the Meta Ads MCP server (pipeboard-co/meta-ads-mcp)
uvx meta-ads-mcp

echo Meta Ads MCP server started
