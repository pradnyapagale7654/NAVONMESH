from fastapi import APIRouter
from database import get_connection

router = APIRouter()


# GET all machines
@router.get("/machines")
def get_machines():

    conn = get_connection()

    rows = conn.execute("""
        SELECT DISTINCT Machine_ID, Machine_Model
        FROM machine_energy
    """).fetchall()

    conn.close()

    return [dict(row) for row in rows]


# LIVE DATA
@router.get("/live")
def get_live():

    conn = get_connection()

    rows = conn.execute("""
        SELECT Machine_ID,
               Machine_Model,
               Power_kW,
               Energy_kWh,
               Timestamp,
               [Load_%]
        FROM machine_energy
        ORDER BY Timestamp DESC
        LIMIT 10
    """).fetchall()

    conn.close()

    return [dict(row) for row in rows]


# ANALYTICS SUMMARY
@router.get("/analytics")
def analytics():

    conn = get_connection()

    total_energy = conn.execute(
        "SELECT SUM(Energy_kWh) as value FROM machine_energy"
    ).fetchone()["value"]

    avg_power = conn.execute(
        "SELECT AVG(Power_kW) as value FROM machine_energy"
    ).fetchone()["value"]

    avg_load = conn.execute(
        "SELECT AVG([Load_%]) as value FROM machine_energy"
    ).fetchone()["value"]

    conn.close()

    return {
        "total_energy_kWh": round(total_energy, 2) if total_energy else 0,
        "avg_power_kW": round(avg_power, 2) if avg_power else 0,
        "avg_load_percent": round(avg_load, 2) if avg_load else 0
    }


# ALERTS
@router.get("/alerts")
def alerts():

    conn = get_connection()

    rows = conn.execute("""
        SELECT Machine_ID,
               Power_kW,
               [Load_%]
        FROM machine_energy
        WHERE Power_kW > 80 OR [Load_%] > 90
        LIMIT 10
    """).fetchall()

    conn.close()

    result = []

    for row in rows:

        message = ""

        if row["Power_kW"] > 80:
            message = "High Power Consumption"

        elif row["Load_%"] > 90:
            message = "Machine Overloaded"

        result.append({
            "Machine_ID": row["Machine_ID"],
            "message": message
        })

    return result


# SIMPLE PREDICTION (baseline hackathon logic)
@router.get("/prediction")
def prediction():

    conn = get_connection()

    avg_energy = conn.execute(
        "SELECT AVG(Energy_kWh) as value FROM machine_energy"
    ).fetchone()["value"]

    conn.close()

    predicted = avg_energy * 1.1 if avg_energy else 0

    return {
        "predicted_next_hour_kWh": round(predicted, 2)
    }