import sys
import subprocess
import importlib.util
import os

REQUIRED_PACKAGES = {
    'customtkinter': 'customtkinter',
    'PIL': 'Pillow',
    'psutil': 'psutil',
    'wmi': 'wmi',
    'pythoncom': 'pywin32'
}

def check_and_install_packages():
    missing_packages = []
    
    for module_name, package_name in REQUIRED_PACKAGES.items():
        if importlib.util.find_spec(module_name) is None:
            missing_packages.append(package_name)
    
    if missing_packages:
        print("=" * 60)
        print("zInfo - Installazione Dipendenze / Dependencies Installation")
        print("=" * 60)
        print(f"\nPacchetti mancanti / Missing packages: {', '.join(missing_packages)}")
        print("\nInstallazione in corso / Installing...\n")
        
        for package in missing_packages:
            try:
                print(f"Installing {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])
                print(f"✓ {package} installato con successo / installed successfully")
            except subprocess.CalledProcessError:
                print(f"✗ Errore installando / Error installing {package}")
                print(f"  Prova manualmente / Try manually: pip install {package}")
        
        print("\n" + "=" * 60)
        print("Installazione completata! Avvio applicazione...")
        print("Installation completed! Starting application...")
        print("=" * 60 + "\n")

check_and_install_packages()

import customtkinter as ctk
import tkinter as tk
import threading
import psutil
import platform
import math
import traceback
from PIL import Image, ImageDraw

try:
    import wmi
    import pythoncom
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

def get_system_language():
    try:
        import locale
        try:
            sys_lang = locale.getlocale()[0]
        except:
            sys_lang = None
        
        if not sys_lang:
            try:
                sys_lang = locale.getdefaultlocale()[0]
            except:
                sys_lang = None
        
        if sys_lang:
            if sys_lang.startswith('it'):
                return 'it'
            elif sys_lang.startswith('en'):
                return 'en'
            elif sys_lang.startswith('es'):
                return 'es'
            elif sys_lang.startswith('fr'):
                return 'fr'
            elif sys_lang.startswith('de'):
                return 'de'
        return 'en'
    except:
        return 'en'

TRANSLATIONS = {
    'it': {
        'title': 'zInfo Pro',
        'analyzing': 'Analisi del sistema in corso...',
        'light_mode': 'Modalità Chiara',
        'dark_mode': 'Modalità Scura',
        'changing_in': 'Cambio in {}s',
        'footer': '✨ zInfo Pro | v2.0.0 | Multi-Platform System Tool ✨',
        'os': 'SISTEMA OPERATIVO',
        'cpu': 'PROCESSORE',
        'memory': 'MEMORIA RAM',
        'disks': 'ARCHIVIAZIONE',
        'devices': 'PERIFERICHE E DRIVER',
        'license': 'LICENZA WINDOWS',
        'os_label': 'Sistema',
        'edition': 'Edizione',
        'version': 'Versione',
        'architecture': 'Architettura',
        'computer_name': 'Nome Computer',
        'processor': 'Processore',
        'physical_cores': 'Core Fisici',
        'logical_cores': 'Thread Logici',
        'max_frequency': 'Frequenza Max',
        'frequency_unavailable': 'Frequenza: Non disponibile',
        'total': 'Totale',
        'available': 'Disponibile',
        'in_use': 'In Uso',
        'drive': 'Unità',
        'space': 'Spazio',
        'info_unavailable': 'Informazioni non disponibili',
        'graphics': '  ▸ Schede Grafiche:',
        'driver': '     ├─ Driver',
        'audio': '\n  ▸ Dispositivi Audio:',
        'network': '\n  ▸ Schede di Rete:',
        'ip': '     ├─ IP',
        'wmi_error': '  Errore WMI: {}',
        'wmi_not_installed': '  WMI non disponibile',
        'drivers_windows_only': '  Info driver disponibili solo su Windows',
        'license_key': 'Chiave Prodotto',
        'license_status': 'Stato Licenza',
        'license_error': 'Impossibile recuperare la licenza',
        'license_linux': 'Sistema Linux - Licenza non applicabile',
        'fatal_error': 'ERRORE CRITICO',
        'refresh': 'Aggiorna Dati',
        'refreshing': 'Aggiornamento...'
    },
    'en': {
        'title': 'zInfo Pro',
        'analyzing': 'System analysis in progress...',
        'light_mode': 'Light Mode',
        'dark_mode': 'Dark Mode',
        'changing_in': 'Changing in {}s',
        'footer': '✨ zInfo Pro | v2.0.0 | Multi-Platform System Tool ✨',
        'os': 'OPERATING SYSTEM',
        'cpu': 'PROCESSOR',
        'memory': 'RAM MEMORY',
        'disks': 'STORAGE',
        'devices': 'DEVICES AND DRIVERS',
        'license': 'WINDOWS LICENSE',
        'os_label': 'System',
        'edition': 'Edition',
        'version': 'Version',
        'architecture': 'Architecture',
        'computer_name': 'Computer Name',
        'processor': 'Processor',
        'physical_cores': 'Physical Cores',
        'logical_cores': 'Logical Threads',
        'max_frequency': 'Max Frequency',
        'frequency_unavailable': 'Frequency: Not available',
        'total': 'Total',
        'available': 'Available',
        'in_use': 'In Use',
        'drive': 'Drive',
        'space': 'Space',
        'info_unavailable': 'Information not available',
        'graphics': '  ▸ Graphics Cards:',
        'driver': '     ├─ Driver',
        'audio': '\n  ▸ Audio Devices:',
        'network': '\n  ▸ Network Adapters:',
        'ip': '     ├─ IP',
        'wmi_error': '  WMI Error: {}',
        'wmi_not_installed': '  WMI not available',
        'drivers_windows_only': '  Driver info available only on Windows',
        'license_key': 'Product Key',
        'license_status': 'License Status',
        'license_error': 'Unable to retrieve license',
        'license_linux': 'Linux System - License not applicable',
        'fatal_error': 'CRITICAL ERROR',
        'refresh': 'Refresh Data',
        'refreshing': 'Refreshing...'
    }
}

def format_bytes(bytes_val):
    if bytes_val < 1024:
        return f"{bytes_val} B"
    exp = int(math.log(bytes_val) / math.log(1024))
    pre = "KMGTPE"[exp - 1] + "B"
    return f"{bytes_val / (1024 ** exp):.2f} {pre}"

def get_windows_license():
    try:
        result = subprocess.run(
            ['wmic', 'path', 'softwarelicensingservice', 'get', 'OA3xOriginalProductKey'],
            capture_output=True, text=True, timeout=5, creationflags=subprocess.CREATE_NO_WINDOW
        )
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            key = lines[1].strip()
            if key:
                return key
        
        result = subprocess.run(
            ['wmic', 'path', 'SoftwareLicensingProduct', 'where', 
             'ApplicationID="55c92734-d682-4d71-983e-d6ec3f16059f"', 
             'get', 'LicenseStatus'],
            capture_output=True, text=True, timeout=5, creationflags=subprocess.CREATE_NO_WINDOW
        )
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            status = lines[1].strip()
            if status == '1':
                return 'Licensed ✓'
            elif status == '0':
                return 'Unlicensed ✗'
        
        return 'Status Unknown'
    except Exception:
        return 'Unable to retrieve'

def get_system_info():
    lang = get_system_language()
    t = TRANSLATIONS.get(lang, TRANSLATIONS['en'])
    
    if WMI_AVAILABLE and platform.system() == "Windows":
        try:
            pythoncom.CoInitialize()
        except Exception:
            pass
            
    info_sections = {}
    try:
        uname = platform.uname()

        os_info = []
        os_info.append(f"┌─ {t['os_label']}: {uname.system} {uname.release}")
        if uname.system == "Windows":
            try:
                edition = platform.win32_edition()
                if edition:
                    os_info.append(f"├─ {t['edition']}: {edition}")
            except:
                pass
        os_info.append(f"├─ {t['version']}: {uname.version}")
        os_info.append(f"├─ {t['architecture']}: {uname.machine}")
        os_info.append(f"└─ {t['computer_name']}: {uname.node}")
        info_sections[t['os']] = "\n".join(os_info)

        cpu_info = []
        cpu_info.append(f"┌─ {t['processor']}: {uname.processor}")
        cpu_info.append(f"├─ {t['physical_cores']}: {psutil.cpu_count(logical=False)}")
        cpu_info.append(f"├─ {t['logical_cores']}: {psutil.cpu_count(logical=True)}")
        try:
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                cpu_info.append(f"├─ {t['max_frequency']}: {cpu_freq.max:.2f} MHz")
                cpu_info.append(f"└─ Utilizzo: {psutil.cpu_percent(interval=0.1)}%")
            else:
                cpu_info.append(f"└─ {t['frequency_unavailable']}")
        except Exception:
            cpu_info.append(f"└─ {t['frequency_unavailable']}")
        info_sections[t['cpu']] = "\n".join(cpu_info)

        memory_info = []
        memory = psutil.virtual_memory()
        memory_info.append(f"┌─ {t['total']}: {format_bytes(memory.total)}")
        memory_info.append(f"├─ {t['available']}: {format_bytes(memory.available)}")
        memory_info.append(f"└─ {t['in_use']}: {format_bytes(memory.used)} ({memory.percent}%)")
        info_sections[t['memory']] = "\n".join(memory_info)

        disk_info = []
        partitions = psutil.disk_partitions()
        for idx, p in enumerate(partitions):
            prefix = "└─" if idx == len(partitions) - 1 else "├─"
            disk_info.append(f"{prefix} {t['drive']}: {p.device} ({p.fstype})")
            try:
                usage = psutil.disk_usage(p.mountpoint)
                sub_prefix = "    " if idx == len(partitions) - 1 else "│   "
                disk_info.append(f"{sub_prefix}{t['space']}: {format_bytes(usage.used)} / {format_bytes(usage.total)} ({usage.percent}%)")
            except (PermissionError, FileNotFoundError):
                sub_prefix = "    " if idx == len(partitions) - 1 else "│   "
                disk_info.append(f"{sub_prefix}{t['info_unavailable']}")
        info_sections[t['disks']] = "\n".join(disk_info)
        
        driver_info = []
        if WMI_AVAILABLE and uname.system == "Windows":
            try:
                c = wmi.WMI() 
                driver_info.append(t['graphics'])
                for controller in c.Win32_VideoController():
                    driver_info.append(f"     ├─ {controller.Name}")
                    if controller.DriverVersion:
                        driver_info.append(f"     │  {t['driver']}: {controller.DriverVersion}")
                
                driver_info.append(t['audio'])
                for sound in c.Win32_SoundDevice():
                    if sound.Name:
                        driver_info.append(f"     ├─ {sound.Name}")

                driver_info.append(t['network'])
                for adapter in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
                    if adapter.IPAddress:
                        driver_info.append(f"     ├─ {adapter.Description}")
                        driver_info.append(f"     │  {t['ip']}: {adapter.IPAddress[0]}")
                        
            except Exception as e:
                driver_info.append(t['wmi_error'].format(str(e)[:50]))
        elif uname.system == "Windows":
            driver_info.append(t['wmi_not_installed'])
        else:
            try:
                result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    gpu_lines = [l for l in lines if 'VGA' in l or 'Display' in l or '3D' in l]
                    if gpu_lines:
                        driver_info.append(t['graphics'])
                        for gpu in gpu_lines[:3]:
                            driver_info.append(f"     ├─ {gpu.split(': ')[-1]}")
                    
                    audio_lines = [l for l in lines if 'Audio' in l]
                    if audio_lines:
                        driver_info.append(t['audio'])
                        for audio in audio_lines[:3]:
                            driver_info.append(f"     ├─ {audio.split(': ')[-1]}")
                    
                    net_lines = [l for l in lines if 'Network' in l or 'Ethernet' in l]
                    if net_lines:
                        driver_info.append(t['network'])
                        for net in net_lines[:3]:
                            driver_info.append(f"     ├─ {net.split(': ')[-1]}")
            except:
                driver_info.append(t['drivers_windows_only'])
        
        if not driver_info:
            driver_info.append(t['drivers_windows_only'])
        info_sections[t['devices']] = "\n".join(driver_info)

        license_info = []
        if uname.system == "Windows":
            license_key = get_windows_license()
            license_info.append(f"┌─ {t['license_key']}: {license_key}")
            license_info.append(f"└─ {t['license_status']}: Active")
        else:
            license_info.append(f"└─ {t['license_linux']}")
        info_sections[t['license']] = "\n".join(license_info)

        return info_sections
    except Exception as e:
        return {t['fatal_error']: traceback.format_exc()}

def generate_gradient_image(width, height, start_color, end_color, filename):
    try:
        Image.open(filename)
    except FileNotFoundError:
        img = Image.new('RGB', (width, height), start_color)
        draw = ImageDraw.Draw(img)
        for i in range(height):
            r = int(start_color[0] + (end_color[0] - start_color[0]) * i / height)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * i / height)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * i / height)
            draw.line((0, i, width, i), fill=(r, g, b))
        img.save(filename)

class ZInformationApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.lang = get_system_language()
        self.t = TRANSLATIONS.get(self.lang, TRANSLATIONS['en'])
        
        self.is_dark_mode = True
        self.theme_changing = False
        self.is_refreshing = False
        
        self.title(self.t['title'])
        self.geometry("800x900")
        self.resizable(False, False)

        self.title_font = ctk.CTkFont(family="Segoe UI", size=38, weight="bold")
        self.section_title_font = ctk.CTkFont(family="Segoe UI", size=20, weight="bold")
        self.info_text_font = ctk.CTkFont(family="Consolas", size=13)
        self.button_font = ctk.CTkFont(family="Segoe UI", size=14, weight="bold")
        self.footer_font = ctk.CTkFont(family="Segoe UI", size=10, slant="italic")

        try:
            self.iconbitmap("icon.ico")
        except Exception:
            pass 

        self.light_img = Image.open("gradient_bg_light.png")
        self.dark_img = Image.open("gradient_bg_dark.png")
        self.bg_image_ctk = ctk.CTkImage(light_image=self.light_img, dark_image=self.dark_img, size=(800, 900))
        self.bg_image_label = ctk.CTkLabel(self, image=self.bg_image_ctk, text="")
        self.bg_image_label.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.glass_frame = ctk.CTkFrame(
            self, 
            corner_radius=25, 
            border_width=3,
            fg_color=("#FCFCFC", "#1C1C1C"), 
            border_color=("#E0E0E0", "#353535")
        )
        self.glass_frame.grid(row=0, column=0, padx=45, pady=45, sticky="nsew")
        self.glass_frame.grid_columnconfigure(0, weight=1)
        self.glass_frame.grid_rowconfigure(2, weight=1)

        self.header_frame = ctk.CTkFrame(self.glass_frame, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=30, pady=30, sticky="ew")
        self.header_frame.grid_columnconfigure(1, weight=1)
        
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text=self.t['title'], 
            font=self.title_font,
            text_color=("#0D47A1", "#42A5F5")
        )
        self.title_label.grid(row=0, column=0, sticky="w")
        
        self.button_container = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.button_container.grid(row=0, column=2, sticky="e")
        
        self.refresh_button = ctk.CTkButton(
            self.button_container, 
            text="↻", 
            command=self.refresh_data,
            width=50, 
            height=42, 
            font=ctk.CTkFont(size=20, weight="bold"), 
            corner_radius=12,
            fg_color=("#4CAF50", "#388E3C"),
            hover_color=("#45A049", "#2E7D32")
        )
        self.refresh_button.grid(row=0, column=0, padx=(0, 10))
        
        self.toggle_button = ctk.CTkButton(
            self.button_container, 
            text=self.t['light_mode'], 
            command=self.toggle_theme_with_delay,
            width=150, 
            height=42, 
            font=self.button_font, 
            corner_radius=12,
            fg_color=("#2196F3", "#1976D2"),
            hover_color=("#1976D2", "#1565C0")
        )
        self.toggle_button.grid(row=0, column=1)
        
        self.loading_label = ctk.CTkLabel(
            self.glass_frame, 
            text=self.t['analyzing'], 
            font=self.section_title_font,
            text_color=("#1565C0", "#42A5F5")
        )
        self.loading_label.grid(row=1, column=0, pady=20, sticky="ew")
        
        self.progress_bar = ctk.CTkProgressBar(
            self.glass_frame, 
            mode="indeterminate", 
            height=10, 
            corner_radius=5,
            progress_color=("#2196F3", "#42A5F5")
        )
        self.progress_bar.grid(row=2, column=0, padx=30, pady=(0, 30), sticky="new")
        self.progress_bar.start()

        self.info_scroll_frame = ctk.CTkScrollableFrame(
            self.glass_frame, 
            fg_color="transparent",
            scrollbar_button_color=("#BDBDBD", "#4A4A4A"),
            scrollbar_button_hover_color=("#9E9E9E", "#6A6A6A")
        )
        self.info_scroll_frame.grid_columnconfigure(0, weight=1)
        
        self.footer_label = ctk.CTkLabel(
            self.glass_frame, 
            text=self.t['footer'],
            font=self.footer_font, 
            text_color=("#757575", "#9E9E9E")
        )
        self.footer_label.grid(row=3, column=0, pady=20, sticky="s")

        self.start_data_load()

    def refresh_data(self):
        if self.is_refreshing:
            return
        
        self.is_refreshing = True
        self.refresh_button.configure(state="disabled", text="↻")
        
        for widget in self.info_scroll_frame.winfo_children():
            widget.destroy()
        
        self.loading_label.configure(text=self.t['refreshing'])
        self.loading_label.grid(row=1, column=0, pady=20, sticky="ew")
        self.progress_bar.grid(row=2, column=0, padx=30, pady=(0, 30), sticky="new")
        self.progress_bar.start()
        self.info_scroll_frame.grid_forget()
        
        self.start_data_load()

    def toggle_theme_with_delay(self):
        if self.theme_changing:
            return
            
        self.theme_changing = True
        self.is_dark_mode = not self.is_dark_mode
        self.toggle_button.configure(state="disabled")
        
        for i in range(3, 0, -1):
            self.after((3-i) * 1000, lambda i=i: self.update_button_text(i))
        
        self.after(3000, self.apply_theme)

    def update_button_text(self, i):
        if hasattr(self, 'toggle_button') and self.toggle_button.winfo_exists():
            self.toggle_button.configure(text=self.t['changing_in'].format(i))

    def apply_theme(self):
        if not hasattr(self, 'toggle_button') or not self.toggle_button.winfo_exists():
            return
            
        if self.is_dark_mode:
            ctk.set_appearance_mode("Dark")
            self.toggle_button.configure(text=self.t['light_mode'])
        else:
            ctk.set_appearance_mode("Light")
            self.toggle_button.configure(text=self.t['dark_mode'])
        
        self.toggle_button.configure(state="normal")
        self.theme_changing = False

    def start_data_load(self):
        thread = threading.Thread(target=self.load_data_in_background, daemon=True)
        thread.start()

    def load_data_in_background(self):
        info_sections = get_system_info()
        self.after(0, self.update_gui, info_sections)

    def update_gui(self, info_sections):
        if not hasattr(self, 'progress_bar'):
            return
            
        self.progress_bar.stop()
        self.progress_bar.grid_forget()
        self.loading_label.grid_forget()
        
        self.info_scroll_frame.grid(row=1, column=0, rowspan=2, padx=30, pady=(0, 20), sticky="nsew")

        row_idx = 0
        
        for title, content in info_sections.items():
            
            section_frame = ctk.CTkFrame(
                self.info_scroll_frame,
                fg_color=("#F5F5F5", "#252525"),
                corner_radius=15,
                border_width=2,
                border_color=("#E0E0E0", "#353535")
            )
            section_frame.grid(row=row_idx, column=0, sticky="ew", pady=(0, 15), padx=5)
            section_frame.grid_columnconfigure(0, weight=1)
            
            section_label = ctk.CTkLabel(
                section_frame, 
                text=title, 
                font=self.section_title_font,
                anchor="w",
                text_color=("#0D47A1", "#42A5F5")
            )
            section_label.grid(row=0, column=0, sticky="ew", padx=15, pady=12)
            
            content_label = ctk.CTkLabel(
                section_frame, 
                text=content, 
                font=self.info_text_font,
                wraplength=680, 
                justify="left", 
                anchor="nw",
                text_color=("#424242", "#E0E0E0")
            )
            content_label.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))
            
            row_idx += 1
        
        if hasattr(self, 'refresh_button') and self.refresh_button.winfo_exists():
            self.refresh_button.configure(state="normal", text="↻")
        self.is_refreshing = False

if __name__ == "__main__":
    generate_gradient_image(800, 900, (20, 25, 35), (10, 15, 25), "gradient_bg_dark.png")
    generate_gradient_image(800, 900, (248, 249, 252), (235, 237, 242), "gradient_bg_light.png")

    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    app = ZInformationApp()
    app.mainloop()