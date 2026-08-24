# Setup guide

## 1. Create the Notion integration

Create an internal integration in Notion, copy its secret, and share both the Inventory and Sales databases with it. The integration only needs access to the pages used by this project.

## 2. Find the database IDs

Open each database as a full page. Its database ID appears in the URL. Store it in `.env`; do not add it directly to Python files.

## 3. Configure the project

```bash
python -m venv .venv
```

Activate the environment, then run:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and complete all three values.

## 4. Run locally

```bash
streamlit run app.py
```

## 5. Validate

Confirm the dashboard loads all 11 headline metrics plus the Sales Data Used for Profit and Inventory Overview tables. If it cannot load, verify that the token is current, the database IDs are correct, and both databases have been explicitly shared with the integration.

## Security

- Never commit `.env` or paste the integration secret into an issue.
- Give the integration the minimum necessary permissions.
- Rotate the token immediately if it is exposed.
- Use deployment-platform secrets rather than hard-coded credentials.
