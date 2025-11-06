"""
FARADAY AI - Gmail Connector
Gmail API integration for sending and reading emails
"""

from typing import List, Dict, Any, Optional
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False

from config.settings import settings
from utils.logger import logger


# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.readonly']


class GmailConnector:
    """Gmail API Connector"""

    def __init__(self):
        """Initialize Gmail connector"""
        self.config = settings.connectors
        self.service = None
        self.enabled = self.config.gmail_enabled

        if not GMAIL_AVAILABLE:
            logger.warning("⚠️  Gmail API libraries not installed. Install with: pip install google-auth google-auth-oauthlib google-api-python-client")
            self.enabled = False

        if self.enabled:
            logger.info("📧 Gmail Connector initialized")

    async def authenticate(self) -> bool:
        """
        Authenticate with Gmail API using OAuth 2.0

        Returns:
            True if authentication successful
        """
        if not self.enabled or not GMAIL_AVAILABLE:
            logger.warning("⚠️  Gmail connector not available")
            return False

        try:
            creds = None

            # Load existing token
            token_path = self.config.gmail_token_path
            if token_path.exists():
                creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

            # Refresh or create new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    credentials_path = self.config.gmail_credentials_path
                    if not credentials_path.exists():
                        logger.error(f"❌ Gmail credentials file not found: {credentials_path}")
                        return False

                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(credentials_path), SCOPES
                    )
                    creds = flow.run_local_server(port=0)

                # Save token
                token_path.parent.mkdir(parents=True, exist_ok=True)
                token_path.write_text(creds.to_json())

            # Build service
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info("✅ Gmail authentication successful")
            return True

        except Exception as e:
            logger.error(f"❌ Gmail authentication failed: {e}")
            return False

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: bool = False,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Send email via Gmail.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body
            html: Whether body is HTML (default: False)
            cc: CC recipients (optional)
            bcc: BCC recipients (optional)

        Returns:
            Result dict with message ID
        """
        try:
            if not self.service:
                if not await self.authenticate():
                    return {"success": False, "error": "Authentication failed"}

            logger.info(f"📧 Sending email to: {to}")

            # Create message
            message = MIMEMultipart() if html else MIMEText(body)

            if html:
                message.attach(MIMEText(body, 'html'))

            message['to'] = to
            message['subject'] = subject

            if cc:
                message['cc'] = ', '.join(cc)
            if bcc:
                message['bcc'] = ', '.join(bcc)

            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

            # Send message
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()

            logger.info(f"✅ Email sent: {sent_message['id']}")

            return {
                "success": True,
                "message_id": sent_message['id'],
                "to": to,
                "subject": subject
            }

        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            return {"success": False, "error": str(e)}

    async def read_emails(
        self,
        max_results: int = 10,
        query: Optional[str] = None,
        unread_only: bool = False
    ) -> Dict[str, Any]:
        """
        Read emails from Gmail.

        Args:
            max_results: Maximum number of emails to retrieve
            query: Gmail search query (optional)
            unread_only: Only retrieve unread emails

        Returns:
            List of emails
        """
        try:
            if not self.service:
                if not await self.authenticate():
                    return {"success": False, "error": "Authentication failed"}

            logger.info(f"📬 Reading emails (max: {max_results})")

            # Build query
            if unread_only:
                query = 'is:unread' + (f' {query}' if query else '')

            # Get messages
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q=query
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                logger.info("📭 No emails found")
                return {"success": True, "emails": [], "count": 0}

            # Get full message details
            emails = []
            for msg in messages:
                msg_data = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()

                # Extract headers
                headers = msg_data['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown')

                # Extract body
                body = self._extract_body(msg_data['payload'])

                emails.append({
                    "id": msg['id'],
                    "thread_id": msg['threadId'],
                    "subject": subject,
                    "from": from_email,
                    "date": date,
                    "snippet": msg_data.get('snippet', ''),
                    "body": body[:500]  # Truncate long bodies
                })

            logger.info(f"✅ Retrieved {len(emails)} emails")

            return {
                "success": True,
                "emails": emails,
                "count": len(emails)
            }

        except Exception as e:
            logger.error(f"❌ Failed to read emails: {e}")
            return {"success": False, "error": str(e)}

    def _extract_body(self, payload: dict) -> str:
        """Extract email body from payload"""
        try:
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        data = part['body'].get('data', '')
                        return base64.urlsafe_b64decode(data).decode('utf-8')
            elif 'body' in payload:
                data = payload['body'].get('data', '')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8')
        except Exception as e:
            logger.error(f"Error extracting body: {e}")

        return ""

    async def search_emails(self, query: str, max_results: int = 10) -> Dict[str, Any]:
        """
        Search emails by query.

        Args:
            query: Gmail search query
            max_results: Maximum results

        Returns:
            Search results
        """
        return await self.read_emails(max_results=max_results, query=query)


# Singleton instance
_gmail_connector_instance = None


def get_gmail_connector() -> GmailConnector:
    """Get or create Gmail connector singleton"""
    global _gmail_connector_instance
    if _gmail_connector_instance is None:
        _gmail_connector_instance = GmailConnector()
    return _gmail_connector_instance


# Export
__all__ = ['GmailConnector', 'get_gmail_connector']
