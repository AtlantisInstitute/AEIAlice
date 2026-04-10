#!/usr/bin/env python3
"""
Alice Notification Service - Atlantis Institute
Handles GitHub, Jira, and Confluence notifications via Discord webhooks.
AI conversations are handled by OpenClaw (separate gateway process).
"""

import config
import logging
import os
import sys
import signal
import psutil
import atexit
import threading
import asyncio

# Import integration modules
from notification_manager import init_notification_manager
from webhook_handler import webhook_handler
from task_scheduler import task_scheduler

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('Alice')

# PID file location
PID_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'alice.pid')


def kill_all_alice_instances():
    """Kill all running Alice instances."""
    current_pid = os.getpid()
    killed_count = 0

    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline', [])
            if cmdline and 'alice.py' in ' '.join(cmdline).lower():
                if proc.info['pid'] != current_pid:
                    logger.info(f"Killing old Alice instance (PID: {proc.info['pid']})")
                    proc.kill()
                    killed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    if killed_count > 0:
        logger.info(f"Killed {killed_count} old Alice instance(s)")
    return killed_count


def check_single_instance():
    """Ensure only one instance of Alice is running."""
    kill_all_alice_instances()

    try:
        with open(PID_FILE, 'w') as f:
            f.write(str(os.getpid()))
        logger.info(f'PID file created: {PID_FILE}')
    except Exception as e:
        logger.warning(f'Could not create PID file: {e}')


def cleanup_pid_file():
    """Remove the PID file on exit."""
    try:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
            logger.info('PID file removed')
    except Exception as e:
        logger.warning(f'Could not remove PID file: {e}')


def stop_integrations():
    """Stop all integration services."""
    logger.info('Stopping integrations...')
    if task_scheduler:
        task_scheduler.stop()
    logger.info('Integrations stopped')


def signal_handler(signum, frame):
    """Handle termination signals gracefully."""
    logger.info(f'Received signal {signum}, shutting down Alice notification service...')
    if task_scheduler:
        task_scheduler.stop()
    kill_all_alice_instances()
    cleanup_pid_file()
    sys.exit(0)


def main():
    """Main function to run the Alice notification service."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Register cleanup function
    atexit.register(cleanup_pid_file)
    atexit.register(kill_all_alice_instances)
    atexit.register(stop_integrations)

    # Ensure single instance
    check_single_instance()

    logger.info('Starting Alice notification service...')
    logger.info('AI conversations are handled by OpenClaw gateway.')
    logger.info('This service handles GitHub/Jira/Confluence notifications only.')

    # Initialize notification manager (no Discord bot needed - uses webhook URLs)
    notification_manager = init_notification_manager()

    # Setup webhook handler
    webhook_handler.set_notification_manager(notification_manager)

    # Start webhook server in background thread
    webhook_thread = threading.Thread(
        target=webhook_handler.run,
        daemon=True,
        name="WebhookServer"
    )
    webhook_thread.start()
    logger.info(f"Webhook server started on port {config.WEBHOOK_CONFIG['port']}")

    # Setup and start task scheduler in async event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    task_scheduler.set_notification_manager(notification_manager)

    try:
        loop.run_until_complete(task_scheduler.start())
        logger.info("Task scheduler started")
        logger.info("Alice notification service is running.")
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info('Keyboard interrupt received, shutting down...')
    except Exception as e:
        logger.error(f'An error occurred: {e}')
    finally:
        logger.info('Cleaning up and shutting down Alice notification service...')
        stop_integrations()
        loop.close()
        kill_all_alice_instances()
        cleanup_pid_file()
        logger.info('Alice notification service stopped.')


if __name__ == '__main__':
    main()
