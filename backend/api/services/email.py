"""
Email notification service using Resend (free tier: 3,000 emails/month).
https://resend.com/docs/api-reference/emails/send-email

Usage:
    from backend.services.email import send_report_email, send_admin_alert
    await send_report_email(to="user@example.com", token="abc123", roi_score=87)
"""
import os
import httpx
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "IndiaLens <reports@indialens.in>")
APP_URL = os.getenv("FRONTEND_URL", "https://indialens.in")


def _is_configured() -> bool:
    return bool(RESEND_API_KEY)


async def send_report_email(
    to: str,
    token: str,
    roi_score: int,
    college_name: str = "",
    degree_name: str = "",
    top_recommendation: str = "",
) -> bool:
    """
    Sends the shareable report link after an analysis completes.
    Returns True if sent successfully, False otherwise (non-blocking).
    """
    if not _is_configured():
        logger.info("RESEND_API_KEY not set — skipping email (non-critical)")
        return False

    report_url = f"{APP_URL}/report/{token}"
    
    subject = f"Your IndiaLens ROI Report — Score: {roi_score}/100"
    if college_name and degree_name:
        subject = f"{college_name} {degree_name} — ROI Score {roi_score}/100 | IndiaLens"

    html_body = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{subject}</title>
</head>
<body style="margin:0;padding:0;background:#0A0A12;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <div style="max-width:600px;margin:0 auto;padding:40px 20px;">
    <!-- Header -->
    <div style="text-align:center;margin-bottom:40px;">
      <div style="display:inline-block;background:linear-gradient(135deg,#4F6EF7,#7C3AED);padding:12px 24px;border-radius:8px;">
        <span style="color:#fff;font-size:20px;font-weight:700;letter-spacing:-0.5px;">IndiaLens</span>
      </div>
      <p style="color:#6B7280;font-size:13px;margin-top:12px;">India's Degree ROI Index</p>
    </div>
    
    <!-- Score Card -->
    <div style="background:#13131F;border:1px solid #1E1E2E;border-radius:16px;padding:32px;text-align:center;margin-bottom:24px;">
      <p style="color:#9CA3AF;font-size:13px;text-transform:uppercase;letter-spacing:1px;margin:0 0 8px;">Your ROI Score</p>
      <div style="font-size:72px;font-weight:800;color:#4F6EF7;line-height:1;margin:8px 0;">{roi_score}</div>
      <p style="color:#6B7280;font-size:13px;margin:8px 0 0;">/100 composite score</p>
      {f'<p style="color:#E5E7EB;font-size:16px;margin:16px 0 0;font-weight:600;">{college_name} — {degree_name}</p>' if college_name else ''}
    </div>
    
    <!-- CTA -->
    <div style="text-align:center;margin-bottom:32px;">
      <a href="{report_url}" 
         style="display:inline-block;background:linear-gradient(135deg,#4F6EF7,#7C3AED);
                color:#fff;text-decoration:none;padding:16px 32px;border-radius:8px;
                font-weight:600;font-size:16px;letter-spacing:-0.3px;">
        View Full Report →
      </a>
      <p style="color:#4B5563;font-size:12px;margin-top:12px;">
        This link expires in 90 days · <a href="{report_url}" style="color:#4F6EF7;">{report_url}</a>
      </p>
    </div>
    
    {f'''
    <!-- Recommendation -->
    <div style="background:#13131F;border:1px solid #1E1E2E;border-left:3px solid #22C55E;border-radius:8px;padding:20px;margin-bottom:24px;">
      <p style="color:#22C55E;font-size:12px;text-transform:uppercase;letter-spacing:1px;margin:0 0 8px;">Top Insight</p>
      <p style="color:#E5E7EB;font-size:14px;margin:0;line-height:1.6;">{top_recommendation}</p>
    </div>
    ''' if top_recommendation else ''}
    
    <!-- Footer -->
    <div style="text-align:center;border-top:1px solid #1E1E2E;padding-top:24px;">
      <p style="color:#4B5563;font-size:12px;line-height:1.8;margin:0;">
        IndiaLens · India's first quantitative education ROI platform<br>
        Data updated weekly · Methodology at <a href="{APP_URL}/methodology" style="color:#4F6EF7;">indialens.in/methodology</a><br>
        <a href="{APP_URL}" style="color:#4B5563;">indialens.in</a>
      </p>
    </div>
  </div>
</body>
</html>
"""

    text_body = f"""
Your IndiaLens ROI Report

ROI Score: {roi_score}/100
{f'Program: {college_name} — {degree_name}' if college_name else ''}

View your full report: {report_url}

This link expires in 90 days.

---
IndiaLens · indialens.in
Data methodology: {APP_URL}/methodology
"""

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
                json={
                    "from": FROM_EMAIL,
                    "to": [to],
                    "subject": subject,
                    "html": html_body,
                    "text": text_body,
                },
            )
            if response.status_code == 200:
                email_id = response.json().get("id", "unknown")
                logger.info(f"Report email sent to {to} (id={email_id})")
                return True
            else:
                logger.warning(f"Resend API returned {response.status_code}: {response.text}")
                return False
    except Exception as e:
        logger.warning(f"Failed to send report email to {to}: {e} (non-critical)")
        return False


async def send_admin_alert(
    subject: str,
    message: str,
    severity: str = "warning",
) -> bool:
    """
    Sends an admin alert email. Used for scraper failures, anomalies, etc.
    """
    admin_email = os.getenv("ADMIN_EMAIL", "")
    if not _is_configured() or not admin_email:
        logger.debug("Admin email not configured — skipping alert")
        return False

    severity_color = {
        "critical": "#EF4444",
        "warning": "#F59E0B",
        "info": "#4F6EF7",
    }.get(severity, "#F59E0B")

    html_body = f"""
<!DOCTYPE html>
<html>
<body style="background:#0A0A12;font-family:monospace;padding:40px;">
  <div style="max-width:600px;margin:0 auto;">
    <div style="background:{severity_color};color:#fff;padding:8px 16px;border-radius:6px 6px 0 0;font-size:12px;text-transform:uppercase;letter-spacing:1px;">
      IndiaLens Alert · {severity.upper()} · {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}
    </div>
    <div style="background:#13131F;border:1px solid {severity_color};border-top:0;border-radius:0 0 6px 6px;padding:24px;">
      <h2 style="color:#E5E7EB;margin:0 0 16px;">{subject}</h2>
      <pre style="color:#9CA3AF;font-size:13px;white-space:pre-wrap;background:#0A0A12;padding:16px;border-radius:6px;">{message}</pre>
      <p style="color:#4B5563;font-size:12px;margin:16px 0 0;">
        Admin panel: <a href="{APP_URL}/admin" style="color:#4F6EF7;">{APP_URL}/admin</a>
      </p>
    </div>
  </div>
</body>
</html>
"""

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
                json={
                    "from": FROM_EMAIL,
                    "to": [admin_email],
                    "subject": f"[IndiaLens {severity.upper()}] {subject}",
                    "html": html_body,
                },
            )
            return response.status_code == 200
    except Exception as e:
        logger.warning(f"Failed to send admin alert: {e}")
        return False
