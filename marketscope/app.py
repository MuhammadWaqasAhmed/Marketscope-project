import random
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

import config
from database import get_db, init_db, country_lookup
from adapters import aggregate_search, live_status

app = Flask(__name__)
app.config["SECRET_KEY"] = config.SECRET_KEY

COUNTRIES = country_lookup()


def login_required(view):
    @wraps(view)
    def wrapped(*a, **kw):
        if not session.get("user_id"):
            return redirect(url_for("login", next=request.path))
        return view(*a, **kw)
    return wrapped


def influencer_login_required(view):
    @wraps(view)
    def wrapped(*a, **kw):
        if not session.get("influencer_id"):
            return redirect(url_for("influencer_login"))
        return view(*a, **kw)
    return wrapped


# ---------------------------------------------------------------- pages ----

@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        company = request.form.get("company", "").strip()
        conn = get_db()
        existing = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
        if existing:
            conn.close()
            return render_template("register.html", error="An account with that email already exists.")
        conn.execute(
            "INSERT INTO users (name, email, password_hash, company, created_at) VALUES (?,?,?,?,?)",
            (name, email, generate_password_hash(password), company, datetime.utcnow().isoformat()),
        )
        conn.commit()
        user = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()
        conn.close()
        session["user_id"] = user["id"]
        session["user_name"] = name
        return redirect(url_for("dashboard"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()
        if not user or not check_password_hash(user["password_hash"], password):
            return render_template("login.html", error="Incorrect email or password.")
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        return redirect(url_for("dashboard"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user_name=session.get("user_name"),
                            live=live_status())


# ----------------------------------------------------------- influencer ----

@app.route("/influencer/login", methods=["GET", "POST"])
def influencer_login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        conn = get_db()
        inf = conn.execute("SELECT * FROM influencers WHERE email=?", (email,)).fetchone()
        conn.close()
        if not inf or not check_password_hash(inf["password_hash"], password):
            return render_template("influencer_login.html", error="Incorrect email or password.")
        session["influencer_id"] = inf["id"]
        session["influencer_name"] = inf["name"]
        return redirect(url_for("influencer_connect"))
    return render_template("influencer_login.html")


@app.route("/influencer/register", methods=["GET", "POST"])
def influencer_register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        platform = request.form.get("primary_platform", "")
        handle = request.form.get("handle", "")
        followers = int(request.form.get("followers") or 0)
        niche = request.form.get("niche", "")
        conn = get_db()
        existing = conn.execute("SELECT id FROM influencers WHERE email=?", (email,)).fetchone()
        if existing:
            conn.close()
            return render_template("influencer_register.html", error="An account with that email already exists.")
        conn.execute(
            """INSERT INTO influencers (name, email, password_hash, primary_platform, handle,
               followers, niche, created_at) VALUES (?,?,?,?,?,?,?,?)""",
            (name, email, generate_password_hash(password), platform, handle, followers, niche,
             datetime.utcnow().isoformat()),
        )
        conn.commit()
        inf = conn.execute("SELECT id FROM influencers WHERE email=?", (email,)).fetchone()
        conn.close()
        session["influencer_id"] = inf["id"]
        session["influencer_name"] = name
        return redirect(url_for("influencer_connect"))
    return render_template("influencer_register.html")


@app.route("/influencer/logout")
def influencer_logout():
    session.pop("influencer_id", None)
    session.pop("influencer_name", None)
    return redirect(url_for("influencer_login"))


@app.route("/influencer/connect", methods=["GET", "POST"])
@influencer_login_required
def influencer_connect():
    conn = get_db()
    if request.method == "POST":
        platform = request.form["platform"]
        handle = request.form["handle"].strip()
        automation_goal = request.form.get("automation_goal", "")
        posting_frequency = request.form.get("posting_frequency", "")
        ai_tone = request.form.get("ai_tone", "")
        auto_publish = 1 if request.form.get("auto_publish") == "on" else 0
        conn.execute(
            """INSERT INTO influencer_connections
               (influencer_id, platform, handle, automation_goal, posting_frequency,
                ai_tone, auto_publish, status, created_at)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (session["influencer_id"], platform, handle, automation_goal, posting_frequency,
             ai_tone, auto_publish, "connected", datetime.utcnow().isoformat()),
        )
        conn.commit()

    connections = conn.execute(
        "SELECT * FROM influencer_connections WHERE influencer_id=? ORDER BY id DESC",
        (session["influencer_id"],),
    ).fetchall()
    conn.close()
    return render_template("influencer_connect.html",
                            influencer_name=session.get("influencer_name"),
                            connections=connections)


@app.route("/api/influencer/connections/<int:conn_id>/delete", methods=["POST"])
@influencer_login_required
def delete_connection(conn_id):
    conn = get_db()
    conn.execute("DELETE FROM influencer_connections WHERE id=? AND influencer_id=?",
                 (conn_id, session["influencer_id"]))
    conn.commit()
    conn.close()
    return jsonify({"ok": True})


# ------------------------------------------------------------------ API ----

@app.route("/api/search")
@login_required
def api_search():
    q = request.args.get("q", "").strip()
    marketplace = request.args.get("marketplace", "")
    country = request.args.get("country", "")
    sort = request.args.get("sort", "trend")

    results = aggregate_search(q, per_source_limit=40) if q else aggregate_search("", per_source_limit=12)
    if not q:
        # default view: top trending across everything
        conn = get_db()
        rows = conn.execute("SELECT * FROM products ORDER BY trend_score DESC LIMIT 60").fetchall()
        conn.close()
        results = [dict(r) for r in rows]

    if marketplace:
        results = [r for r in results if r["marketplace"] == marketplace]
    if country:
        results = [r for r in results if r["country_code"] == country]

    if sort == "price_asc":
        results.sort(key=lambda r: r["price"])
    elif sort == "price_desc":
        results.sort(key=lambda r: r["price"], reverse=True)
    elif sort == "rating":
        results.sort(key=lambda r: r["rating"], reverse=True)
    elif sort == "sales":
        results.sort(key=lambda r: r["units_sold_30d"], reverse=True)
    else:
        results.sort(key=lambda r: r["trend_score"], reverse=True)

    for r in results:
        r["country_name"] = COUNTRIES.get(r["country_code"], {}).get("name", r["country_code"])

    conn = get_db()
    conn.execute("INSERT INTO search_log (user_id, query, result_count, created_at) VALUES (?,?,?,?)",
                 (session["user_id"], q, len(results), datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()

    return jsonify({
        "query": q,
        "count": len(results),
        "results": results[:60],
        "live_status": live_status(),
    })


@app.route("/api/countries")
@login_required
def api_countries():
    """Aggregate live country-level performance for the world map."""
    conn = get_db()
    rows = conn.execute(
        """SELECT country_code,
                  COUNT(*) AS listing_count,
                  AVG(trend_score) AS avg_trend,
                  AVG(rating) AS avg_rating,
                  SUM(units_sold_30d) AS total_sales
           FROM products GROUP BY country_code"""
    ).fetchall()
    conn.close()

    out = []
    for r in rows:
        info = COUNTRIES.get(r["country_code"])
        if not info:
            continue
        # small live jitter so the map visibly breathes between polls
        jitter = random.uniform(-3, 3)
        out.append({
            "code": r["country_code"],
            "name": info["name"],
            "lat": info["lat"],
            "lng": info["lng"],
            "listing_count": r["listing_count"],
            "trend_score": round(max(0, min(100, r["avg_trend"] + jitter)), 1),
            "avg_rating": round(r["avg_rating"], 2),
            "total_sales": int(r["total_sales"] * random.uniform(0.98, 1.03)),
        })
    out.sort(key=lambda c: c["trend_score"], reverse=True)
    return jsonify({"countries": out, "updated_at": datetime.utcnow().isoformat()})


@app.route("/api/trending")
@login_required
def api_trending():
    conn = get_db()
    rows = conn.execute("SELECT * FROM products ORDER BY trend_score DESC LIMIT 8").fetchall()
    conn.close()
    results = [dict(r) for r in rows]
    for r in results:
        r["country_name"] = COUNTRIES.get(r["country_code"], {}).get("name", r["country_code"])
    return jsonify({"results": results})


@app.route("/api/stats")
@login_required
def api_stats():
    conn = get_db()
    total_products = conn.execute("SELECT COUNT(*) c FROM products").fetchone()["c"]
    avg_trend = conn.execute("SELECT AVG(trend_score) a FROM products").fetchone()["a"]
    total_sales = conn.execute("SELECT SUM(units_sold_30d) s FROM products").fetchone()["s"]
    active_countries = conn.execute("SELECT COUNT(DISTINCT country_code) c FROM products").fetchone()["c"]
    conn.close()
    return jsonify({
        "total_products": total_products,
        "avg_trend": round(avg_trend, 1),
        "total_sales": int(total_sales * random.uniform(0.99, 1.02)),
        "active_countries": active_countries,
        "live_status": live_status(),
    })


if __name__ == "__main__":
    init_db()
    import os as _os
    debug_mode = _os.environ.get("MARKETSCOPE_DEBUG", "1") == "1"
    app.run(debug=debug_mode, use_reloader=False, host="0.0.0.0", port=5000)
