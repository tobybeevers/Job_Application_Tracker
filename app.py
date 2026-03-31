from __future__ import annotations

import os
from datetime import datetime

from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

from services.benchmarks import summarize_recruiter_metrics

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///job_tracker.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Recruiter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    company = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="Applied")
    recruiter_id = db.Column(db.Integer, db.ForeignKey("recruiter.id"), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Interaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("application.id"), nullable=False)
    recruiter_id = db.Column(db.Integer, db.ForeignKey("recruiter.id"), nullable=True)
    interaction_type = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text)
    happened_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


@app.route("/")
def dashboard():
    total_applications = db.session.query(func.count(Application.id)).scalar() or 0
    total_recruiters = db.session.query(func.count(Recruiter.id)).scalar() or 0
    total_interactions = db.session.query(func.count(Interaction.id)).scalar() or 0

    status_counts = (
        db.session.query(Application.status, func.count(Application.id))
        .group_by(Application.status)
        .all()
    )

    aggregate = (
        db.session.query(
            Recruiter.id,
            Recruiter.name,
            Recruiter.company,
            func.count(Application.id).label("applications"),
            func.sum(func.case((Application.status == "Interview", 1), else_=0)).label("interviews"),
            func.sum(func.case((Application.status == "Offer", 1), else_=0)).label("offers"),
            func.sum(func.case((Application.status == "Ghosted", 1), else_=0)).label("ghosted"),
        )
        .outerjoin(Application, Application.recruiter_id == Recruiter.id)
        .group_by(Recruiter.id)
        .all()
    )

    leaderboard = summarize_recruiter_metrics(
        [
            {
                "id": row.id,
                "name": row.name,
                "company": row.company,
                "applications": row.applications or 0,
                "interviews": row.interviews or 0,
                "offers": row.offers or 0,
                "ghosted": row.ghosted or 0,
            }
            for row in aggregate
        ]
    )

    return render_template(
        "dashboard.html",
        total_applications=total_applications,
        total_recruiters=total_recruiters,
        total_interactions=total_interactions,
        status_counts=status_counts,
        leaderboard=leaderboard,
    )


@app.route("/applications", methods=["GET", "POST"])
def applications():
    if request.method == "POST":
        db.session.add(
            Application(
                company=request.form["company"],
                role=request.form["role"],
                status=request.form["status"],
                recruiter_id=request.form.get("recruiter_id") or None,
            )
        )
        db.session.commit()
        return redirect(url_for("applications"))

    records = Application.query.order_by(Application.created_at.desc()).all()
    recruiters = Recruiter.query.order_by(Recruiter.name).all()
    return render_template("applications.html", applications=records, recruiters=recruiters)


@app.route("/recruiters", methods=["GET", "POST"])
def recruiters():
    if request.method == "POST":
        db.session.add(
            Recruiter(
                name=request.form["name"],
                company=request.form["company"],
                email=request.form.get("email"),
            )
        )
        db.session.commit()
        return redirect(url_for("recruiters"))

    rows = Recruiter.query.order_by(Recruiter.created_at.desc()).all()
    return render_template("recruiters.html", recruiters=rows)


@app.route("/interactions", methods=["GET", "POST"])
def interactions():
    if request.method == "POST":
        happened_at = request.form.get("happened_at")
        parsed_dt = datetime.fromisoformat(happened_at) if happened_at else datetime.utcnow()
        db.session.add(
            Interaction(
                application_id=request.form["application_id"],
                recruiter_id=request.form.get("recruiter_id") or None,
                interaction_type=request.form["interaction_type"],
                notes=request.form.get("notes"),
                happened_at=parsed_dt,
            )
        )
        db.session.commit()
        return redirect(url_for("interactions"))

    records = Interaction.query.order_by(Interaction.happened_at.desc()).all()
    applications = Application.query.order_by(Application.created_at.desc()).all()
    recruiters = Recruiter.query.order_by(Recruiter.name).all()
    return render_template(
        "interactions.html",
        interactions=records,
        applications=applications,
        recruiters=recruiters,
    )


@app.cli.command("init-db")
def init_db() -> None:
    db.create_all()
    print("Database initialized.")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)
