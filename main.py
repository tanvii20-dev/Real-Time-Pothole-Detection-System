from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Enable CORS so your Frontend can talk to the Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- GLOBAL KNOWLEDGE GRAPH ---
# base_weight = distance. Higher hazards = higher cost.
road_network = {
    "Route_A": {
        "name": "Highway 101 (Main)",
        "coords": [[18.1506, 74.5768], [18.1515, 74.5780], [18.1530, 74.5800], [18.1550, 74.5820]],
        "base_weight": 5.0,
        "hazards": []
    },
    "Route_B": {
        "name": "Bypass Sector 7 (Safe)",
        "coords": [[18.1506, 74.5768], [18.1500, 74.5800], [18.1510, 74.5850], [18.1550, 74.5820]],
        "base_weight": 7.5, # Longer distance
        "hazards": []
    }
}

class HazardReport(BaseModel):
    lat: float
    lon: float
    severity: int

@app.get("/navigation/plan")
async def plan_route():
    """
    GOOGLE-SCALE LOGIC:
    Calculate path cost: Cost = Distance + (Hazards * Penalty)
    """
    penalty_multiplier = 2.0
    
    cost_a = road_network["Route_A"]["base_weight"] + (len(road_network["Route_A"]["hazards"]) * penalty_multiplier)
    cost_b = road_network["Route_B"]["base_weight"] + (len(road_network["Route_B"]["hazards"]) * penalty_multiplier)
    
    # Selection Logic
    if cost_a <= cost_b:
        selected = "Route_A"
        reason = "Shortest Path"
    else:
        selected = "Route_B"
        reason = "Safest Path (Hazards detected on Main)"

    return {
        "selected_id": selected,
        "route_name": road_network[selected]["name"],
        "coords": road_network[selected]["coords"],
        "cost_analysis": {"Route_A": cost_a, "Route_B": cost_b},
        "recommendation": reason
    }

@app.post("/report_hazard")
async def report_hazard(report: HazardReport):
    # In a real system, we'd check which road is closest to these coords
    # For the demo, we add the hazard to Route_A (Main Road)
    road_network["Route_A"]["hazards"].append({"lat": report.lat, "lon": report.lon})
    return {"status": "Global Map Updated", "total_hazards": len(road_network["Route_A"]["hazards"])}

@app.get("/hazards/all")
async def get_all_hazards():
    return road_network["Route_A"]["hazards"] + road_network["Route_B"]["hazards"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)