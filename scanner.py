import socket
import json
from datetime import datetime

# --- Настройки ---
TARGET = "192.168.1.1"
PORTS = [21, 22, 23, 25, 53, 80, 110, 443, 8080, 8443]
TIMEOUT = 1  # секунд на порт

# Цвета для консоли (ANSI)
COLORS = {
    "Высокий": "\033[91m",   # красный
    "Средний": "\033[93m",   # жёлтый
    "Низкий": "\033[92m",    # зелёный
    "Информационный": "\033[94m",  # синий
    "reset": "\033[0m"
}

def load_knowledge_base(filename="knowledge_base.json"):
    """Загружает базу знаний из JSON-файла."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Ошибка: файл {filename} не найден.")
        return {}
    except json.JSONDecodeError:
        print(f"Ошибка: файл {filename} повреждён.")
        return {}

def scan_ports(target, ports):
    """Сканирует порты и возвращает список открытых."""
    open_ports = []
    print(f"Сканируем {target}...\n")
    
    for port in ports:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT)
        result = s.connect_ex((target, port))
        if result == 0:
            open_ports.append(port)
        s.close()
    
    return open_ports

def print_brief_report(target, open_ports, kb):
    """Выводит краткий отчёт в консоль с цветами."""
    print("=" * 50)
    print(f"КРАТКИЙ ОТЧЁТ: {target}")
    print("=" * 50)
    
    if not open_ports:
        print("Открытых портов не найдено.")
        return
    
    for port in open_ports:
        info = kb.get(str(port), {})
        service = info.get("service", "Неизвестно")
        risk = info.get("risk", "Неизвестно")
        color = COLORS.get(risk, "")
        reset = COLORS["reset"]
        
        print(f"Порт {port:5} | {service:10} | Риск: {color}{risk}{reset}")
    
    print("=" * 50)
    print(f"Всего открыто: {len(open_ports)} портов.")
    
    # Считаем по уровням риска
    risk_counts = {}
    for port in open_ports:
        risk = kb.get(str(port), {}).get("risk", "Неизвестно")
        risk_counts[risk] = risk_counts.get(risk, 0) + 1
    
    for risk, count in risk_counts.items():
        print(f"  {risk}: {count}")

def save_detailed_report(target, open_ports, kb):
    """Сохраняет подробный отчёт в текстовый файл."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"report_{target.replace('.', '_')}_{timestamp}.txt"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write(f"ПОДРОБНЫЙ ОТЧЁТ ПО БЕЗОПАСНОСТИ\n")
        f.write(f"Цель: {target}\n")
        f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")
        
        if not open_ports:
            f.write("Открытых портов не найдено.\n")
            return filename
        
        for port in open_ports:
            info = kb.get(str(port), {})
            service = info.get("service", "Неизвестно")
            risk = info.get("risk", "Неизвестно")
            description = info.get("description", "Описание отсутствует.")
            recommendations = info.get("recommendations", [])
            
            f.write(f"--- Порт {port} ({service}) ---\n")
            f.write(f"Уровень риска: {risk}\n")
            f.write(f"Описание: {description}\n")
            f.write("Рекомендации:\n")
            for rec in recommendations:
                f.write(f"  - {rec}\n")
            f.write("\n")
        
        f.write("=" * 60 + "\n")
        f.write("Конец отчёта.\n")
    
    return filename

def main():
    kb = load_knowledge_base()
    if not kb:
        print("База знаний пуста. Проверьте файл knowledge_base.json")
        return
    
    open_ports = scan_ports(TARGET, PORTS)
    print_brief_report(TARGET, open_ports, kb)
    
    report_file = save_detailed_report(TARGET, open_ports, kb)
    print(f"\nПодробный отчёт сохранён в: {report_file}")

if __name__ == "__main__":
    main()