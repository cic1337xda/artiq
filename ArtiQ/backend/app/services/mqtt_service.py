import json
import os
import paho.mqtt.client as mqtt

from app.core.config import settings

# In-memory live telemetry state for connected EMG hardware node
emg_node_status: dict = {
    "mac": "Waiting for node...",
    "target_mac": "",
    "is_online": False,
    "raw": 0,
    "percent": 0,
    "mvc": 0,
    "calibrating": False,
}

# Cache per-MAC latest state so switching/re-linking a node restores live status immediately
nodes_cache: dict[str, dict] = {}


def _on_mqtt_connect(client, userdata, flags, rc, *args, **kwargs):
    print(
        f"[SYSTEM] Connected to MQTT Broker {settings.MQTT_BROKER}:{settings.MQTT_PORT} (Code: {rc})",
        flush=True,
    )
    client.subscribe("artiq/emg/data/+")
    client.subscribe("artiq/emg/status/+")
    print("[SYSTEM] Subscribed to ArtiQ EMG topics!", flush=True)


def _on_mqtt_message(client, userdata, msg, *args, **kwargs):
    global emg_node_status
    topic = msg.topic
    payload = msg.payload.decode(errors="ignore")

    mac = topic.split("/")[-1].replace(":", "").strip().upper()
    node_state = nodes_cache.setdefault(
        mac,
        {
            "mac": mac,
            "is_online": False,
            "raw": 0,
            "percent": None,
            "mvc": 0,
            "calibrating": False,
        },
    )

    if "artiq/emg/status/" in topic:
        node_state["is_online"] = payload.strip().lower() == "online"
        state = "ONLINE" if node_state["is_online"] else "OFFLINE"
        print(f"[EMG NODE] {mac} is now {state}", flush=True)
    elif "artiq/emg/data/" in topic:
        try:
            data = json.loads(payload)
            node_state["is_online"] = True
            node_state["raw"] = data.get("raw", 0)
            node_state["percent"] = data.get("percent")
            node_state["mvc"] = data.get("mvc", 0)
            node_state["calibrating"] = data.get("calibrating", False)
        except Exception:
            return
    else:
        return

    target = emg_node_status.get("target_mac", "")
    if target and mac != target:
        return

    emg_node_status["mac"] = mac
    emg_node_status["is_online"] = node_state["is_online"]
    emg_node_status["raw"] = node_state["raw"]
    emg_node_status["percent"] = node_state["percent"]
    emg_node_status["mvc"] = node_state["mvc"]
    emg_node_status["calibrating"] = node_state["calibrating"]


def set_active_target_mac(normalized_mac: str) -> None:
    """Bind telemetry state to a specific MAC and hydrate from cache if already online."""
    emg_node_status["target_mac"] = normalized_mac
    cached = nodes_cache.get(normalized_mac)
    if cached:
        emg_node_status["mac"] = normalized_mac
        emg_node_status["is_online"] = cached["is_online"]
        emg_node_status["raw"] = cached["raw"]
        emg_node_status["percent"] = cached["percent"]
        emg_node_status["mvc"] = cached["mvc"]
        emg_node_status["calibrating"] = cached["calibrating"]
    else:
        emg_node_status["mac"] = "Waiting for node..."
        emg_node_status["is_online"] = False
        emg_node_status["raw"] = 0
        emg_node_status["percent"] = None
        emg_node_status["mvc"] = 0
        emg_node_status["calibrating"] = False


try:
    mqtt_backend_client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION1, f"artiq_backend_{os.getpid()}"
    )
except AttributeError:
    mqtt_backend_client = mqtt.Client(f"artiq_backend_{os.getpid()}")

mqtt_backend_client.on_connect = _on_mqtt_connect
mqtt_backend_client.on_message = _on_mqtt_message


def start_mqtt_client() -> None:
    """Start non-blocking MQTT background loop and connect to Mosquitto broker."""
    mqtt_backend_client.loop_start()
    try:
        mqtt_backend_client.connect_async(settings.MQTT_BROKER, settings.MQTT_PORT, 60)
    except Exception as exc:
        print(f"[ERROR] MQTT Connection Failed: {exc}", flush=True)


def stop_mqtt_client() -> None:
    mqtt_backend_client.loop_stop()
    mqtt_backend_client.disconnect()


def publish_emg_command(mac: str, cmd: str) -> None:
    topic = f"artiq/emg/command/{mac}"
    mqtt_backend_client.publish(topic, cmd, qos=1)
