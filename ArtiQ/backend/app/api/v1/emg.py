from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.common import api_response
from app.schemas.session import MacRequest
from app.services.mqtt_service import (
    emg_node_status,
    publish_emg_command,
    set_active_target_mac,
)

router = APIRouter(tags=["EMG Telemetry"])

ALLOWED_EMG_COMMANDS = {"calibrate", "reset", "relax", "baseline"}


@router.get("/api/emg/telemetry")
@router.get("/api/v1/emg/telemetry")
def get_emg_telemetry(current_user: User = Depends(get_current_user)):
    return api_response(True, "Telemetry retrieved.", data=emg_node_status)


@router.post("/api/emg/set-mac")
@router.post("/api/v1/emg/set-mac")
def set_target_mac(
    req: MacRequest,
    current_user: User = Depends(get_current_user),
):
    normalized_mac = req.mac.replace(":", "").replace(" ", "").strip().upper()
    if not normalized_mac:
        raise HTTPException(status_code=400, detail="Valid MAC address is required.")

    set_active_target_mac(normalized_mac)
    return api_response(
        True,
        "Target hardware node linked.",
        data={"target_mac": normalized_mac},
    )


@router.post("/api/emg/command/{cmd}")
@router.post("/api/v1/emg/command/{cmd}")
def send_emg_command(
    cmd: str,
    current_user: User = Depends(get_current_user),
):
    clean_cmd = cmd.strip().lower()
    if clean_cmd not in ALLOWED_EMG_COMMANDS:
        raise HTTPException(status_code=400, detail="Unsupported hardware command.")

    mac = emg_node_status.get("target_mac") or emg_node_status.get("mac")
    if not mac or mac == "Waiting for node...":
        raise HTTPException(status_code=400, detail="No active node connected!")

    publish_emg_command(mac, clean_cmd)
    return api_response(
        True,
        f"Command '{clean_cmd}' dispatched to hardware node.",
        data={"command": clean_cmd, "target": mac},
    )
