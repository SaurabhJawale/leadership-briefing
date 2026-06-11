from datetime import date, datetime
from pathlib import Path
from typing import Any
import smtplib

import pandas as pd
import yagmail

from config import (
    cfg,
    logger,
    STATUS_COMPLETED,
    BLOCKER_KEYWORDS,
)

# ===========================================================================
# CONFIG & HELPERS
# ===========================================================================
TEMPLATE_FILE = Path("templates/report_template.html")

def load_css() -> str:
    """Return clean, compact, email-friendly inline CSS"""
    raw_css = """
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.5; color: #333; background-color: #f9f9f9; }
        .container { max-width: 1000px; margin: 0 auto; background-color: #ffffff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
        h1, h2 { color: #1e3a8a; margin-top: 10px; margin-bottom: 12px; }
        table { border-collapse: collapse; width: 100%; margin: 12px 0; }
        th, td { border: 1px solid #ddd; padding: 9px 12px; text-align: left; }
        th { background-color: #f2f2f2; font-weight: bold; }
        .delayed-row { background-color: #fff3e0; }
        .blocker-row { background-color: #ffebee; }
        .header { text-align: center; margin-bottom: 25px; padding-bottom: 15px; border-bottom: 2px solid #eee; }
        .summary-box, .action-box, .recommendation-box { background-color: #f8fafc; padding: 16px; border-radius: 6px; margin: 15px 0; border-left: 4px solid #1e3a8a; }
        .highlight { background-color: #e0f2fe; padding: 10px; border-radius: 4px; }
        p { margin: 8px 0; }
        ul, ol { margin: 10px 0; padding-left: 20px; }
        hr { margin: 25px 0; border: 0; border-top: 1px solid #eee; }
    """
    
    # CRITICAL FIX: Remove all newlines so yagmail doesn't convert them to <br> tags
    return raw_css.replace('\n', ' ')

def load_html_template() -> str:
    try:
        return TEMPLATE_FILE.read_text(encoding="utf-8")
    except FileNotFoundError:
        logger.error("HTML template not found: %s", TEMPLATE_FILE)
        raise

# ===========================================================================
# DATA LOADING & PROCESSING
# ===========================================================================
def load_excel_data(file_path: str | Path) -> pd.DataFrame:
    file_path = Path(file_path)
    logger.info("Loading Excel data from: %s", file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"Excel file not found: {file_path}")

    df = pd.read_excel(
        file_path,
        sheet_name="Employee Tasks",
        header=2,
        engine="openpyxl"
    )
    df.columns = df.columns.str.strip()
    df.dropna(how="all", inplace=True)
    return df

def validate_and_clean(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Starting data validation and cleaning …")
    original_count = len(df)

    str_cols = df.select_dtypes(include="object").columns
    for col in str_cols:
        df[col] = df[col].astype(str).str.strip()

    df.replace("nan", "", inplace=True)
    df["Status"] = df["Status"].str.lower()
    df["Due Date"] = pd.to_datetime(df["Due Date"], errors="coerce").dt.date
    df["Comments"] = df["Comments"].fillna("").astype(str)

    critical_fields = ["Employee", "Task", "Status"]
    df.dropna(subset=critical_fields, inplace=True)
    df = df[df[critical_fields].apply(lambda col: col.str.strip() != "").all(axis=1)]

    logger.info("Cleaning complete. %d/%d rows retained.", len(df), original_count)
    return df.reset_index(drop=True)

def apply_business_rules(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Applying business rules …")
    today = date.today()

    df["is_completed"] = df["Status"].str.lower() == STATUS_COMPLETED
    df["is_delayed"] = (
        df["Due Date"].apply(lambda d: d < today if pd.notna(d) else False)
        & ~df["is_completed"]
    )
    df["is_blocker"] = df["Comments"].apply(
        lambda c: any(kw in str(c).lower() for kw in BLOCKER_KEYWORDS)
    )
    df["is_in_progress"] = ~df["is_completed"] & ~df["is_delayed"]
    return df

def compute_metrics(df: pd.DataFrame) -> dict[str, Any]:
    total = len(df)
    completed = int(df["is_completed"].sum())
    delayed = int(df["is_delayed"].sum())
    blocked = int(df["is_blocker"].sum())
    in_progress = int(df["is_in_progress"].sum())
    completion_rate = round((completed / total * 100), 1) if total else 0.0

    top_contributors = (
        df[df["is_completed"]]
        .groupby("Employee")
        .size()
        .sort_values(ascending=False)
        .head(5)
        .reset_index(name="completed_tasks")
        .to_dict(orient="records")
    )

    delayed_details = df[df["is_delayed"]][["Employee", "Project", "Task", "Due Date", "Status"]].to_dict(orient="records")
    blocker_details = df[df["is_blocker"]][["Employee", "Project", "Task", "Comments"]].to_dict(orient="records")

    return {
        "total_tasks": total,
        "completed_tasks": completed,
        "in_progress_tasks": in_progress,
        "delayed_tasks": delayed,
        "blocked_tasks": blocked,
        "completion_rate": completion_rate,
        "top_contributors": top_contributors,
        "delayed_details": delayed_details,
        "blocker_details": blocker_details,
    }

# ===========================================================================
# HTML REPORT BUILDER
# ===========================================================================
def build_html_report(
    metrics: dict,
    executive_summary: str,
    manager_actions_html: str,
    recommendations_html: str,
) -> str:
    
    template = load_html_template()
    css = load_css()

    # Build tables
    top_contributors_table = "".join(
        f"<tr><td>{c.get('Employee', '')}</td><td>{c.get('completed_tasks', 0)}</td></tr>"
        for c in metrics.get("top_contributors", [])
    )

    delayed_tasks_table = "".join(
        f"<tr class='delayed-row'>"
        f"<td>{t.get('Employee', '')}</td>"
        f"<td>{t.get('Task', '')}</td>"
        f"<td>{t.get('Project', '')}</td>"
        f"<td>{t.get('Due Date', '')}</td>"
        f"<td>{t.get('Status', '')}</td></tr>"
        for t in metrics.get("delayed_details", [])
    )

    blockers_table = "".join(
        f"<tr class='blocker-row'>"
        f"<td>{b.get('Employee', '')}</td>"
        f"<td>{b.get('Task', '')}</td>"
        f"<td>{b.get('Comments', '')}</td>"
        f"<td>Delivery Impact</td></tr>"
        for b in metrics.get("blocker_details", [])
    )

    rate = metrics.get("completion_rate", 0)
    team_health = "🟢 Healthy" if rate >= 70 else "🟡 Moderate Risk" if rate >= 40 else "🔴 High Risk"

    html_report = (
        template
        .replace("{{css}}", css)
        .replace("{{report_date}}", date.today().strftime("%Y-%m-%d"))
        .replace("{{team_health}}", team_health)
        .replace("{{executive_summary}}", executive_summary)
        .replace("{{total_tasks}}", str(metrics.get("total_tasks", 0)))
        .replace("{{completed_tasks}}", str(metrics.get("completed_tasks", 0)))
        .replace("{{in_progress_tasks}}", str(metrics.get("in_progress_tasks", 0)))
        .replace("{{delayed_tasks}}", str(metrics.get("delayed_tasks", 0)))
        .replace("{{blocked_tasks}}", str(metrics.get("blocked_tasks", 0)))
        .replace("{{completion_rate}}", str(rate))
        .replace("{{top_contributors_table}}", top_contributors_table)
        .replace("{{delayed_tasks_table}}", delayed_tasks_table)
        .replace("{{blockers_table}}", blockers_table)
        .replace("{{manager_actions}}", manager_actions_html)
        .replace("{{recommendations}}", recommendations_html)
        .replace("{{generated_timestamp}}", datetime.now().strftime("%d-%m-%Y %I:%M %p"))
    )

    return html_report

# ===========================================================================
# EMAIL SENDING
# ===========================================================================
def send_email_report(report_path: Path, html_content: str) -> None:
    sender_email = cfg.sender_email
    sender_pwd = cfg.sender_app_password
    manager_email = cfg.manager_email

    if not all([sender_email, sender_pwd, manager_email]):
        logger.warning("Email credentials missing. Skipping email.")
        return

    subject = f"📊 Daily Work Tracking Report – {date.today().strftime('%B %d, %Y')}"

    try:
        logger.info("Sending report email to %s …", manager_email)
        yag = yagmail.SMTP(sender_email, sender_pwd)

        safe_html_content = html_content.replace('\n', '')
        yag.send(
            to=manager_email,
            subject=subject,
            contents=[safe_html_content, str(report_path)]
        )
        logger.info("Email delivered successfully to %s.", manager_email)
    except smtplib.SMTPAuthenticationError:
        logger.error("SMTP authentication failed. Check credentials.")
    except Exception as exc:
        logger.error("Failed to send email: %s", exc)

# ===========================================================================
# MAIN PIPELINE
# ===========================================================================
def run_pipeline() -> None:
    logger.info("Employee Work Tracking Agent – Pipeline START")
    cfg.validate(strict=False)

    # 1. Load & Process Data
    raw_df = load_excel_data(cfg.excel_file_path)
    clean_df = validate_and_clean(raw_df)
    enriched_df = apply_business_rules(clean_df)
    metrics = compute_metrics(enriched_df)

    # 2. Prepare content for template
    executive_summary = f"The team completed <strong>{metrics['completed_tasks']}</strong> out of <strong>{metrics['total_tasks']}</strong> tasks today with a completion rate of <strong>{metrics['completion_rate']}%</strong>."
    
    manager_actions_html = """
        <ol>
            <li>Immediately review and resolve all <strong>blockers</strong>.</li>
            <li>Follow up with employees having delayed tasks.</li>
            <li>Acknowledge and motivate top contributors.</li>
        </ol>
    """
    
    recommendations_html = """
        <ul>
            <li>Prioritize unblocking critical tasks to improve velocity.</li>
            <li>Consider resource reallocation for delayed projects.</li>
            <li>Recognize high performers to maintain team morale.</li>
        </ul>
    """

    # 3. Build Final HTML Report
    html_report = build_html_report(
        metrics=metrics,
        executive_summary=executive_summary,
        manager_actions_html=manager_actions_html,
        recommendations_html=recommendations_html,
    )

    # 4. Save Report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = cfg.REPORTS_DIR / f"manager_report_{timestamp}.html"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(html_report, encoding="utf-8")
    logger.info("Report saved: %s", report_path)

    # 5. Send Email
    send_email_report(report_path, html_report)

    logger.info("Pipeline completed successfully.")

if __name__ == "__main__":
    run_pipeline()
