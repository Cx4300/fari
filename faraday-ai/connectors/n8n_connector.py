"""
FARADAY AI - N8N Connector
N8N workflow automation integration
"""

from typing import Dict, Any, Optional
import aiohttp
import json

from config.settings import settings
from utils.logger import logger


class N8NConnector:
    """N8N Workflow Automation Connector"""

    def __init__(self):
        """Initialize N8N connector"""
        self.config = settings.connectors
        self.enabled = self.config.n8n_enabled
        self.webhook_url = self.config.n8n_webhook_url
        self.api_key = self.config.n8n_api_key

        if self.enabled:
            logger.info("🔗 N8N Connector initialized")
        else:
            logger.info("ℹ️  N8N Connector disabled")

    async def send_webhook(
        self,
        data: Dict[str, Any],
        webhook_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send data to N8N webhook.

        Args:
            data: Data to send
            webhook_url: Optional webhook URL (uses default if not provided)

        Returns:
            Response from webhook
        """
        try:
            if not self.enabled:
                logger.warning("⚠️  N8N connector is disabled")
                return {
                    "success": False,
                    "error": "N8N connector is disabled in settings"
                }

            url = webhook_url or self.webhook_url

            if not url:
                logger.error("❌ No webhook URL configured")
                return {
                    "success": False,
                    "error": "No webhook URL configured"
                }

            logger.info(f"🔗 Sending webhook to N8N: {url[:50]}...")

            # Prepare headers
            headers = {
                'Content-Type': 'application/json'
            }

            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'

            # Send POST request
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=data,
                    headers=headers,
                    timeout=30
                ) as response:
                    response_text = await response.text()

                    if response.status in [200, 201]:
                        try:
                            response_data = json.loads(response_text)
                        except json.JSONDecodeError:
                            response_data = {"raw": response_text}

                        logger.info("✅ Webhook sent successfully")

                        return {
                            "success": True,
                            "status_code": response.status,
                            "response": response_data
                        }
                    else:
                        logger.error(f"❌ Webhook failed: {response.status}")
                        return {
                            "success": False,
                            "status_code": response.status,
                            "error": response_text
                        }

        except asyncio.TimeoutError:
            logger.error("❌ Webhook timeout")
            return {
                "success": False,
                "error": "Request timeout"
            }
        except Exception as e:
            logger.error(f"❌ Webhook error: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def trigger_workflow(
        self,
        workflow_id: str,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Trigger N8N workflow by ID.

        Args:
            workflow_id: Workflow ID
            data: Optional data to pass to workflow

        Returns:
            Workflow execution result
        """
        try:
            if not self.enabled:
                return {"success": False, "error": "N8N connector disabled"}

            logger.info(f"🚀 Triggering workflow: {workflow_id}")

            # Construct workflow webhook URL
            # Assumes N8N webhook URL pattern: https://n8n.example.com/webhook/{workflow_id}
            if self.webhook_url:
                base_url = self.webhook_url.rsplit('/', 1)[0]
                workflow_url = f"{base_url}/{workflow_id}"
            else:
                logger.error("❌ No base webhook URL configured")
                return {"success": False, "error": "No webhook URL configured"}

            # Send to workflow-specific webhook
            result = await self.send_webhook(
                data=data or {},
                webhook_url=workflow_url
            )

            return result

        except Exception as e:
            logger.error(f"❌ Failed to trigger workflow: {e}")
            return {"success": False, "error": str(e)}

    async def get_workflow_status(
        self,
        execution_id: str,
        n8n_api_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get workflow execution status.
        Requires N8N API access.

        Args:
            execution_id: Execution ID
            n8n_api_url: N8N API base URL

        Returns:
            Execution status
        """
        try:
            if not self.enabled:
                return {"success": False, "error": "N8N connector disabled"}

            if not n8n_api_url:
                logger.error("❌ N8N API URL not provided")
                return {"success": False, "error": "N8N API URL required"}

            url = f"{n8n_api_url}/executions/{execution_id}"

            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'

            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "execution_id": execution_id,
                            "status": data.get('finished', False),
                            "data": data
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"API request failed: {response.status}"
                        }

        except Exception as e:
            logger.error(f"❌ Failed to get workflow status: {e}")
            return {"success": False, "error": str(e)}

    def is_available(self) -> bool:
        """Check if N8N connector is available"""
        return self.enabled and bool(self.webhook_url)


# Singleton instance
_n8n_connector_instance = None


def get_n8n_connector() -> N8NConnector:
    """Get or create N8N connector singleton"""
    global _n8n_connector_instance
    if _n8n_connector_instance is None:
        _n8n_connector_instance = N8NConnector()
    return _n8n_connector_instance


# Export
__all__ = ['N8NConnector', 'get_n8n_connector']
