"""
FARADAY AI - WhatsApp Connector
Twilio WhatsApp API integration
"""

from typing import Dict, Any, Optional

try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

from config.settings import settings
from utils.logger import logger


class WhatsAppConnector:
    """WhatsApp Connector using Twilio API"""

    def __init__(self):
        """Initialize WhatsApp connector"""
        self.config = settings.connectors
        self.client = None
        self.enabled = self.config.whatsapp_enabled

        if not TWILIO_AVAILABLE:
            logger.warning("⚠️  Twilio library not installed. Install with: pip install twilio")
            self.enabled = False

        if self.enabled:
            self._initialize_client()
            logger.info("💬 WhatsApp Connector initialized")

    def _initialize_client(self):
        """Initialize Twilio client"""
        try:
            if not self.config.twilio_account_sid or not self.config.twilio_auth_token:
                logger.warning("⚠️  Twilio credentials not configured")
                self.enabled = False
                return

            self.client = Client(
                self.config.twilio_account_sid,
                self.config.twilio_auth_token
            )
            logger.info("✅ Twilio client initialized")

        except Exception as e:
            logger.error(f"❌ Failed to initialize Twilio client: {e}")
            self.enabled = False

    async def send_message(
        self,
        to: str,
        body: str,
        media_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send WhatsApp message.

        Args:
            to: Recipient phone number (with country code, e.g., +385991234567)
            body: Message text
            media_url: Optional media URL (image, video, etc.)

        Returns:
            Result dict with message SID
        """
        try:
            if not self.enabled or not self.client:
                logger.warning("⚠️  WhatsApp connector not available")
                return {
                    "success": False,
                    "error": "WhatsApp connector not available or not configured"
                }

            # Format phone number for WhatsApp
            if not to.startswith('whatsapp:'):
                to = f'whatsapp:{to}'

            from_number = self.config.twilio_whatsapp_number
            if not from_number.startswith('whatsapp:'):
                from_number = f'whatsapp:{from_number}'

            logger.info(f"💬 Sending WhatsApp message to: {to}")

            # Send message
            message_params = {
                'body': body,
                'from_': from_number,
                'to': to
            }

            if media_url:
                message_params['media_url'] = [media_url]

            message = self.client.messages.create(**message_params)

            logger.info(f"✅ WhatsApp message sent: {message.sid}")

            return {
                "success": True,
                "message_sid": message.sid,
                "to": to,
                "status": message.status,
                "body": body
            }

        except Exception as e:
            logger.error(f"❌ Failed to send WhatsApp message: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_message_status(self, message_sid: str) -> Dict[str, Any]:
        """
        Get WhatsApp message status.

        Args:
            message_sid: Message SID from send_message

        Returns:
            Message status info
        """
        try:
            if not self.enabled or not self.client:
                return {"success": False, "error": "WhatsApp connector not available"}

            message = self.client.messages(message_sid).fetch()

            return {
                "success": True,
                "message_sid": message.sid,
                "status": message.status,
                "to": message.to,
                "from": message.from_,
                "date_sent": str(message.date_sent),
                "error_code": message.error_code,
                "error_message": message.error_message
            }

        except Exception as e:
            logger.error(f"❌ Failed to get message status: {e}")
            return {"success": False, "error": str(e)}

    async def send_template_message(
        self,
        to: str,
        template_sid: str,
        template_variables: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Send WhatsApp template message.

        Args:
            to: Recipient phone number
            template_sid: Twilio template SID
            template_variables: Template variables

        Returns:
            Result dict
        """
        try:
            if not self.enabled or not self.client:
                return {"success": False, "error": "WhatsApp connector not available"}

            # Format numbers
            if not to.startswith('whatsapp:'):
                to = f'whatsapp:{to}'

            from_number = self.config.twilio_whatsapp_number
            if not from_number.startswith('whatsapp:'):
                from_number = f'whatsapp:{from_number}'

            logger.info(f"💬 Sending template message to: {to}")

            # Send template message
            message = self.client.messages.create(
                content_sid=template_sid,
                from_=from_number,
                to=to,
                content_variables=template_variables or {}
            )

            logger.info(f"✅ Template message sent: {message.sid}")

            return {
                "success": True,
                "message_sid": message.sid,
                "to": to,
                "status": message.status
            }

        except Exception as e:
            logger.error(f"❌ Failed to send template message: {e}")
            return {"success": False, "error": str(e)}

    def is_available(self) -> bool:
        """Check if WhatsApp connector is available"""
        return self.enabled and self.client is not None


# Singleton instance
_whatsapp_connector_instance = None


def get_whatsapp_connector() -> WhatsAppConnector:
    """Get or create WhatsApp connector singleton"""
    global _whatsapp_connector_instance
    if _whatsapp_connector_instance is None:
        _whatsapp_connector_instance = WhatsAppConnector()
    return _whatsapp_connector_instance


# Export
__all__ = ['WhatsAppConnector', 'get_whatsapp_connector']
