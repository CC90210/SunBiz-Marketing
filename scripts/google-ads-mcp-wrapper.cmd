@echo off
REM Google Ads MCP Wrapper — Sets environment variables before launching MCP server
REM Update these values with your actual credentials from .env.agents

set GOOGLE_ADS_DEVELOPER_TOKEN=INSERT_YOUR_DEVELOPER_TOKEN
set GOOGLE_ADS_CLIENT_ID=INSERT_YOUR_CLIENT_ID
set GOOGLE_ADS_CLIENT_SECRET=INSERT_YOUR_CLIENT_SECRET
set GOOGLE_ADS_REFRESH_TOKEN=INSERT_YOUR_REFRESH_TOKEN
set GOOGLE_ADS_LOGIN_CUSTOMER_ID=INSERT_YOUR_CUSTOMER_ID

REM Launch the Google Ads MCP server
REM Option 1: Community MCP with write capabilities
REM npx google-ads-mcp-complete
REM Option 2: Custom Python MCP server
REM python scripts/google_ads_mcp_server.py
REM Option 3: Official (READ-ONLY)
REM python -m google_ads_mcp

echo Google Ads MCP server started
