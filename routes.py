import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from .models import db, User, Setting, WatchlistItem, PortfolioHolding
from .security import encrypt_secret, decrypt_secret, mask_secret
from .providers import UpstoxClient, demo_market_snapshot, ProviderError

main = Blueprint("main", __name__)

ALLOWED_SETTINGS = {"gemini_api_key","groq_api_key","upstox_access_token"}

@main.get("/")
def index():
    if not current_user.is_authenticated:
        return redirect(url_for("main.login"))
    return render_template("dashboard.html", user=current_user)

@main.route("/setup", methods=["GET","POST"])
def setup():
    if User.query.first():
        return redirect(url_for("main.login"))
    if request.method == "POST":
        name = request.form.get("name","").strip()
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        if not name or not email or len(password) < 12:
            flash("Enter your name and email. Password must be at least 12 characters.", "error")
        else:
            user = User(display_name=name, email=email,
                        password_hash=generate_password_hash(password), role="owner")
            db.session.add(user); db.session.commit()
            login_user(user)
            return redirect(url_for("main.index"))
    return render_template("auth.html", mode="setup")

@main.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, request.form.get("password","")):
            login_user(user)
            return redirect(url_for("main.index"))
        flash("Email or password is incorrect.", "error")
    return render_template("auth.html", mode="login")

@main.post("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.login"))

@main.get("/api/me")
@login_required
def me():
    return jsonify(name=current_user.display_name, email=current_user.email, role=current_user.role)

@main.get("/api/settings")
@login_required
def get_settings():
    values = {}
    for row in Setting.query.filter_by(user_id=current_user.id).all():
        try: raw = decrypt_secret(row.encrypted_value)
        except Exception: raw = ""
        values[row.key] = {"configured": bool(raw), "masked": mask_secret(raw)}
    return jsonify(settings=values)

@main.post("/api/settings")
@login_required
def save_settings():
    payload = request.get_json(silent=True) or {}
    key = payload.get("key")
    value = payload.get("value","").strip()
    if key not in ALLOWED_SETTINGS:
        return jsonify(ok=False, error="Unsupported setting."), 400
    if not value:
        return jsonify(ok=False, error="Enter a value, or use Disconnect to remove it."), 400
    try:
        encrypted = encrypt_secret(value)
    except RuntimeError as exc:
        return jsonify(ok=False, error=str(exc)), 503
    row = Setting.query.filter_by(user_id=current_user.id, key=key).first()
    if not row:
        row = Setting(user_id=current_user.id, key=key)
        db.session.add(row)
    row.encrypted_value = encrypted
    db.session.commit()
    return jsonify(ok=True, message="Credential encrypted and saved.")

@main.delete("/api/settings/<key>")
@login_required
def delete_setting(key):
    if key not in ALLOWED_SETTINGS:
        return jsonify(ok=False, error="Unsupported setting."), 400
    Setting.query.filter_by(user_id=current_user.id, key=key).delete()
    db.session.commit()
    return jsonify(ok=True)

def user_secret(key):
    row = Setting.query.filter_by(user_id=current_user.id, key=key).first()
    return decrypt_secret(row.encrypted_value) if row else ""

@main.post("/api/connections/upstox/test")
@login_required
def test_upstox():
    token = user_secret("upstox_access_token")
    if not token:
        return jsonify(ok=False, error="Save your Upstox access token first."), 400
    try:
        profile = UpstoxClient(token).profile()
        return jsonify(ok=True, account=profile.get("user_name") or profile.get("email") or "Connected")
    except Exception as exc:
        return jsonify(ok=False, error=str(exc)), 502

@main.get("/api/dashboard")
@login_required
def dashboard_data():
    demo = os.getenv("APP_MODE","demo").lower() == "demo"
    holdings = PortfolioHolding.query.filter_by(user_id=current_user.id).all()
    watchlist = WatchlistItem.query.filter_by(user_id=current_user.id).all()
    return jsonify(mode="DEMO — sample prices, not live market data" if demo else "LIVE MODE",
                   snapshot=demo_market_snapshot() if demo else [],
                   holdings=[{"broker":h.broker,"symbol":h.symbol,"quantity":h.quantity,
                              "average_price":h.average_price} for h in holdings],
                   watchlist=[{"symbol":w.symbol,"exchange":w.exchange} for w in watchlist])

@main.get("/settings")
@login_required
def settings_page():
    return render_template("settings.html", user=current_user)

@main.post("/api/watchlist")
@login_required
def add_watchlist():
    payload=request.get_json(silent=True) or {}
    symbol=str(payload.get("symbol","")).upper().strip()
    if not symbol or len(symbol)>40:
        return jsonify(ok=False,error="Enter a valid symbol."),400
    exists=WatchlistItem.query.filter_by(user_id=current_user.id,symbol=symbol,exchange="NSE").first()
    if not exists:
        db.session.add(WatchlistItem(user_id=current_user.id,symbol=symbol,exchange="NSE"))
        db.session.commit()
    return jsonify(ok=True)

@main.delete("/api/watchlist/<symbol>")
@login_required
def remove_watchlist(symbol):
    WatchlistItem.query.filter_by(user_id=current_user.id,symbol=symbol.upper()).delete()
    db.session.commit()
    return jsonify(ok=True)
