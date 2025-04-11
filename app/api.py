from fastapi import FastAPI, HTTPException
import uvicorn

app = FastAPI()

# Simulated database (in-memory storage for now)
machine_logic_db = {
    "machine_A": "def process(data, state): state['status'] = 'running' if data['signal'] == 1 else 'stopped'; return state",
    "machine_B": "def process(data, state): state['status'] = 'running' if data['timestamp'] % 2 == 0 else 'stopped'; return state",
    "machine_C": "def process(data, state): state['status'] = 'stopped' if data['signal'] == 0 else 'running'; return state"
}

@app.get("/machines/{machine_id}/logic")
async def get_machine_logic(machine_id: str):
    """Retrieve the processing logic for a machine."""
    if machine_id in machine_logic_db:
        return {"machine_id": machine_id, "logic": machine_logic_db[machine_id]}
    raise HTTPException(status_code=404, detail="Machine not found")

@app.post("/machines/{machine_id}/logic")
async def update_machine_logic(machine_id: str, logic: str):
    """Update the processing logic for a machine."""
    if not logic.startswith("def process("):
        raise HTTPException(status_code=400, detail="Invalid function format")
    
    machine_logic_db[machine_id] = logic
    return {"message": "Logic updated successfully", "machine_id": machine_id}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
