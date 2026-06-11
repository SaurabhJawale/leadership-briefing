# Leadership Briefing

AI-powered reporting platform that transforms employee work data into leadership-ready briefings, actionable insights, blocker alerts, and progress summaries.

## Overview

Leadership Briefing helps managers and business leaders gain visibility into team activities without manually collecting status updates.

The platform automatically ingests work data from Excel, analyzes task progress, identifies risks and blockers, generates executive summaries, and delivers professional reports via email.

## Key Features

* Automated Excel data ingestion
* AI-powered work analysis and summarization
* Blocker and risk detection
* Team progress tracking
* Executive-ready daily reports
* Automated email distribution
* Audit and execution logging
* Configurable business rules

## Use Cases

* Daily manager reporting
* Team status reviews
* Project progress monitoring
* Leadership updates
* Risk and blocker identification
* Operational reporting

## Workflow

Excel Data
→ Data Validation
→ Business Rules Engine
→ AI Analysis
→ Report Generation
→ Email Distribution

## Technology Stack

* Python
* Pandas
* OpenAI / Gemini
* SMTP Email
* Logging Framework
* OpenPyXL

## Project Structure

```text
src/
├── main.py
├── excel_reader.py
├── data_validator.py
├── business_rules.py
├── llm_analyzer.py
├── report_generator.py
└── email_sender.py
```

## Getting Started

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_api_key

SMTP_EMAIL=your_email

SMTP_PASSWORD=your_password

MANAGER_EMAIL=manager_email
```

### Run Application

```bash
python src/main.py
```

## Sample Output

The system generates leadership-ready reports containing:

* Executive Summary
* Team Performance Metrics
* Task Completion Status
* Delayed Activities
* Blocker Analysis
* Recommended Actions
* AI-Generated Insights

## Future Enhancements

* Jira Integration
* CRM Integration
* Microsoft Teams Integration
* Slack Integration
* Web Dashboard
* Trend Analytics
* Weekly and Monthly Briefings
* Multi-Team Reporting

