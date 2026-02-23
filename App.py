"""
eyoTools Main Application
Central hub for all utility tools with Dark Mode and Multi-language support
Bilingual: English and Amharic
"""

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.uix.switch import Switch
from kivy.uix.spinner import Spinner
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty, ListProperty
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.core.text import LabelBase
import os
import sys

# Add functions directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'functions'))

# Import tool screens
try:
    from functions.youtube_dl import YouTubeDownloaderScreen
    from functions.bg_remover import BackgroundRemoverScreen
    from functions.pdf_tools import PDFExtractorScreen, PDFToAudioScreen
    from functions.ocr_tool import OCRScreen
    from functions.qr_tool import QRGeneratorScreen
    from functions.steganography import SteganographyScreen
    TOOLS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some tools could not be imported: {e}")
    TOOLS_AVAILABLE = False

# Register Amharic font if available
FONT_REGISTERED = False
try:
    # Check multiple possible font paths
    font_paths = [
        os.path.join(os.path.dirname(__file__), 'fonts', 'AbyssinicaSIL-Regular.ttf'),
        os.path.join(os.path.dirname(__file__), 'fonts', 'abyssinica.ttf'),
        os.path.join(os.path.dirname(__file__), 'fonts', 'Abyssinica.ttf'),
        'fonts/AbyssinicaSIL-Regular.ttf',
        'fonts/abyssinica.ttf'
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            LabelBase.register(name='Abyssinica', fn_regular=font_path)
            FONT_REGISTERED = True
            print(f"Amharic font loaded from: {font_path}")
            break
    
    if not FONT_REGISTERED:
        print("Amharic font not found. Please place AbyssinicaSIL-Regular.ttf in the fonts/ folder.")
except Exception as e:
    print(f"Error loading Amharic font: {e}")

# Language strings
STRINGS = {
    'en': {
        'app_name': 'eyoTools',
        'home': 'Home',
        'tools': 'Tools',
        'settings': 'Settings',
        'dark_mode': 'Dark Mode',
        'light_mode': 'Light Mode',
        'language': 'Language',
        'english': 'English',
        'amharic': 'አማርኛ',
        'about': 'About',
        'contact': 'Contact',
        'developer': 'Developer Info',
        'version': 'Version 1.0.0',
        'youtube': 'YouTube\nDownloader',
        'bg_remover': 'Background\nRemover',
        'pdf_extract': 'PDF to\nText',
        'pdf_audio': 'PDF to\nAudio',
        'ocr': 'Image to\nText (OCR)',
        'qr': 'QR Code\nGenerator',
        'steganography': 'Steganography',
        'loading': 'Loading...',
        'welcome': 'Welcome to eyoTools',
        'select_tool': 'Select a tool to get started',
        'ok': 'OK',
        'cancel': 'Cancel',
        'message': 'Message'
    },
    'am': {
        'app_name': 'ኢዮ መሳሪያዎች',
        'home': 'መነሻ',
        'tools': 'መሳሪያዎች',
        'settings': 'ማስተካከያ',
        'dark_mode': 'ጨለማ ሁነታ',
        'light_mode': 'ብርሃን ሁነታ',
        'language': 'ቋንቋ',
        'english': 'እንግሊዝኛ',
        'amharic': 'አማርኛ',
        'about': 'ስለ እኛ',
        'contact': 'መገናኛ',
        'developer': 'ገንቢ መረጃ',
        'version': 'እትም 1.0.0',
        'youtube': 'ዩቲዩብ\nአውራጅ',
        'bg_remover': 'ዳራ\nአስወጋጅ',
        'pdf_extract': 'PDF ወደ\nጽሁፍ',
        'pdf_audio': 'PDF ወደ\nድምጽ',
        'ocr': 'ምስል ወደ\nጽሁፍ',
        'qr': 'QR ኮድ\nአመንጪ',
        'steganography': 'ስውር መልእክት',
        'loading': 'በመጫን ላይ...',
        'welcome': 'እንኳን ወደ ኢዮ መሳሪያዎች በደህና መጡ',
        'select_tool': 'ለመጀመር መሳሪያ ይምረጡ',
        'ok': 'እሺ',
        'cancel': 'ሰርዝ',
        'message': 'መልእክት'
    }
}

# Custom button class for tool cards
class ToolCard(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_size = '16sp'
        self.background_normal = ''
        self.size_hint_y = None
        self.height = dp(150)
        self.text_size = (self.width, None)
        self.halign = 'center'
        self.valign = 'middle'
        self.bind(pos=self.update_text_size, size=self.update_text_size)
    
    def update_text_size(self, *args):
        self.text_size = (self.width * 0.9, None)

# Check if assets exist
LOGO_EXISTS = os.path.exists(os.path.join('assets', 'logo.png'))
SPLASH_EXISTS = os.path.exists(os.path.join('assets', 'splash.png'))

Builder.load_string('''
<SplashScreen>:
    canvas:
        Color:
            rgba: (0.1, 0.1, 0.1, 1) if app.dark_mode else (0.95, 0.95, 0.95, 1)
        Rectangle:
            pos: self.pos
            size: self.size
    
    BoxLayout:
        orientation: 'vertical'
        spacing: 20
        padding: 20
        
        RelativeLayout:
            size_hint_y: 0.8
            
            Image:
                id: logo
                source: 'assets/logo.png' if app.logo_exists else ''
                size_hint: None, None
                size: dp(200), dp(200)
                pos_hint: {'center_x': 0.5, 'center_y': 0.6}
                allow_stretch: True
                keep_ratio: True
            
            Label:
                id: app_name
                text: app.get_string('app_name')
                font_size: '32sp'
                bold: True
                color: (1, 1, 1, 1) if app.dark_mode else (0.1, 0.1, 0.1, 1)
                pos_hint: {'center_x': 0.5, 'center_y': 0.3}
        
        ProgressBar:
            id: progress
            max: 100
            size_hint_x: 0.8
            size_hint_y: 0.1
            pos_hint: {'center_x': 0.5}
            color: (0.2, 0.6, 0.8, 1)
        
        Label:
            id: loading_label
            text: app.get_string('loading')
            font_size: '16sp'
            color: (0.8, 0.8, 0.8, 1) if app.dark_mode else (0.3, 0.3, 0.3, 1)
            size_hint_y: 0.1

<HomeScreen>:
    canvas:
        Color:
            rgba: (0.95, 0.95, 0.95, 1) if not app.dark_mode else (0.15, 0.15, 0.15, 1)
        Rectangle:
            pos: self.pos
            size: self.size
    
    BoxLayout:
        orientation: 'vertical'
        spacing: 10
        padding: [15, 30, 15, 15]
        
        # Header
        BoxLayout:
            size_hint_y: 0.1
            spacing: 10
            
            Button:
                text: 'menu'
                font_size: '24sp'
                size_hint_x: 0.15
                background_normal: ''
                background_color: (0.2, 0.6, 0.8, 1)
                color: 1, 1, 1, 1
                on_release: root.toggle_menu()
            
            Label:
                text: app.get_string('app_name')
                font_size: '24sp'
                bold: True
                color: (0.2, 0.2, 0.2, 1) if not app.dark_mode else (1, 1, 1, 1)
                size_hint_x: 0.7
                text_size: self.size
                halign: 'center'
                valign: 'middle'
            
            BoxLayout:
                size_hint_x: 0.15
        
        # Welcome Message
        Label:
            text: app.get_string('welcome')
            font_size: '20sp'
            color: (0.3, 0.3, 0.3, 1) if not app.dark_mode else (0.8, 0.8, 0.8, 1)
            size_hint_y: 0.1
            text_size: self.size
            halign: 'center'
            valign: 'middle'
        
        # Tools Grid
        ScrollView:
            size_hint_y: 0.7
            do_scroll_x: False
            do_scroll_y: True
            
            GridLayout:
                id: tools_grid
                cols: 2
                spacing: dp(15)
                padding: dp(10)
                size_hint_y: None
                height: self.minimum_height
        
        # Footer
        Label:
            text: app.get_string('select_tool')
            font_size: '14sp'
            color: (0.5, 0.5, 0.5, 1) if not app.dark_mode else (0.6, 0.6, 0.6, 1)
            size_hint_y: 0.1
            text_size: self.size
            halign: 'center'
            valign: 'middle'

<NavigationMenu>:
    size_hint_x: 0.8
    canvas:
        Color:
            rgba: (1, 1, 1, 1) if not app.dark_mode else (0.2, 0.2, 0.2, 1)
        Rectangle:
            pos: self.pos
            size: self.size
    
    BoxLayout:
        orientation: 'vertical'
        spacing: 5
        padding: [15, 30, 15, 15]
        
        # Header
        BoxLayout:
            size_hint_y: 0.15
            orientation: 'vertical'
            spacing: 10
            
            Label:
                text: app.get_string('app_name')
                font_size: '28sp'
                bold: True
                color: (0.2, 0.2, 0.2, 1) if not app.dark_mode else (1, 1, 1, 1)
                text_size: self.size
                halign: 'center'
                valign: 'middle'
            
            Label:
                text: app.get_string('version')
                font_size: '12sp'
                color: (0.5, 0.5, 0.5, 1) if not app.dark_mode else (0.7, 0.7, 0.7, 1)
                size_hint_y: 0.3
        
        # Tools Section
        BoxLayout:
            size_hint_y: 0.4
            orientation: 'vertical'
            spacing: 5
            
            Label:
                text: app.get_string('tools')
                font_size: '18sp'
                bold: True
                color: (0.2, 0.6, 0.8, 1)
                size_hint_y: 0.1
                text_size: self.size
                halign: 'left'
                valign: 'middle'
            
            ScrollView:
                size_hint_y: 0.9
                do_scroll_x: False
                do_scroll_y: True
                
                BoxLayout:
                    id: tools_list
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: 2
        
        # Settings Section
        BoxLayout:
            size_hint_y: 0.25
            orientation: 'vertical'
            spacing: 5
            
            Label:
                text: app.get_string('settings')
                font_size: '18sp'
                bold: True
                color: (0.2, 0.6, 0.8, 1)
                size_hint_y: 0.2
                text_size: self.size
                halign: 'left'
                valign: 'middle'
            
            # Dark Mode Toggle
            BoxLayout:
                size_hint_y: 0.3
                spacing: 10
                
                Label:
                    text: app.get_string('dark_mode') if app.dark_mode else app.get_string('light_mode')
                    color: (0.2, 0.2, 0.2, 1) if not app.dark_mode else (1, 1, 1, 1)
                    size_hint_x: 0.6
                    text_size: self.size
                    halign: 'left'
                    valign: 'middle'
                
                Switch:
                    id: dark_mode_switch
                    active: app.dark_mode
                    on_active: app.toggle_dark_mode()
                    size_hint_x: 0.4
            
            # Language Selection
            BoxLayout:
                size_hint_y: 0.3
                spacing: 10
                
                Label:
                    text: app.get_string('language')
                    color: (0.2, 0.2, 0.2, 1) if not app.dark_mode else (1, 1, 1, 1)
                    size_hint_x: 0.6
                    text_size: self.size
                    halign: 'left'
                    valign: 'middle'
                
                Spinner:
                    id: lang_spinner
                    text: app.get_string('english') if app.current_lang == 'en' else app.get_string('amharic')
                    values: [app.get_string('english'), app.get_string('amharic')]
                    size_hint_x: 0.4
                    on_text: root.on_language_select(self.text)
        
        # Info Buttons
        BoxLayout:
            size_hint_y: 0.2
            orientation: 'vertical'
            spacing: 2
            
            Button:
                text: app.get_string('about')
                background_normal: ''
                background_color: (0.9, 0.9, 0.9, 1) if not app.dark_mode else (0.3, 0.3, 0.3, 1)
                color: (0.2, 0.2, 0.2, 1) if not app.dark_mode else (1, 1, 1, 1)
                size_hint_y: 0.3
                on_release: root.show_about()
            
            Button:
                text: app.get_string('contact')
                background_normal: ''
                background_color: (0.9, 0.9, 0.9, 1) if not app.dark_mode else (0.3, 0.3, 0.3, 1)
                color: (0.2, 0.2, 0.2, 1) if not app.dark_mode else (1, 1, 1, 1)
                size_hint_y: 0.3
                on_release: root.show_contact()
            
            Button:
                text: app.get_string('developer')
                background_normal: ''
                background_color: (0.9, 0.9, 0.9, 1) if not app.dark_mode else (0.3, 0.3, 0.3, 1)
                color: (0.2, 0.2, 0.2, 1) if not app.dark_mode else (1, 1, 1, 1)
                size_hint_y: 0.3
                on_release: root.show_developer()
''')


class SplashScreen(Screen):
    """Enhanced splash screen with professional animation"""
    
    def on_enter(self):
        """Start animations when screen enters"""
        # Initial setup
        logo = self.ids.logo
        app_name = self.ids.app_name
        progress = self.ids.progress
        
        # Set initial states
        logo.opacity = 0
        logo.scale = 0.5
        app_name.opacity = 0
        progress.value = 0
        
        # Create fade-in and scale-up animation for logo
        anim_logo = Animation(opacity=1, scale=1, duration=1.5, t='out_elastic')
        anim_logo.start(logo)
        
        # Animate app name with slight delay
        Clock.schedule_once(lambda dt: Animation(opacity=1, duration=1).start(app_name), 0.8)
        
        # Animate progress bar smoothly
        anim_progress = Animation(value=100, duration=2.5, t='linear')
        anim_progress.start(progress)
        
        # Schedule transition to home screen
        Clock.schedule_once(self.go_to_home, 3)
    
    def go_to_home(self, dt):
        """Transition to home screen with fade"""
        self.manager.transition.direction = 'left'
        self.manager.current = 'home'


class NavigationMenu(BoxLayout):
    """Slide-out navigation menu"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        Clock.schedule_once(self.create_tools_list, 0)
    
    def create_tools_list(self, dt=None):
        """Create tools menu items"""
        tools = [
            ('youtube', 'YouTube Downloader', 'youtube_dl'),
            ('bg_remover', 'Background Remover', 'bg_remover'),
            ('pdf_extract', 'PDF to Text', 'pdf_extract'),
            ('pdf_audio', 'PDF to Audio', 'pdf_audio'),
            ('ocr', 'Image to Text', 'ocr'),
            ('qr', 'QR Generator', 'qr'),
            ('steganography', 'Steganography', 'steganography')
        ]
        
        self.ids.tools_list.clear_widgets()
        
        for tool_id, tool_name_en, screen_name in tools:
            btn = Button(
                text=self.app.get_string(tool_id) if tool_id in ['youtube', 'bg_remover', 'pdf_extract', 'pdf_audio', 'ocr', 'qr', 'steganography'] else tool_name_en,
                size_hint_y=None,
                height=dp(50),
                background_normal='',
                background_color=(0.95, 0.95, 0.95, 1) if not self.app.dark_mode else (0.25, 0.25, 0.25, 1),
                color=(0.2, 0.2, 0.2, 1) if not self.app.dark_mode else (1, 1, 1, 1)
            )
            btn.bind(on_release=lambda x, s=screen_name: self.open_tool(s))
            self.ids.tools_list.add_widget(btn)
    
    def open_tool(self, screen_name):
        """Open selected tool screen"""
        self.app.root.current = screen_name
        self.app.toggle_menu()
    
    def on_language_select(self, text):
        """Handle language selection"""
        if text == self.app.get_string('amharic'):
            self.app.current_lang = 'am'
        else:
            self.app.current_lang = 'en'
        self.app.update_ui_language()
    
    def show_about(self):
        """Show about dialog"""
        self.app.show_info_dialog(self.app.get_string('about'), 
                                 'eyobTools - A collection of useful utilities\nVersion 1.0.0')
    
    def show_contact(self):
        """Show contact info"""
        self.app.show_info_dialog(self.app.get_string('contact'), 
                                 'Email: https://eyobbegashaw.vercel.app/')
    
    def show_developer(self):
        """Show developer info"""
        self.app.show_info_dialog(self.app.get_string('developer'), 
                                 'Developed by: Dn Eyob Begashaw\n© 2025 (2018) eyoTools\nAll rights reserved.')


class HomeScreen(Screen):
    """Home screen with tools grid"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.menu = None
    
    def on_pre_enter(self):
        """Called before screen enters"""
        self.app = App.get_running_app()
        # Set a reference to the app for tool screens that might try to access it
        self.manager_app = self.app
        self.create_tools_grid()
    
    def create_tools_grid(self):
        """Create grid of tool cards"""
        self.ids.tools_grid.clear_widgets()
        
        tools = [
            ('youtube', self.app.get_string('youtube'), 'youtube_dl'),
            ('bg_remover', self.app.get_string('bg_remover'), 'bg_remover'),
            ('pdf_extract', self.app.get_string('pdf_extract'), 'pdf_extract'),
            ('pdf_audio', self.app.get_string('pdf_audio'), 'pdf_audio'),
            ('ocr', self.app.get_string('ocr'), 'ocr'),
            ('qr', self.app.get_string('qr'), 'qr'),
            ('steganography', self.app.get_string('steganography'), 'steganography')
        ]
        
        for tool_id, tool_name, screen_name in tools:
            btn = ToolCard()
            btn.text = tool_name
            btn.font_name = 'Abyssinica' if self.app.current_lang == 'am' and self.app.FONT_REGISTERED else 'Roboto'
            btn.background_color = (1, 1, 1, 1) if not self.app.dark_mode else (0.25, 0.25, 0.25, 1)
            btn.color = (0.2, 0.2, 0.2, 1) if not self.app.dark_mode else (1, 1, 1, 1)
            btn.bind(on_release=lambda x, s=screen_name: self.open_tool(s))
            self.ids.tools_grid.add_widget(btn)
    
    def open_tool(self, screen_name):
        """Open selected tool"""
        self.manager.current = screen_name
    
    def toggle_menu(self):
        """Toggle navigation menu"""
        if not self.menu:
            self.menu = NavigationMenu()
            self.menu.pos_hint = {'x': -1}
            Window.add_widget(self.menu)
        
        # Animate menu
        if self.menu.pos_hint['x'] < 0:
            anim = Animation(pos_hint={'x': 0}, duration=0.3)
        else:
            anim = Animation(pos_hint={'x': -1}, duration=0.3)
        anim.start(self.menu)


class eyoToolsApp(App):
    """Main application class"""
    
    # Global properties
    dark_mode = BooleanProperty(False)
    current_lang = StringProperty('en')
    FONT_REGISTERED = FONT_REGISTERED
    logo_exists = LOGO_EXISTS
    
    def build(self):
        """Build the application"""
        # Set window size for desktop
        Window.size = (400, 700)
        
        # Create screen manager
        self.sm = ScreenManager(transition=FadeTransition())
        
        # Add splash screen
        self.sm.add_widget(SplashScreen(name='splash'))
        
        # Add home screen
        self.sm.add_widget(HomeScreen(name='home'))
        
        # Add tool screens if available
        if TOOLS_AVAILABLE:
            try:
                # Create tool screens and pass app reference
                youtube_screen = YouTubeDownloaderScreen(name='youtube_dl')
                youtube_screen.app = self
                self.sm.add_widget(youtube_screen)
                
                bg_screen = BackgroundRemoverScreen(name='bg_remover')
                bg_screen.app = self
                self.sm.add_widget(bg_screen)
                
                pdf_extract_screen = PDFExtractorScreen(name='pdf_extract')
                pdf_extract_screen.app = self
                self.sm.add_widget(pdf_extract_screen)
                
                pdf_audio_screen = PDFToAudioScreen(name='pdf_audio')
                pdf_audio_screen.app = self
                self.sm.add_widget(pdf_audio_screen)
                
                ocr_screen = OCRScreen(name='ocr')
                ocr_screen.app = self
                self.sm.add_widget(ocr_screen)
                
                qr_screen = QRGeneratorScreen(name='qr')
                qr_screen.app = self
                self.sm.add_widget(qr_screen)
                
                steg_screen = SteganographyScreen(name='steganography')
                steg_screen.app = self
                self.sm.add_widget(steg_screen)
                
            except Exception as e:
                print(f"Error loading tools: {e}")
        
        return self.sm
    
    def get_string(self, key):
        """Get string in current language"""
        return STRINGS[self.current_lang].get(key, STRINGS['en'].get(key, key))
    
    def toggle_dark_mode(self):
        """Toggle dark mode"""
        self.dark_mode = not self.dark_mode
        self.update_ui_theme()
    
    def update_ui_theme(self):
        """Update UI theme for all screens"""
        # Update home screen
        home = self.sm.get_screen('home')
        if home:
            home.create_tools_grid()
        
        # Update navigation menu if exists
        if hasattr(home, 'menu') and home.menu:
            home.menu.create_tools_list()
        
        # Update all tool screens
        for screen in self.sm.screens:
            if hasattr(screen, 'update_ui_language'):
                screen.update_ui_language()
            if hasattr(screen, 'update_fonts'):
                screen.update_fonts()
    
    def update_ui_language(self):
        """Update language for all screens"""
        # Update home screen
        home = self.sm.get_screen('home')
        if home:
            home.create_tools_grid()
        
        # Update navigation menu if exists
        if hasattr(home, 'menu') and home.menu:
            home.menu.create_tools_list()
        
        # Update all tool screens
        for screen in self.sm.screens:
            if hasattr(screen, 'update_ui_language'):
                screen.update_ui_language()
            if hasattr(screen, 'update_fonts'):
                screen.update_fonts()
    
    def get_storage_path(self, folder):
        """Get storage path for files"""
        base_path = os.path.join(os.path.expanduser('~'), 'eyoTools')
        path = os.path.join(base_path, folder)
        os.makedirs(path, exist_ok=True)
        return path
    
    def show_info_dialog(self, title, message):
        """Show information dialog"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        label = Label(text=message, text_size=(Window.width * 0.7, None))
        if self.current_lang == 'am' and self.FONT_REGISTERED:
            label.font_name = 'Abyssinica'
        content.add_widget(label)
        
        btn = Button(text=self.get_string('ok'), size_hint_y=0.3)
        content.add_widget(btn)
        
        popup = Popup(title=title, content=content, size_hint=(0.8, 0.4))
        btn.bind(on_release=popup.dismiss)
        popup.open()
    
    def toggle_menu(self):
        """Close menu if open"""
        home = self.sm.get_screen('home')
        if home and hasattr(home, 'menu') and home.menu:
            if home.menu.pos_hint['x'] >= 0:
                anim = Animation(pos_hint={'x': -1}, duration=0.3)
                anim.start(home.menu)


if __name__ == '__main__':
    eyoToolsApp().run()