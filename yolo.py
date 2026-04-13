import time
import cv2
import csv
import os
import serial
from ultralytics import YOLO

# ================== configuration ==================
SERIAL_PORT = "COM4"          # 改成你的 Arduino 端口
BAUD_RATE = 115200
CAMERA_INDEX = 1              # 你现在 USB 摄像头是 1 就保持 1
MODEL_PATH = "yolov8n.pt"
CONF_THRES = 0.4
SEND_INTERVAL = 0.5           # 每 0.5 秒发送一次人数
TRIAL_ID = "T01"              # 每组实验改一下，例如 T01, T02...
GT_PEOPLE = 1                 # 当前这组实验真实人数，手动改
SAVE_VIDEO = True             # 是否保存检测视频
VIDEO_FPS = 20

# ================== file paths ==================
timestamp_str = time.strftime("%Y%m%d_%H%M%S")
os.makedirs("logs", exist_ok=True)
csv_path = f"logs/{TRIAL_ID}_{timestamp_str}.csv"
video_path = f"logs/{TRIAL_ID}_{timestamp_str}.mp4"

# ================== serial init ==================
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.05)
time.sleep(2)

# ================== model init ==================
model = YOLO(MODEL_PATH)
cap = cv2.VideoCapture(CAMERA_INDEX)

if not cap.isOpened():
    raise RuntimeError("Cannot open USB camera.")

frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

video_writer = None
if SAVE_VIDEO:
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video_writer = cv2.VideoWriter(video_path, fourcc, VIDEO_FPS, (frame_width, frame_height))

# ================== helper ==================
last_send_time = 0
start_time = time.time()

# 用来存 Arduino 返回的最近状态
last_radar = ""
last_fusion = ""
last_light = ""
last_fanpwm = ""

def people_to_fan_target(count: int) -> str:
    if count <= 0:
        return "OFF"
    elif count == 1:
        return "LOW"
    elif count == 2:
        return "MEDIUM"
    else:
        return "HIGH"

def parse_arduino_line(line: str):
    """
    解析 Arduino 回传格式，例如：
    RADAR=1,FUSION=OCC-MID,LIGHT=1,FANPWM=180
    """
    result = {
        "radar_out": "",
        "fusion_state": "",
        "light_on": "",
        "fan_pwm": ""
    }

    try:
        parts = line.strip().split(",")
        for part in parts:
            if "=" not in part:
                continue
            key, value = part.split("=", 1)
            key = key.strip().upper()
            value = value.strip()

            if key == "RADAR":
                result["radar_out"] = value
            elif key == "FUSION":
                result["fusion_state"] = value
            elif key == "LIGHT":
                result["light_on"] = value
            elif key == "FANPWM":
                result["fan_pwm"] = value
    except:
        pass

    return result

# ================== CSV init ==================
with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow([
        "trial_id",
        "elapsed_time_s",
        "gt_people",
        "yolo_people",
        "sent_people",
        "target_fan_level",
        "radar_out",
        "fusion_state",
        "light_on",
        "fan_pwm",
        "raw_arduino_line"
    ])

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to read frame.")
                break

            results = model(frame, conf=CONF_THRES, verbose=False)

            person_count = 0
            annotated = frame.copy()

            for r in results:
                boxes = r.boxes
                if boxes is None:
                    continue

                for box in boxes:
                    cls_id = int(box.cls[0].item())
                    conf = float(box.conf[0].item())

                    # COCO person class = 0
                    if cls_id == 0 and conf >= CONF_THRES:
                        person_count += 1
                        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                        cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(
                            annotated,
                            f"person {conf:.2f}",
                            (x1, max(0, y1 - 10)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (0, 255, 0),
                            2
                        )

            # 你的 Arduino 新程序需要的是“真实人数”
            sent_people = person_count

            now = time.time()
            raw_arduino_line = ""

            # 定时发送给 Arduino
            if now - last_send_time >= SEND_INTERVAL:
                ser.write(f"{sent_people}\n".encode("utf-8"))
                last_send_time = now

            # 尝试读取 Arduino 回传（如果 Arduino 没有回传，这里也不会报错）
            try:
                if ser.in_waiting > 0:
                    raw_arduino_line = ser.readline().decode("utf-8", errors="ignore").strip()
                    parsed = parse_arduino_line(raw_arduino_line)

                    if parsed["radar_out"] != "":
                        last_radar = parsed["radar_out"]
                    if parsed["fusion_state"] != "":
                        last_fusion = parsed["fusion_state"]
                    if parsed["light_on"] != "":
                        last_light = parsed["light_on"]
                    if parsed["fan_pwm"] != "":
                        last_fanpwm = parsed["fan_pwm"]
            except:
                pass

            elapsed = round(now - start_time, 3)
            target_fan_level = people_to_fan_target(person_count)

            # 写 CSV
            writer.writerow([
                TRIAL_ID,
                elapsed,
                GT_PEOPLE,
                person_count,
                sent_people,
                target_fan_level,
                last_radar,
                last_fusion,
                last_light,
                last_fanpwm,
                raw_arduino_line
            ])
            f.flush()

            # 画面叠字
            cv2.putText(
                annotated,
                f"Trial: {TRIAL_ID}",
                (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (255, 0, 0),
                2
            )

            cv2.putText(
                annotated,
                f"GT: {GT_PEOPLE}  YOLO: {person_count}",
                (20, 65),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 0, 255),
                2
            )

            cv2.putText(
                annotated,
                f"Target Fan: {target_fan_level}",
                (20, 100),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 128, 255),
                2
            )

            cv2.putText(
                annotated,
                f"Radar: {last_radar} Fusion: {last_fusion}",
                (20, 135),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 0),
                2
            )

            cv2.putText(
                annotated,
                f"Light: {last_light} FanPWM: {last_fanpwm}",
                (20, 170),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 0),
                2
            )

            cv2.imshow("YOLOv8 People Counting + Logging", annotated)

            if video_writer is not None:
                video_writer.write(annotated)

            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord('q'):
                break

    finally:
        cap.release()
        if video_writer is not None:
            video_writer.release()
        cv2.destroyAllWindows()
        ser.close()

print(f"CSV log saved to: {csv_path}")
if SAVE_VIDEO:
    print(f"Video saved to: {video_path}")