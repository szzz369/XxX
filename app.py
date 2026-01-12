from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "app.db"

app = Flask(__name__)


@dataclass(frozen=True)
class RechargePlan:
    id: int
    name: str
    amount: float
    bonus_amount: float
    bonus_points: int
    start_time: str
    end_time: str | None
    company_id: int
    status: str


@dataclass(frozen=True)
class Account:
    id: int
    company_id: int
    balance: float
    points: int


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_db()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS account (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            balance REAL NOT NULL DEFAULT 0,
            points INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS recharge_plan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            bonus_amount REAL NOT NULL DEFAULT 0,
            bonus_points INTEGER NOT NULL DEFAULT 0,
            start_time TEXT NOT NULL,
            end_time TEXT,
            company_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'active'
        );

        CREATE TABLE IF NOT EXISTS recharge_record (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            account_id INTEGER NOT NULL,
            plan_id INTEGER NOT NULL,
            principal_amount REAL NOT NULL,
            bonus_amount REAL NOT NULL DEFAULT 0,
            bonus_points INTEGER NOT NULL DEFAULT 0,
            total_amount REAL NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(account_id) REFERENCES account(id),
            FOREIGN KEY(plan_id) REFERENCES recharge_plan(id)
        );
        """
    )
    conn.commit()
    conn.close()


init_db()


def row_to_plan(row: sqlite3.Row) -> RechargePlan:
    return RechargePlan(
        id=row["id"],
        name=row["name"],
        amount=row["amount"],
        bonus_amount=row["bonus_amount"],
        bonus_points=row["bonus_points"],
        start_time=row["start_time"],
        end_time=row["end_time"],
        company_id=row["company_id"],
        status=row["status"],
    )


def row_to_account(row: sqlite3.Row) -> Account:
    return Account(
        id=row["id"],
        company_id=row["company_id"],
        balance=row["balance"],
        points=row["points"],
    )


def get_active_plans(company_id: int) -> list[RechargePlan]:
    now = datetime.now(timezone.utc).isoformat()
    conn = get_db()
    rows = conn.execute(
        """
        SELECT * FROM recharge_plan
        WHERE company_id = ?
          AND status = 'active'
          AND start_time <= ?
          AND (end_time IS NULL OR end_time >= ?)
        ORDER BY amount ASC
        """,
        (company_id, now, now),
    ).fetchall()
    conn.close()
    return [row_to_plan(row) for row in rows]


def ensure_account(company_id: int) -> Account:
    conn = get_db()
    row = conn.execute(
        "SELECT * FROM account WHERE company_id = ? ORDER BY id LIMIT 1",
        (company_id,),
    ).fetchone()
    if row:
        account = row_to_account(row)
        conn.close()
        return account
    cursor = conn.execute(
        "INSERT INTO account (company_id, balance, points) VALUES (?, 0, 0)",
        (company_id,),
    )
    conn.commit()
    account = Account(id=cursor.lastrowid, company_id=company_id, balance=0, points=0)
    conn.close()
    return account


def format_promo(plan: RechargePlan) -> str:
    parts: list[str] = []
    if plan.bonus_amount:
        parts.append(f"赠送{plan.bonus_amount:.2f}元")
    if plan.bonus_points:
        parts.append(f"赠送{plan.bonus_points}积分")
    return "，".join(parts) if parts else "无赠送"


@app.get("/recharge")
def recharge_page() -> str:
    company_id = int(request.args.get("company_id", 1))
    plans = get_active_plans(company_id)
    return render_template("recharge.html", plans=plans, company_id=company_id)


@app.get("/api/recharge/plans")
def recharge_plans() -> Any:
    company_id = int(request.args.get("company_id", 1))
    plans = get_active_plans(company_id)
    return jsonify(
        {
            "company_id": company_id,
            "plans": [
                {
                    "id": plan.id,
                    "name": plan.name,
                    "amount": plan.amount,
                    "bonus_amount": plan.bonus_amount,
                    "bonus_points": plan.bonus_points,
                    "promo_text": format_promo(plan),
                    "start_time": plan.start_time,
                    "end_time": plan.end_time,
                }
                for plan in plans
            ],
        }
    )


@app.post("/api/recharge/complete")
def recharge_complete() -> Any:
    payload = request.get_json(force=True)
    plan_id = int(payload["plan_id"])
    company_id = int(payload.get("company_id", 1))
    account = ensure_account(company_id)

    conn = get_db()
    plan_row = conn.execute(
        "SELECT * FROM recharge_plan WHERE id = ? AND company_id = ?",
        (plan_id, company_id),
    ).fetchone()
    if not plan_row:
        conn.close()
        return jsonify({"error": "plan_not_found"}), 404

    plan = row_to_plan(plan_row)
    principal_amount = plan.amount
    bonus_amount = plan.bonus_amount
    bonus_points = plan.bonus_points
    total_amount = principal_amount + bonus_amount
    created_at = datetime.now(timezone.utc).isoformat()

    conn.execute(
        """
        INSERT INTO recharge_record (
            account_id,
            plan_id,
            principal_amount,
            bonus_amount,
            bonus_points,
            total_amount,
            created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            account.id,
            plan.id,
            principal_amount,
            bonus_amount,
            bonus_points,
            total_amount,
            created_at,
        ),
    )
    conn.execute(
        "UPDATE account SET balance = balance + ?, points = points + ? WHERE id = ?",
        (total_amount, bonus_points, account.id),
    )
    conn.commit()

    updated_account = conn.execute(
        "SELECT * FROM account WHERE id = ?",
        (account.id,),
    ).fetchone()
    conn.close()

    return jsonify(
        {
            "record": {
                "plan_id": plan.id,
                "principal_amount": principal_amount,
                "bonus_amount": bonus_amount,
                "bonus_points": bonus_points,
                "total_amount": total_amount,
                "created_at": created_at,
            },
            "account": {
                "id": updated_account["id"],
                "balance": updated_account["balance"],
                "points": updated_account["points"],
            },
        }
    )


@app.get("/admin/recharge-plans")
def admin_recharge_plans() -> str:
    company_id = int(request.args.get("company_id", 1))
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM recharge_plan WHERE company_id = ? ORDER BY id DESC",
        (company_id,),
    ).fetchall()
    conn.close()
    plans = [row_to_plan(row) for row in rows]
    return render_template("admin_plans.html", plans=plans, company_id=company_id)


@app.post("/admin/recharge-plans")
def admin_create_plan() -> Any:
    form = request.form
    company_id = int(form.get("company_id", 1))
    name = form.get("name", "")
    amount = float(form.get("amount", 0))
    bonus_amount = float(form.get("bonus_amount", 0))
    bonus_points = int(form.get("bonus_points", 0))
    start_time = form.get("start_time") or datetime.now(timezone.utc).isoformat()
    end_time = form.get("end_time") or None
    status = form.get("status", "active")

    conn = get_db()
    conn.execute(
        """
        INSERT INTO recharge_plan (
            name,
            amount,
            bonus_amount,
            bonus_points,
            start_time,
            end_time,
            company_id,
            status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            name,
            amount,
            bonus_amount,
            bonus_points,
            start_time,
            end_time,
            company_id,
            status,
        ),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("admin_recharge_plans", company_id=company_id))


@app.post("/admin/recharge-plans/<int:plan_id>")
def admin_update_plan(plan_id: int) -> Any:
    form = request.form
    company_id = int(form.get("company_id", 1))
    name = form.get("name", "")
    amount = float(form.get("amount", 0))
    bonus_amount = float(form.get("bonus_amount", 0))
    bonus_points = int(form.get("bonus_points", 0))
    start_time = form.get("start_time") or datetime.now(timezone.utc).isoformat()
    end_time = form.get("end_time") or None
    status = form.get("status", "active")

    conn = get_db()
    conn.execute(
        """
        UPDATE recharge_plan
        SET name = ?,
            amount = ?,
            bonus_amount = ?,
            bonus_points = ?,
            start_time = ?,
            end_time = ?,
            status = ?
        WHERE id = ? AND company_id = ?
        """,
        (
            name,
            amount,
            bonus_amount,
            bonus_points,
            start_time,
            end_time,
            status,
            plan_id,
            company_id,
        ),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("admin_recharge_plans", company_id=company_id))


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
