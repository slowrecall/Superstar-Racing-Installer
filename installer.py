import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import requests
import os
from pathlib import Path
import sys
import logging
import subprocess
from datetime import datetime
import time
import sys
from pathlib import Path

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

class SplashScreen:
    def __init__(self):
        self.root = tk.Tk()
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.attributes('-alpha', 0.0)  # Start fully transparent
        
        # Load hero image with transparency and resize
        hero_path = get_resource_path(os.path.join('resources', 'Hero.png'))
        hero_img = Image.open(hero_path)
        hero_img = hero_img.convert('RGBA')
        # Resize the hero image to 80% of its original size
        new_width = int(hero_img.width * 0.5)
        new_height = int(hero_img.height * 0.5)
        hero_img = hero_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.hero_photo = ImageTk.PhotoImage(hero_img)
        
        # Calculate window size and position
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = hero_img.width
        window_height = hero_img.height
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Configure window and label for transparency
        self.root.attributes('-transparentcolor', '#000001')
        self.root.configure(bg='#000001')
        self.hero_label = tk.Label(self.root, image=self.hero_photo, bg='#000001')
        self.hero_label.pack()
        
        # Initialize animation variables
        self.alpha = 0.0
        self.y_offset = 0
        self.start_y = y
        
        # Start fade-in animation
        self.animate_fade_in()
        
    def animate_fade_in(self):
        if self.alpha < 1.0:
            self.alpha += 0.05
            self.root.attributes('-alpha', self.alpha)
            self.root.after(20, self.animate_fade_in)
        else:
            self.animate_move_up()
    
    def animate_move_up(self):
        target_offset = -50  # Move up by 50 pixels
        if self.y_offset > target_offset:
            self.y_offset -= 2
            x = (self.root.winfo_screenwidth() - self.root.winfo_width()) // 2
            y = self.start_y + self.y_offset
            self.root.geometry(f"+{x}+{y}")
            self.root.after(20, self.animate_move_up)
        else:
            self.root.after(500, self.close)  # Wait half second before closing
    
    def close(self):
        self.root.destroy()
        launch_installer()

class InstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Superstar Racing Installer")
        self.root.resizable(False, False)

        # Set window icon
        icon_path = get_resource_path(os.path.join('resources', 'Icon.ico'))
        self.root.iconbitmap(icon_path)

        # Setup logging
        self.setup_logging()

        # Load and display banner
        banner_path = get_resource_path(os.path.join('resources', 'Banner.jpg'))
        banner_img = Image.open(banner_path)
        # Set window size based on banner dimensions
        window_width = banner_img.width
        window_height = banner_img.height + 100
        self.root.geometry(f"{window_width}x{window_height}")
        
        # Center the window on screen
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"+{x}+{y}")
        
        self.banner_photo = ImageTk.PhotoImage(banner_img)
        banner_label = tk.Label(root, image=self.banner_photo)
        banner_label.pack()

        # Create a frame for controls
        self.controls_frame = tk.Frame(root)
        self.controls_frame.pack(fill=tk.X, padx=20, pady=10)

        # Progress bar with style
        style = ttk.Style()
        style.configure("Custom.Horizontal.TProgressbar", thickness=20)
        self.progress = ttk.Progressbar(self.controls_frame, length=banner_img.width-80, mode='determinate', style="Custom.Horizontal.TProgressbar")
        self.progress.pack(pady=10, fill=tk.X)

        # Status label with custom font
        self.status_label = tk.Label(root, text="Ready to install", font=("Arial", 10))
        self.status_label.pack(pady=5)
        
        # Start installation automatically
        self.root.after(1000, self.start_installation)

    def setup_logging(self):
        log_dir = Path(os.path.expanduser("~")) / "Superstar Racing Launcher"
        log_dir.mkdir(exist_ok=True)
        log_file = log_dir / "log.txt"
        
        logging.basicConfig(
            filename=str(log_file),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def start_installation(self):
        try:
            self.status_label.config(text="Checking for existing installation...")
            logging.info("Checking for existing installation")
            
            # Create installation directory
            install_dir = Path(os.path.expanduser("~")) / "Superstar Racing Launcher"
            install_dir.mkdir(parents=True, exist_ok=True)
            file_path = install_dir / "Superstar Racing.exe"
            
            # Check if game is already installed
            if file_path.exists() and file_path.stat().st_size > 0:
                self.status_label.config(text="Game is already installed!")
                logging.info("Game is already installed")
                messagebox.showinfo("Already Installed", "Superstar Racing is already installed. Launching the game...")
                subprocess.Popen([str(file_path)], shell=True)
                self.root.quit()
                self.root.destroy()
                return
            
            logging.info(f"Created installation directory: {install_dir}")
            
            # Download URL
            url = "https://web.archive.org/web/20211117032231/http://superstarracing.net/download/Superstar%20Racing.exe"
            self.status_label.config(text="Downloading game...")
            logging.info("Starting game download")
            
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Get file size for progress calculation
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024  # 1 KB
            downloaded = 0
            
            file_path = install_dir / "Superstar Racing.exe"
            
            with open(file_path, 'wb') as f:
                for data in response.iter_content(block_size):
                    downloaded += len(data)
                    f.write(data)
                    # Update progress bar
                    if total_size:
                        progress = (downloaded / total_size) * 100
                        self.progress['value'] = progress
                        self.status_label.config(text=f"Downloading... {progress:.1f}%")
                        self.root.update_idletasks()
            
            logging.info("Download completed successfully")
            
            # Verify file exists and has size
            if file_path.exists() and file_path.stat().st_size > 0:
                self.status_label.config(text="Installation completed successfully! Launching game...")
                self.progress['value'] = 100
                logging.info("Installation completed successfully")
                
                # Launch the game
                subprocess.Popen([str(file_path)], shell=True)
                logging.info("Game launched")
                # Close the installer
                self.root.quit()
            else:
                raise Exception("Downloaded file is invalid or empty")
            
        except Exception as e:
            error_msg = f"Error during installation: {str(e)}"
            self.status_label.config(text=error_msg)
            logging.error(error_msg)
            messagebox.showerror("Installation Error", error_msg, icon=os.path.join(os.path.dirname(__file__), 'resources', 'Icon.ico'))
            self.progress['value'] = 0
            

def launch_installer():
    root = tk.Tk()
    app = InstallerApp(root)
    root.mainloop()

def main():
    splash = SplashScreen()
    splash.root.mainloop()

if __name__ == "__main__":
    main()