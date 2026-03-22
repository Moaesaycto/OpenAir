import pynmea2
import serial
import serial.tools.list_ports

GPS_BAUD = 9600
GPS_PORT = "/dev/cu.usbmodem1101"


def find_gps_port() -> str | None:
    for port in serial.tools.list_ports.comports():
        if port.vid and port.pid:
            return port.device
    return None


def try_get_gps(port: str | None = None) -> dict:
    port = GPS_PORT
    if not port:
        return {"available": False, "reason": "No GPS device found"}
    try:
        with serial.Serial(port, GPS_BAUD, timeout=1) as ser:
            for _ in range(30):
                line = ser.readline().decode("ascii", errors="replace")
                if line.startswith("$GPGGA"):
                    try:
                        msg = pynmea2.parse(line)
                        if (
                            msg.gps_qual
                            and int(msg.gps_qual) > 0
                            and msg.latitude
                            and msg.longitude
                        ):
                            return {
                                "available": True,
                                "lat": float(msg.latitude),
                                "lon": float(msg.longitude),
                                "port": port,
                            }
                    except pynmea2.ParseError:
                        continue
        return {"available": False, "reason": "No GPS fix"}
    except serial.SerialException as e:
        return {"available": False, "reason": str(e)}
