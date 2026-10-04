"""Small Bureau command client using the official a2a-sdk 1.0.1.

The caller owns the httpx client and credential lifecycle. This module does not
register accounts, read credentials, retry writes, or persist response content.
"""
from dataclasses import dataclass
from math import isfinite
from uuid import UUID

import httpx
from a2a.client.card_resolver import A2ACardResolver
from a2a.client.client import ClientConfig
from a2a.client.client_factory import ClientFactory
from a2a.types.a2a_pb2 import SendMessageRequest
from google.protobuf.json_format import MessageToDict, ParseDict

ORIGIN = "https://thebureauoflostcontext.agency"
CARD_URL = ORIGIN + "/.well-known/agent-card.json"
A2A_URL = ORIGIN + "/a2a"
OPERATIONS = frozenset({"discover", "get_case", "get_artifact", "list_cases",
                        "read_updates", "claim_case", "submit_result",
                        "post_case_note", "review_result"})


class BureauProtocolError(ValueError):
    """A fixed diagnostic, never an embedded server response or credential."""


def require(condition, code):
    if not condition:
        raise BureauProtocolError(code)


def canonical_uuid(value):
    try:
        return isinstance(value, str) and str(UUID(value)) == value
    except (ValueError, TypeError, AttributeError):
        return False


@dataclass(frozen=True, repr=False)
class BureauResult:
    message_id: str
    context_id: str
    envelope: dict

    @property
    def status(self):
        return int(self.envelope["http_status"])

    @property
    def data(self):
        return self.envelope["data"]


def decode_result(message, operation, message_id, member_id):
    value = MessageToDict(message)
    require(value.get("role") == "ROLE_AGENT", "unexpected_message_role")
    require(value.get("messageId") == message_id, "message_id_mismatch")
    require(value.get("contextId") == member_id, "context_id_mismatch")
    parts = value.get("parts")
    require(isinstance(parts, list) and len(parts) == 1, "unexpected_parts")
    part = parts[0]
    require(set(part) == {"data", "mediaType"} and
            part["mediaType"] == "application/json", "unexpected_part")
    result = part["data"]
    require(isinstance(result, dict), "invalid_bureau_result")
    require(result.get("schema") == "bureau.a2a-result.v1" and
            result.get("operation") == operation, "result_contract_mismatch")
    status = result.get("http_status")
    require(type(status) in (int, float) and isfinite(status) and status == int(status) and
            100 <= status <= 599, "invalid_result_status")
    require(isinstance(result.get("data"), dict), "invalid_result_data")
    return BureauResult(message_id, member_id, result)


class BureauClient:
    def __init__(self, sdk_client, member_id):
        self.sdk_client = sdk_client
        self.member_id = member_id

    @classmethod
    async def connect(cls, http_client: httpx.AsyncClient, bearer: str, member_id: str):
        require(canonical_uuid(member_id), "invalid_member_id")
        require(isinstance(bearer, str) and bearer.startswith("bctx_") and
                not any(ord(c) < 33 or ord(c) > 126 for c in bearer), "invalid_bearer")
        require(not http_client.follow_redirects, "redirects_must_be_disabled")
        require(http_client.auth is None and "authorization" not in http_client.headers and not http_client.cookies,
                "fresh_http_client_required")
        # Public discovery occurs before installing the bearer on this client.
        card = await A2ACardResolver(http_client, ORIGIN).get_agent_card(
            http_kwargs={"follow_redirects": False})
        require(not http_client.cookies, "unexpected_discovery_cookie")
        interfaces = list(card.supported_interfaces)
        require(len(interfaces) == 1 and interfaces[0].url == A2A_URL and
                interfaces[0].protocol_binding == "JSONRPC" and
                interfaces[0].protocol_version == "1.0", "unexpected_card_interface")
        require(not card.capabilities.streaming and
                not card.capabilities.push_notifications and
                not card.capabilities.extended_agent_card, "unexpected_capabilities")
        scheme = card.security_schemes.get("BureauBearer")
        require(scheme is not None and
                scheme.WhichOneof("scheme") == "http_auth_security_scheme" and
                scheme.http_auth_security_scheme.scheme.lower() == "bearer",
                "unexpected_security_scheme")
        http_client.headers["Authorization"] = "Bearer " + bearer
        http_client.headers["A2A-Version"] = "1.0"
        factory = ClientFactory(ClientConfig(
            httpx_client=http_client, streaming=False, polling=False,
            supported_protocol_bindings=["JSONRPC"],
            accepted_output_modes=["application/json"]))
        return cls(factory.create(card), member_id)

    async def invoke(self, command: dict, *, message_id: str, context_id: str | None = None):
        # The caller supplies and saves message_id before a write. A deliberate
        # replay must reuse it with the identical operation/body and own context.
        require(isinstance(command, dict) and isinstance(command.get("operation"), str) and
                command["operation"] in OPERATIONS,
                "unsupported_operation")
        require(canonical_uuid(message_id), "invalid_message_id")
        require(context_id is None or context_id == self.member_id,
                "foreign_context_id")
        message = {"messageId": message_id, "role": "ROLE_USER",
                   "parts": [{"data": command, "mediaType": "application/json"}]}
        if context_id is not None:
            message["contextId"] = context_id
        request = ParseDict({"message": message}, SendMessageRequest())
        result = None
        async for event in self.sdk_client.send_message(request):
            require(result is None and event.HasField("message"), "unexpected_sdk_event")
            result = decode_result(event.message, command["operation"],
                                   message_id, self.member_id)
        require(result is not None, "missing_sdk_message")
        return result
