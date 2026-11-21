# Swing Desk — clean foundation

This is a new codebase, independent of the earlier V3 files. It is an initial foundation, not yet the complete V3.1 product.

## Included now
- Flask web application with responsive dashboard and settings pages
- First-owner account setup and login
- User-scoped settings, watchlists and portfolio-holding tables
- Server-side encrypted storage for Gemini, Groq and Upstox credentials
- Upstox profile connection test
- Clearly labelled demo market snapshot (not live market data)
- Basic deployment entrypoint for Gunicorn

## Not implemented yet
Nifty 500/ETF scanning, technical/fundamental/news scoring pipeline, LLM research agents, Kite OAuth, Upstox portfolio sync, family invitations/roles, backtesting engine, alerts, journal, multi-user production hardening and cloud deployment configuration.

## Local run
1. Install Python 3.11+.
2. Create a virtual environment and install dependencies:
   `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
3. Create `.env` from `.env.example`.
4. Generate secrets:
   `python -c "import secrets; print(secrets.token_urlsafe(48))"`
   `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
   Put the first value in `SECRET_KEY` and the second in `CREDENTIAL_ENCRYPTION_KEY`.
5. Run:
   `flask --app wsgi run --debug`
6. Open `http://127.0.0.1:5000/setup` to create the first owner account.

## Important
- Never commit `.env` or share API keys in chat.
- Do not deploy with the example development secret.
- Set `COOKIE_SECURE=1` behind HTTPS in production.
- Back up the encryption key securely. If it is lost, stored credentials cannot be decrypted.
- The demo snapshot is static sample data. Do not use it for trading decisions.
- The first-account setup route is intended for initial bootstrap. Before public deployment, disable it after creating the owner and implement invitation-only family onboarding, CSRF protection, rate limits, audit logging, password reset and database migrations.
- Broker API terms, market-data licensing and Indian financial-services regulatory requirements must be reviewed before external commercialization.
