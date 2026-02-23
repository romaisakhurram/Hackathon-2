"""
Email service for sending task reminders and notifications.
Supports multiple email providers (SMTP, SendGrid, etc.)
"""

import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service to handle email sending for reminders and notifications.
    """

    def __init__(self):
        # Email configuration - in production, these should come from environment variables
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "noreply@taskflow.com"
        self.sender_password = ""  # Should be set via environment variable
        self.use_tls = True

    async def send_task_reminder(
        self,
        recipient_email: str,
        task_title: str,
        task_description: Optional[str],
        due_date: datetime,
        reminder_time: datetime
    ) -> bool:
        """
        Send a task reminder email.

        Args:
            recipient_email: Email address of the recipient
            task_title: Title of the task
            task_description: Description of the task
            due_date: When the task is due
            reminder_time: When this reminder was scheduled

        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Create the email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"📋 Task Reminder: {task_title}"
            msg['From'] = self.sender_email
            msg['To'] = recipient_email

            # Create HTML and plain text versions
            html_content = self._create_reminder_html(
                task_title, task_description, due_date, reminder_time
            )
            text_content = self._create_reminder_text(
                task_title, task_description, due_date, reminder_time
            )

            msg.attach(MIMEText(text_content, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))

            # Send the email
            if self.smtp_password:
                await self._send_email(recipient_email, msg)
                logger.info(f"Reminder email sent to {recipient_email} for task: {task_title}")
                return True
            else:
                # Log the email content if no SMTP configured (for development)
                logger.info(f"[DEV MODE] Would send email to {recipient_email}:")
                logger.info(f"Subject: {msg['Subject']}")
                logger.info(f"Content: {text_content[:200]}...")
                return True

        except Exception as e:
            logger.error(f"Failed to send reminder email to {recipient_email}: {str(e)}")
            return False

    async def _send_email(self, recipient_email: str, msg: MIMEMultipart) -> None:
        """
        Send email via SMTP.

        Args:
            recipient_email: Email address of the recipient
            msg: The email message to send
        """
        try:
            # Create SMTP connection
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.smtp_password)
            server.sendmail(self.sender_email, recipient_email, msg.as_string())
            server.quit()
        except Exception as e:
            logger.error(f"SMTP error: {str(e)}")
            raise

    def _create_reminder_html(
        self,
        task_title: str,
        task_description: Optional[str],
        due_date: datetime,
        reminder_time: datetime
    ) -> str:
        """
        Create HTML email content for task reminder.
        """
        due_date_str = due_date.strftime("%B %d, %Y at %I:%M %p") if due_date else "No due date"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px 10px 0 0; text-align: center; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .task-title {{ font-size: 24px; font-weight: bold; margin-bottom: 10px; color: #667eea; }}
                .task-description {{ background: white; padding: 15px; border-left: 4px solid #667eea; margin: 20px 0; }}
                .reminder-info {{ margin: 20px 0; }}
                .info-item {{ margin: 10px 0; }}
                .label {{ font-weight: bold; color: #666; }}
                .cta-button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
                .footer {{ text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #999; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📋 Task Reminder</h1>
                </div>
                <div class="content">
                    <div class="task-title">{task_title}</div>
                    
                    {f'<div class="task-description">{task_description}</div>' if task_description else ''}
                    
                    <div class="reminder-info">
                        <div class="info-item">
                            <span class="label">⏰ Due Date:</span> {due_date_str}
                        </div>
                        <div class="info-item">
                            <span class="label">🔔 Reminder Time:</span> {reminder_time.strftime("%B %d, %Y at %I:%M %p")}
                        </div>
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="#" class="cta-button">View Task</a>
                    </div>
                    
                    <div class="footer">
                        <p>This is an automated reminder from TaskFlow.</p>
                        <p>© {datetime.now().year()} TaskFlow. All rights reserved.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    def _create_reminder_text(
        self,
        task_title: str,
        task_description: Optional[str],
        due_date: datetime,
        reminder_time: datetime
    ) -> str:
        """
        Create plain text email content for task reminder.
        """
        due_date_str = due_date.strftime("%B %d, %Y at %I:%M %p") if due_date else "No due date"
        reminder_str = reminder_time.strftime("%B %d, %Y at %I:%M %p")

        text = f"""
TASK REMINDER
=============

Task: {task_title}

{f'Description: {task_description}' if task_description else ''}

Due Date: {due_date_str}
Reminder Time: {reminder_str}

---
This is an automated reminder from TaskFlow.
© {datetime.now().year()} TaskFlow. All rights reserved.
        """
        return text.strip()

    async def send_welcome_email(self, recipient_email: str, user_name: str) -> bool:
        """
        Send a welcome email to new users.
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = "Welcome to TaskFlow! 🎉"
            msg['From'] = self.sender_email
            msg['To'] = recipient_email

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; }}
                    .content {{ padding: 30px; background: #f9f9f9; margin-top: 20px; border-radius: 10px; }}
                    .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Welcome to TaskFlow! 🎉</h1>
                    </div>
                    <div class="content">
                        <p>Hi {user_name},</p>
                        <p>Thank you for joining TaskFlow! We're excited to help you organize your tasks and boost your productivity.</p>
                        <p>Get started by creating your first task and setting up reminders.</p>
                        <div style="text-align: center;">
                            <a href="#" class="button">Create Your First Task</a>
                        </div>
                        <p>Best regards,<br>The TaskFlow Team</p>
                    </div>
                </div>
            </body>
            </html>
            """

            msg.attach(MIMEText(html_content, 'html'))

            if self.smtp_password:
                await self._send_email(recipient_email, msg)
                logger.info(f"Welcome email sent to {recipient_email}")
                return True
            else:
                logger.info(f"[DEV MODE] Would send welcome email to {recipient_email}")
                return True

        except Exception as e:
            logger.error(f"Failed to send welcome email: {str(e)}")
            return False


# Singleton instance
email_service = EmailService()
