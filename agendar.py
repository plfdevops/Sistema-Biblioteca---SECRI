import json
import os
import subprocess
import sys

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def schedule_linux(hour, minute):
    python = sys.executable
    cmd = f'{python} -c "from notifier import send_overdue_notification; send_overdue_notification()"'
    cron_line = f"{minute} {hour} * * * cd {SCRIPT_DIR} && {cmd}"

    # Verifica se já existe
    result = subprocess.run("crontab -l", shell=True, capture_output=True, text=True)
    current = result.stdout if result.returncode == 0 else ""

    if "send_overdue_notification" in current:
        print("Cron já está configurado. Atualizando...")
        lines = [l for l in current.splitlines() if "send_overdue_notification" not in l]
        lines.append(cron_line)
    else:
        lines = current.splitlines() + [cron_line]

    new_cron = "\n".join(lines) + "\n"
    proc = subprocess.run("crontab -", shell=True, input=new_cron, text=True)
    if proc.returncode == 0:
        print(f"✓ Cron agendado: todo dia às {hour:02d}:{minute:02d}")
    else:
        print("✗ Erro ao configurar cron.")


def schedule_windows(hour, minute):
    python = sys.executable
    task_name = "BibliotecaSECRI_Notificacao"
    cmd = f'cd /d {SCRIPT_DIR} && {python} -c "from notifier import send_overdue_notification; send_overdue_notification()"'

    # Remove tarefa anterior se existir
    subprocess.run(f'schtasks /delete /tn {task_name} /f', shell=True, capture_output=True)

    # Cria nova tarefa
    result = subprocess.run(
        f'schtasks /create /tn {task_name} /tr "cmd /c {cmd}" /sc daily /st {hour:02d}:{minute:02d} /f',
        shell=True, capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"✓ Tarefa agendada: todo dia às {hour:02d}:{minute:02d}")
    else:
        print(f"✗ Erro: {result.stderr}")


def main():
    config = load_config()
    time_str = config.get("schedule_time", "08:00")
    platform = config.get("platform", "auto")

    hour, minute = map(int, time_str.split(":"))

    if platform == "auto":
        platform = "windows" if sys.platform == "win32" else "linux"

    print(f"Plataforma: {platform}")
    print(f"Horário: {time_str}")

    if platform == "linux":
        schedule_linux(hour, minute)
    elif platform == "windows":
        schedule_windows(hour, minute)
    else:
        print(f"✗ Plataforma '{platform}' não reconhecida. Use: auto, linux ou windows")


if __name__ == "__main__":
    main()
