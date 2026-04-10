"""
Flask webhook server and event processors.

Receives inbound webhooks from GitHub, Jira, and Confluence,
verifies signatures, and routes events to the notification manager.
"""
