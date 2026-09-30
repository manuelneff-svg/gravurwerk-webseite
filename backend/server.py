from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import re
import ipaddress
import logging
import uuid
import httpx
from html import escape
from html.parser import HTMLParser
from urllib.parse import urlparse
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Email (Emergent managed Resend integration)
# ---------------------------------------------------------------------------
EMAIL_BASE_URL = "https://integrations.emergentagent.com"
EMAIL_KEY = os.environ["EMERGENT_EMAIL_KEY"]
EMAIL_FROM_NAME = os.environ["EMAIL_FROM_NAME"]
OWNER_EMAIL = os.environ["OWNER_EMAIL"]

_SHORTENERS = ("bit.ly", "tinyurl.com", "t.co", "is.gd", "cutt.ly", "goo.gl", "rebrand.ly")
_CRED_ASK = ("reply with your password", "reply with the code", "send your password", "cvv",
             "send us your password", "enter your password below", "confirm your card number",
             "your full card number", "seed phrase", "recovery phrase", "verify your card",
             "social security number", "confirm your bank details")
_HOSTISH = re.compile(r"\b(?:https?://)?((?:[a-z0-9-]+\.)+[a-z]{2,})", re.I)


def _host_ok(host: str) -> bool:
    if not host or "xn--" in host:
        return False
    try:
        ipaddress.ip_address(host)
        return False
    except ValueError:
        pass
    return not any(host == s or host.endswith("." + s) for s in _SHORTENERS)


def _same_site(shown: str, real: str) -> bool:
    return shown == real or real.endswith("." + shown) or shown.endswith("." + real)


class _EmailScan(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags, self.urls, self.anchors = set(), [], []
        self._href, self._text = None, []

    def handle_starttag(self, tag, attrs):
        self.tags.add(tag.lower())
        self.urls += [v for k, v in attrs if k.lower() in ("href", "src") and v]
        if tag.lower() == "a":
            self._href = dict((k.lower(), v) for k, v in attrs).get("href")
            self._text = []

    def handle_data(self, data):
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag.lower() == "a" and self._href is not None:
            self.anchors.append((self._href, "".join(self._text)))
            self._href, self._text = None, []


def _assert_safe_email(subject: str, html: str) -> None:
    scan = _EmailScan()
    scan.feed(html)
    if scan.tags & {"form", "input", "textarea", "select"}:
        raise ValueError("No forms or input fields in email (G2)")
    body = f"{subject}\n{html}".lower()
    for p in _CRED_ASK:
        if p in body:
            raise ValueError(f"Email asks the recipient for credentials: {p!r} (G2)")
    for url in scan.urls:
        low = url.strip().lower()
        if low.startswith(("mailto:", "tel:", "cid:", "#")):
            continue
        if not low.startswith("https://"):
            raise ValueError(f"Email links/assets must be absolute https: {url!r} (G3)")
        host = urlparse(low).hostname or ""
        if not _host_ok(host) or urlparse(low).username is not None:
            raise ValueError(f"Shortened, numeric-host or credential-bearing URL: {url!r} (G3)")
    for href, text in scan.anchors:
        real = urlparse(href.strip().lower()).hostname or ""
        if not real:
            continue
        for m in _HOSTISH.finditer(text):
            if not _same_site(m.group(1).lower(), real):
                raise ValueError(f"Anchor text {m.group(1)!r} ≠ real link host {real!r} (G3)")


async def send_email(*, to: str, subject: str, html: str, reply_to: Optional[str] = None) -> Optional[str]:
    _assert_safe_email(subject, html)
    payload = {"to": [to], "subject": subject, "html": html, "from_name": EMAIL_FROM_NAME}
    if reply_to:
        payload["contact_email"] = reply_to
    async with httpx.AsyncClient(timeout=30) as http_client:
        resp = await http_client.post(
            f"{EMAIL_BASE_URL}/api/v1/email/send",
            headers={"X-Email-Key": EMAIL_KEY},
            json=payload,
        )
    resp.raise_for_status()
    return resp.json().get("id")


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class InquiryCreate(BaseModel):
    product: str = Field(..., min_length=1, max_length=120)
    wish: str = Field(..., min_length=1, max_length=4000)
    email: EmailStr
    name: Optional[str] = Field(default=None, max_length=120)


class Inquiry(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    product: str
    wish: str
    email: str
    name: Optional[str] = None
    email_status: str = "pending"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# Email templates (server-side only)
# ---------------------------------------------------------------------------
def _owner_email_html(inq: Inquiry) -> str:
    name = escape(inq.name) if inq.name else "—"
    return (
        '<table role="presentation" width="100%" style="background:#0a0a0b;padding:24px">'
        '<tr><td style="font-family:Arial,Helvetica,sans-serif;color:#e6f7fa;max-width:600px">'
        f'<h2 style="color:#22d3ee;margin:0 0 16px">Neue Anfrage – {escape(EMAIL_FROM_NAME)}</h2>'
        '<table role="presentation" width="100%" style="border-collapse:collapse">'
        f'<tr><td style="padding:6px 0;color:#8aa0a6;width:140px">Produkt</td>'
        f'<td style="padding:6px 0;color:#e6f7fa"><strong>{escape(inq.product)}</strong></td></tr>'
        f'<tr><td style="padding:6px 0;color:#8aa0a6;vertical-align:top">Wunsch</td>'
        f'<td style="padding:6px 0;color:#e6f7fa">{escape(inq.wish)}</td></tr>'
        f'<tr><td style="padding:6px 0;color:#8aa0a6">Name</td>'
        f'<td style="padding:6px 0;color:#e6f7fa">{name}</td></tr>'
        f'<tr><td style="padding:6px 0;color:#8aa0a6">E-Mail</td>'
        f'<td style="padding:6px 0;color:#e6f7fa">{escape(inq.email)}</td></tr>'
        '</table>'
        '<p style="font-size:12px;color:#8aa0a6;margin-top:24px">Antworte direkt auf diese '
        'E-Mail, um der anfragenden Person zu antworten.</p>'
        '</td></tr></table>'
    )


def _confirmation_email_html(inq: Inquiry) -> str:
    greeting = f"Hallo {escape(inq.name)}," if inq.name else "Hallo,"
    return (
        '<table role="presentation" width="100%" style="background:#0a0a0b;padding:24px">'
        '<tr><td style="font-family:Arial,Helvetica,sans-serif;color:#e6f7fa;max-width:600px">'
        f'<h2 style="color:#22d3ee;margin:0 0 16px">{escape(EMAIL_FROM_NAME)}</h2>'
        f'<p style="margin:0 0 12px">{greeting}</p>'
        '<p style="margin:0 0 12px">vielen Dank für deine Anfrage. Wir haben sie erhalten und '
        'melden uns <strong>innert 24 h</strong> bei dir.</p>'
        '<p style="margin:0 0 6px;color:#8aa0a6">Deine Anfrage:</p>'
        '<table role="presentation" width="100%" style="border-collapse:collapse">'
        f'<tr><td style="padding:6px 0;color:#8aa0a6;width:120px">Produkt</td>'
        f'<td style="padding:6px 0;color:#e6f7fa"><strong>{escape(inq.product)}</strong></td></tr>'
        f'<tr><td style="padding:6px 0;color:#8aa0a6;vertical-align:top">Wunsch</td>'
        f'<td style="padding:6px 0;color:#e6f7fa">{escape(inq.wish)}</td></tr>'
        '</table>'
        '<p style="font-size:12px;color:#8aa0a6;margin-top:24px">Diese E-Mail wurde von '
        f'{escape(EMAIL_FROM_NAME)} gesendet. Wir fragen dich niemals per E-Mail nach '
        'Passwörtern oder Zahlungsdaten.</p>'
        '</td></tr></table>'
    )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@api_router.get("/")
async def root():
    return {"message": "Gravurwerk Schweiz API"}


@api_router.post("/inquiries")
async def create_inquiry(payload: InquiryCreate):
    inq = Inquiry(**payload.model_dump())

    doc = inq.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.inquiries.insert_one(doc)

    owner_sent = False
    customer_sent = False
    try:
        await send_email(
            to=OWNER_EMAIL,
            subject=f"Neue Anfrage: {inq.product}",
            html=_owner_email_html(inq),
            reply_to=inq.email,
        )
        owner_sent = True
    except Exception as e:
        logger.error(f"Owner email failed for inquiry {inq.id}: {e}")

    try:
        await send_email(
            to=inq.email,
            subject=f"Wir haben deine Anfrage erhalten – {EMAIL_FROM_NAME}",
            html=_confirmation_email_html(inq),
            reply_to=OWNER_EMAIL,
        )
        customer_sent = True
    except Exception as e:
        logger.error(f"Confirmation email failed for inquiry {inq.id}: {e}")

    status = "sent" if owner_sent else "failed"
    await db.inquiries.update_one({"id": inq.id}, {"$set": {"email_status": status}})

    if not owner_sent:
        raise HTTPException(
            status_code=502,
            detail="Deine Anfrage wurde gespeichert, aber der E-Mail-Versand ist "
                   "fehlgeschlagen. Bitte versuche es erneut oder schreib an "
                   f"{OWNER_EMAIL}.",
        )

    return {"status": "success", "id": inq.id, "confirmation_sent": customer_sent}


@api_router.get("/inquiries", response_model=List[Inquiry])
async def list_inquiries():
    rows = await db.inquiries.find({}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    for r in rows:
        if isinstance(r.get('created_at'), str):
            r['created_at'] = datetime.fromisoformat(r['created_at'])
    return rows


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
