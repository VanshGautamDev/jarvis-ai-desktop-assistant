
"""
System Controller Module for JARVIS
Handles system-level operations like file management, app control, media playback
"""

import os
import subprocess
import platform
import logging
import webbrowser
import psutil
import pyautogui
import time
from pathlib import Path
import json
import glob
import shutil

class SystemController:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.system = platform.system().lower()
        self.music_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.wma']
        self.video_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm']
        self.image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.svg']
        
        # Common application paths
        self.app_paths = self._get_common_app_paths()
        
        self.logger.info(f"System controller initialized for {self.system}")
    
    def _get_common_app_paths(self):
        """Get common application paths for different operating systems"""
        paths = {}
        
        if self.system == "windows":
            username = os.getenv('USERNAME', '')
            
            # Standard Windows applications
            paths = {
                'notepad': 'notepad.exe',
                'calculator': 'calc.exe',
                'paint': 'mspaint.exe',
                'browser': 'start',
                'explorer': 'explorer.exe',
                'cmd': 'cmd.exe',
                'powershell': 'powershell.exe',
                'task_manager': 'taskmgr.exe',
                'control_panel': 'control.exe',
            }
            
            # Try to find common applications in typical locations
            app_locations = {
                'chrome': [
                    r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                    r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
                    rf'C:\Users\{username}\AppData\Local\Google\Chrome\Application\chrome.exe'
                ],
                'firefox': [
                    r'C:\Program Files\Mozilla Firefox\firefox.exe',
                    r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe'
                ],
                'vlc': [
                    r'C:\Program Files\VideoLAN\VLC\vlc.exe',
                    r'C:\Program Files (x86)\VideoLAN\VLC\vlc.exe'
                ],
                'spotify': [
                    rf'C:\Users\{username}\AppData\Roaming\Spotify\Spotify.exe',
                    rf'C:\Users\{username}\AppData\Local\Microsoft\WindowsApps\Spotify.exe',
                    r'C:\Program Files\WindowsApps\SpotifyAB.SpotifyMusic_*\Spotify.exe'
                ],
                'discord': [
                    rf'C:\Users\{username}\AppData\Local\Discord\Update.exe --processStart Discord.exe',
                    rf'C:\Users\{username}\AppData\Local\Discord\app-*\Discord.exe',
                    rf'C:\Users\{username}\AppData\Roaming\discord\*\Discord.exe'
                ],
                'vscode': [
                    r'C:\Program Files\Microsoft VS Code\Code.exe',
                    r'C:\Program Files (x86)\Microsoft VS Code\Code.exe',
                    rf'C:\Users\{username}\AppData\Local\Programs\Microsoft VS Code\Code.exe'
                ],
                'whatsapp': [
                    rf'C:\Users\{username}\AppData\Local\WhatsApp\WhatsApp.exe',
                    rf'C:\Users\{username}\AppData\Local\Microsoft\WindowsApps\WhatsApp.exe'
                ]
            }
            
            # Find existing application paths
            for app_name, possible_paths in app_locations.items():
                for path in possible_paths:
                    if '*' in path:
                        # Handle wildcard paths
                        import glob
                        matches = glob.glob(path)
                        if matches:
                            paths[app_name] = matches[0]
                            break
                    elif os.path.exists(path):
                        paths[app_name] = path
                        break
                
                # If not found in standard locations, try to find via registry or start menu
                if app_name not in paths:
                    paths[app_name] = app_name  # Will attempt to find via search
            
        elif self.system == "darwin":  # macOS
            paths = {
                'finder': 'open -a Finder',
                'safari': 'open -a Safari',
                'chrome': 'open -a "Google Chrome"',
                'firefox': 'open -a Firefox',
                'terminal': 'open -a Terminal',
                'calculator': 'open -a Calculator',
                'textedit': 'open -a TextEdit',
                'vlc': 'open -a VLC',
                'spotify': 'open -a Spotify',
                'vscode': 'open -a "Visual Studio Code"',
                'discord': 'open -a Discord',
                'whatsapp': 'open -a WhatsApp'
            }
        else:  # Linux
            paths = {
                'browser': 'xdg-open',
                'terminal': 'gnome-terminal',
                'calculator': 'gnome-calculator',
                'text_editor': 'gedit',
                'file_manager': 'nautilus',
                'chrome': 'google-chrome',
                'firefox': 'firefox',
                'vlc': 'vlc',
                'vscode': 'code',
                'spotify': 'spotify',
                'discord': 'discord'
            }
        
        return paths
    
    def open_application(self, app_name):
        """Open an application by name"""
        try:
            app_name_clean = app_name.lower().replace(' ', '_').replace('-', '_')
            
            self.logger.info(f"Attempting to open: {app_name} (cleaned: {app_name_clean})")
            
            # Check if we have a direct path
            if app_name_clean in self.app_paths:
                command = self.app_paths[app_name_clean]
                
                if self.system == "windows":
                    if command.endswith('.exe') and os.path.exists(command):
                        subprocess.Popen([command])
                    elif '--processStart' in command:
                        # Handle Discord-style commands
                        parts = command.split()
                        subprocess.Popen(parts)
                    else:
                        subprocess.Popen(command, shell=True)
                else:
                    subprocess.Popen(command, shell=True)
                
                self.logger.info(f"Opened application: {app_name}")
                return f"Opening {app_name}"
            
            # Try alternative app names
            app_aliases = {
                'spotify': ['spotify', 'spotify music'],
                'discord': ['discord'],
                'whatsapp': ['whatsapp', 'whats app'],
                'chrome': ['chrome', 'google chrome'],
                'firefox': ['firefox', 'mozilla firefox'],
                'vscode': ['vscode', 'vs code', 'visual studio code', 'code'],
                'calculator': ['calculator', 'calc'],
                'notepad': ['notepad', 'text editor']
            }
            
            # Find matching alias
            for key, aliases in app_aliases.items():
                if any(alias in app_name.lower() for alias in aliases):
                    if key in self.app_paths:
                        return self.open_application(key)
            
            # Try Windows-specific methods
            if self.system == "windows":
                # Try opening via Windows start command
                try:
                    subprocess.Popen(['start', '', app_name], shell=True)
                    return f"Attempting to open {app_name}"
                except:
                    pass
                
                # Try PowerShell Start-Process
                try:
                    subprocess.Popen(['powershell', 'Start-Process', app_name])
                    return f"Opening {app_name} via PowerShell"
                except:
                    pass
            
            # Last resort: search and open
            if self._find_and_open_app(app_name):
                return f"Found and opening {app_name}"
            else:
                return f"Could not find application: {app_name}. Try saying the exact application name."
                    
        except Exception as e:
            self.logger.error(f"Error opening application {app_name}: {e}")
            return f"Failed to open {app_name}: {str(e)}"
    
    def _find_and_open_app(self, app_name):
        """Try to find and open an application"""
        try:
            if self.system == "windows":
                # Search in common directories
                search_paths = [
                    r"C:\Program Files",
                    r"C:\Program Files (x86)",
                    os.path.expanduser("~\\AppData\\Local"),
                    os.path.expanduser("~\\AppData\\Roaming")
                ]
                
                for path in search_paths:
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            if app_name.lower() in file.lower() and file.endswith('.exe'):
                                full_path = os.path.join(root, file)
                                subprocess.Popen([full_path])
                                return True
                        # Limit search depth to avoid long searches
                        if root.count(os.sep) - path.count(os.sep) > 2:
                            break
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error finding application: {e}")
            return False
    
    def close_application(self, app_name):
        """Close an application by name"""
        try:
            app_name = app_name.lower()
            closed = False
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if app_name in proc.info['name'].lower():
                        proc.terminate()
                        closed = True
                        self.logger.info(f"Closed process: {proc.info['name']}")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if closed:
                return f"Closed {app_name}"
            else:
                return f"No running processes found for {app_name}"
                
        except Exception as e:
            self.logger.error(f"Error closing application {app_name}: {e}")
            return f"Failed to close {app_name}"
    
    def open_file(self, file_path):
        """Open a file with the default application"""
        try:
            if os.path.exists(file_path):
                if self.system == "windows":
                    os.startfile(file_path)
                elif self.system == "darwin":
                    subprocess.run(["open", file_path])
                else:
                    subprocess.run(["xdg-open", file_path])
                
                self.logger.info(f"Opened file: {file_path}")
                return f"Opening {os.path.basename(file_path)}"
            else:
                return f"File not found: {file_path}"
                
        except Exception as e:
            self.logger.error(f"Error opening file: {e}")
            return f"Failed to open file"
    
    def open_folder(self, folder_path):
        """Open a folder in file explorer"""
        try:
            if os.path.exists(folder_path):
                if self.system == "windows":
                    subprocess.run(["explorer", folder_path])
                elif self.system == "darwin":
                    subprocess.run(["open", folder_path])
                else:
                    subprocess.run(["xdg-open", folder_path])
                
                self.logger.info(f"Opened folder: {folder_path}")
                return f"Opening folder {os.path.basename(folder_path)}"
            else:
                return f"Folder not found: {folder_path}"
                
        except Exception as e:
            self.logger.error(f"Error opening folder: {e}")
            return f"Failed to open folder"
    
    def search_files(self, filename, search_path=None):
        """Search for files by name"""
        try:
            if search_path is None:
                search_path = os.path.expanduser("~")
            
            results = []
            pattern = f"**/*{filename}*"
            
            for file_path in glob.glob(os.path.join(search_path, pattern), recursive=True):
                if os.path.isfile(file_path):
                    results.append(file_path)
                if len(results) >= 10:  # Limit results
                    break
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching files: {e}")
            return []
    
    def play_media(self, file_path):
        """Play media file (audio/video)"""
        try:
            if not os.path.exists(file_path):
                return f"Media file not found: {file_path}"
            
            file_ext = Path(file_path).suffix.lower()
            
            if file_ext in self.music_extensions or file_ext in self.video_extensions:
                if self.system == "windows":
                    os.startfile(file_path)
                elif self.system == "darwin":
                    subprocess.run(["open", file_path])
                else:
                    subprocess.run(["xdg-open", file_path])
                
                self.logger.info(f"Playing media: {file_path}")
                return f"Playing {os.path.basename(file_path)}"
            else:
                return f"Unsupported media format: {file_ext}"
                
        except Exception as e:
            self.logger.error(f"Error playing media: {e}")
            return f"Failed to play media"
    
    def find_and_play_music(self, search_term):
        """Search and play music files"""
        try:
            # Common music directories
            music_dirs = [
                os.path.expanduser("~/Music"),
                os.path.expanduser("~/Downloads"),
                "C:/Users/{}/Music".format(os.getenv('USERNAME', '')) if self.system == "windows" else None
            ]
            
            music_dirs = [d for d in music_dirs if d and os.path.exists(d)]
            
            for music_dir in music_dirs:
                for ext in self.music_extensions:
                    pattern = f"**/*{search_term}*{ext}"
                    matches = glob.glob(os.path.join(music_dir, pattern), recursive=True)
                    
                    if matches:
                        # Play first match
                        return self.play_media(matches[0])
            
            return f"No music found matching: {search_term}"
            
        except Exception as e:
            self.logger.error(f"Error finding music: {e}")
            return f"Failed to find music"
    
    def open_website(self, url):
        """Open a website in the default browser"""
        try:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            webbrowser.open(url)
            self.logger.info(f"Opened website: {url}")
            return f"Opening {url}"
            
        except Exception as e:
            self.logger.error(f"Error opening website: {e}")
            return f"Failed to open website"
    
    def search_youtube(self, query):
        """Search and open YouTube with query"""
        try:
            search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            self.logger.info(f"Searching YouTube for: {query}")
            return f"Searching YouTube for {query}"
            
        except Exception as e:
            self.logger.error(f"Error searching YouTube: {e}")
            return f"Failed to search YouTube"
    
    def play_youtube_video(self, query):
        """Play first YouTube video matching query"""
        try:
            # This opens YouTube search - for actual video playing, you'd need youtube-dl or similar
            search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            
            # Simulate clicking first video (basic automation)
            time.sleep(3)  # Wait for page to load
            pyautogui.click(640, 350)  # Approximate position of first video
            
            self.logger.info(f"Playing YouTube video: {query}")
            return f"Playing {query} on YouTube"
            
        except Exception as e:
            self.logger.error(f"Error playing YouTube video: {e}")
            return f"Searching YouTube for {query}"
    
    def get_system_info(self):
        """Get system information"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            info = {
                'cpu': f"{cpu_percent}%",
                'memory': f"{memory.percent}%",
                'disk': f"{disk.percent}%",
                'system': platform.system(),
                'machine': platform.machine(),
                'processor': platform.processor()
            }
            
            return info
            
        except Exception as e:
            self.logger.error(f"Error getting system info: {e}")
            return {}
    
    def shutdown_system(self):
        """Shutdown the system"""
        try:
            if self.system == "windows":
                os.system("shutdown /s /t 1")
            elif self.system == "darwin":
                os.system("sudo shutdown -h now")
            else:
                os.system("sudo shutdown now")
                
            return "Shutting down system"
            
        except Exception as e:
            self.logger.error(f"Error shutting down: {e}")
            return "Failed to shutdown system"
    
    def restart_system(self):
        """Restart the system"""
        try:
            if self.system == "windows":
                os.system("shutdown /r /t 1")
            elif self.system == "darwin":
                os.system("sudo shutdown -r now")
            else:
                os.system("sudo reboot")
                
            return "Restarting system"
            
        except Exception as e:
            self.logger.error(f"Error restarting: {e}")
            return "Failed to restart system"
    
    def lock_screen(self):
        """Lock the screen"""
        try:
            if self.system == "windows":
                subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
            elif self.system == "darwin":
                subprocess.run(["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"])
            else:
                subprocess.run(["xdg-screensaver", "lock"])
                
            return "Screen locked"
            
        except Exception as e:
            self.logger.error(f"Error locking screen: {e}")
            return "Failed to lock screen"
    
    def adjust_volume(self, level):
        """Adjust system volume (0-100)"""
        try:
            level = max(0, min(100, level))  # Clamp between 0-100
            
            if self.system == "windows":
                # Try multiple methods for Windows volume control
                try:
                    # Method 1: Using PowerShell (most reliable)
                    ps_command = f"[audio]::Volume = {level/100}"
                    subprocess.run([
                        "powershell", 
                        "-c", 
                        f"Add-Type -TypeDefinition 'using System.Runtime.InteropServices; public class audio {{ [DllImport(\"user32.dll\")] public static extern int SendMessageW(int hWnd, int Msg, int wParam, int lParam); public static void SetVolume(int level) {{ SendMessageW(0xFFFF, 0x0319, 0x000A0000, level * 655); }} }}'; [audio]::SetVolume({level})"
                    ], check=True)
                except:
                    # Method 2: Using VBScript
                    vbs_script = f"""
                    Set oShell = CreateObject("WScript.Shell")
                    For i = 1 to 50
                        oShell.SendKeys(chr(174))
                    Next
                    For i = 1 to {level//2}
                        oShell.SendKeys(chr(175))
                    Next
                    """
                    with open("temp_volume.vbs", "w") as f:
                        f.write(vbs_script)
                    subprocess.run(["cscript", "//nologo", "temp_volume.vbs"])
                    os.remove("temp_volume.vbs")
                    
            elif self.system == "darwin":
                subprocess.run(["osascript", "-e", f"set volume output volume {level}"])
            else:
                subprocess.run(["amixer", "set", "Master", f"{level}%"])
                
            return f"Volume set to {level}%"
            
        except Exception as e:
            self.logger.error(f"Error adjusting volume: {e}")
            return "Volume adjustment failed - trying alternative method"
    
    def take_screenshot(self, filename=None):
        """Take a screenshot"""
        try:
            if filename is None:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            
            self.logger.info(f"Screenshot saved: {filename}")
            return f"Screenshot saved as {filename}"
            
        except Exception as e:
            self.logger.error(f"Error taking screenshot: {e}")
            return "Failed to take screenshot"
    
    def create_folder(self, folder_path):
        """Create a new folder"""
        try:
            os.makedirs(folder_path, exist_ok=True)
            self.logger.info(f"Created folder: {folder_path}")
            return f"Created folder {os.path.basename(folder_path)}"
            
        except Exception as e:
            self.logger.error(f"Error creating folder: {e}")
            return "Failed to create folder"
    
    def delete_file(self, file_path):
        """Delete a file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                self.logger.info(f"Deleted file: {file_path}")
                return f"Deleted {os.path.basename(file_path)}"
            else:
                return f"File not found: {file_path}"
                
        except Exception as e:
            self.logger.error(f"Error deleting file: {e}")
            return "Failed to delete file"
    
    def copy_file(self, source, destination):
        """Copy a file"""
        try:
            shutil.copy2(source, destination)
            self.logger.info(f"Copied file from {source} to {destination}")
            return f"Copied {os.path.basename(source)} to {destination}"
            
        except Exception as e:
            self.logger.error(f"Error copying file: {e}")
            return "Failed to copy file"
    
    def move_file(self, source, destination):
        """Move a file"""
        try:
            shutil.move(source, destination)
            self.logger.info(f"Moved file from {source} to {destination}")
            return f"Moved {os.path.basename(source)} to {destination}"
            
        except Exception as e:
            self.logger.error(f"Error moving file: {e}")
            return "Failed to move file"

# Test function
if __name__ == "__main__":
    controller = SystemController()
    
    print("Testing system controller...")
    print("System info:", controller.get_system_info())
    print("Opening calculator...")
    print(controller.open_application("calculator"))