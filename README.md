# Internship Bot

This project wires a Google Sheets backend to a FastAPI service so that every job
application attempt is recorded with detailed metadata, confirmation IDs and the
materials that were uploaded. A lightweight dashboard and API make it easy to
review the submission history and guard against duplicate applications.

## Spreadsheet backend

Google Sheets is used as the source of truth because it is collaborative and can
be shared without granting access to infrastructure. The sheet needs the
following columns (the app will seed them automatically):

| Column | Purpose |
| --- | --- |
| `Application ID` | Deterministic hash of company + role + job URL. Used to prevent duplicates. |
| `Company` | Employer name. |
| `Role` | Title/position. |
| `Location` | City/state/remote descriptor. |
| `Job Post URL` | Link to the job posting. |
| `Source` | Where the job was found (LinkedIn, referral, etc.). |
| `Status` | Current status (Draft, Applied, Interviewing, Offer, Rejected). |
| `Last Attempt Outcome` | `Success`, `Failure`, or context for the latest attempt. |
| `Attempt Timestamp` | UTC timestamp of the most recent attempt. |
| `Next Follow Up` | Planned follow-up date. |
| `Confirmation ID` | Tracking ID returned by the ATS. |
| `Uploaded Materials` | Filenames or share links submitted with the application. |
| `Notes` | Freeform notes (recruiter feedback, interview prep). |
| `Created At` | When the job was first tracked. |
| `Updated At` | When the row was last edited. |

Each application attempt is logged with:

* success/failure context in `Last Attempt Outcome`
* ATS confirmation number in `Confirmation ID`
* resume/cover letter links in `Uploaded Materials`

## Running the API/dashboard

1. Create a Google Cloud service account with access to the spreadsheet and
   download the credentials JSON file.
2. Share the spreadsheet with the service account email.
3. Export the required environment variables:

```bash
export SHEETS_SPREADSHEET_ID="<spreadsheet-id>"
export SHEETS_WORKSHEET="applications"          # optional
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

4. Install dependencies and start the server:

```bash
pip install -r requirements.txt
uvicorn internship_bot.api:app --reload
```

### API endpoints

* `GET /applications` – list all logged applications
* `POST /applications` – log a new attempt (409 if duplicate exists)
* `POST /applications/upsert` – log or update an attempt in one call
* `POST /applications/duplicates` – check whether an attempt already exists
* `GET /dashboard` – HTML table summarizing the application history

These endpoints expose confirmation IDs, uploaded material references and all
timestamps so you can filter or build additional automation downstream.

## Avoiding duplicate applications

The deterministic `Application ID` is computed from the company, role and job
posting URL. Before saving a new attempt the API searches for the same hash.
Duplicates return an HTTP 409 response that includes the clashing rows and the
existing confirmation IDs/materials, helping prevent multiple submissions to the
same requisition.
