"""
QR Code Generator Tool
Generate QR codes from text or URLs
Bilingual: English and Amharic
"""

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty
from kivy.app import App
from threading import Thread
import os
from datetime import datetime

# Try to import qrcode
try:
    import qrcode
    from PIL import Image
    QRCODE_AVAILABLE = True
except ImportError:
    QRCODE_AVAILABLE = False

Builder.load_string('''
<QRGeneratorScreen>:
    canvas:
        Color:
            rgba: (0.1, 0.1, 0.1, 1) if app.dark_mode else (0.95, 0.95, 0.95, 1)
        Rectangle:
            pos: self.pos
            size: self.size
    
    BoxLayout:
        orientation: 'vertical'
        spacing: 10
        padding: 15
        
        # Top Bar
        BoxLayout:
            size_hint_y: 0.1
            spacing: 10
            
            Button:
                text: '←'
                font_size: '24sp'
                size_hint_x: 0.15
                background_normal: ''
                background_color: (0.3, 0.3, 0.3, 1)
                color: 1, 1, 1, 1
                on_release: root.go_back()
            
            Label:
                id: title_label
                text: ''
                font_size: '20sp'
                bold: True
                color: (1, 1, 1, 1) if app.dark_mode else (0.2, 0.2, 0.2, 1)
                size_hint_x: 0.7
                text_size: self.size
                halign: 'center'
                valign: 'middle'
            
            BoxLayout:
                size_hint_x: 0.15
        
        # Input Section
        BoxLayout:
            size_hint_y: 0.2
            orientation: 'vertical'
            spacing: 5
            
            Label:
                id: input_label
                text: ''
                font_size: '16sp'
                color: (1, 1, 1, 1) if app.dark_mode else (0.2, 0.2, 0.2, 1)
                size_hint_y: 0.2
                text_size: self.size
                halign: 'left'
                valign: 'middle'
            
            TextInput:
                id: text_input
                size_hint_y: 0.6
                multiline: True
                text: ''
                hint_text: ''
                background_color: (0.2, 0.2, 0.2, 1) if app.dark_mode else (1, 1, 1, 1)
                foreground_color: (1, 1, 1, 1) if app.dark_mode else (0, 0, 0, 1)
                hint_text_color: (0.6, 0.6, 0.6, 1) if app.dark_mode else (0.5, 0.5, 0.5, 1)
            
            Button:
                id: generate_btn
                text: ''
                size_hint_y: 0.2
                background_normal: ''
                background_color: (0.2, 0.6, 0.8, 1)
                color: 1, 1, 1, 1
                on_release: root.generate_qr()
                disabled: not root.can_generate
        
        # QR Code Preview
        BoxLayout:
            size_hint_y: 0.5
            orientation: 'vertical'
            spacing: 5
            
            Label:
                id: preview_label
                text: ''
                font_size: '16sp'
                color: (1, 1, 1, 1) if app.dark_mode else (0.2, 0.2, 0.2, 1)
                size_hint_y: 0.1
            
            BoxLayout:
                size_hint_y: 0.9
                canvas:
                    Color:
                        rgba: (0.2, 0.2, 0.2, 1) if app.dark_mode else (0.8, 0.8, 0.8, 1)
                    Rectangle:
                        pos: self.pos
                        size: self.size
                
                Image:
                    id: qr_image
                    source: root.qr_path if root.qr_path else ''
                    allow_stretch: True
                    keep_ratio: True
        
        # Action Buttons
        BoxLayout:
            size_hint_y: 0.15
            spacing: 10
            orientation: 'vertical'
            
            BoxLayout:
                size_hint_y: 0.5
                spacing: 10
                
                Button:
                    id: save_btn
                    text: ''
                    background_normal: ''
                    background_color: (0.4, 0.4, 0.8, 1)
                    color: 1, 1, 1, 1
                    on_release: root.save_qr()
                    disabled: not root.qr_path
                
                Button:
                    id: copy_btn
                    text: ''
                    background_normal: ''
                    background_color: (0.6, 0.6, 0.6, 1)
                    color: 1, 1, 1, 1
                    on_release: root.copy_text()
                    disabled: not root.ids.text_input.text
            
            BoxLayout:
                size_hint_y: 0.5
                spacing: 10
                
                Button:
                    id: clear_btn
                    text: ''
                    background_normal: ''
                    background_color: (0.6, 0.6, 0.6, 1)
                    color: 1, 1, 1, 1
                    on_release: root.clear_all()
        
        # Status
        Label:
            id: status_label
            text: root.status_text
            size_hint_y: 0.05
            color: (0.7, 0.7, 0.7, 1) if app.dark_mode else (0.4, 0.4, 0.4, 1)
''')

class QRGeneratorScreen(Screen):
    """QR Code Generator Screen"""
    
    qr_path = StringProperty('')
    can_generate = False
    status_text = StringProperty('')
    current_lang = StringProperty('en')
    
    strings = {
        'en': {
            'qr_generator': 'QR Generator',
            'enter_text': 'Enter Text or URL:',
            'hint': 'Enter text to encode...',
            'generate': 'Generate QR Code',
            'preview': 'Preview:',
            'save': 'Save QR Code',
            'copy': 'Copy Text',
            'clear': 'Clear',
            'enter_text_first': 'Please enter text first',
            'no_qrcode': 'QR generator not available. Install qrcode',
            'generating': 'Generating QR code...',
            'generated': 'QR code generated successfully!',
            'error': 'Error generating QR code',
            'saved': 'QR code saved successfully!',
            'save_error': 'Error saving QR code',
            'copied': 'Text copied to clipboard!',
            'copy_error': 'Error copying text',
            'ready': 'Ready'
        },
        'am': {
            'qr_generator': 'QR ኮድ አመንጪ',
            'enter_text': 'ጽሁፍ ወይም አድራሻ ያስገቡ:',
            'hint': 'ለማስመስጠር ጽሁፍ ያስገቡ...',
            'generate': 'QR ኮድ አመንጭ',
            'preview': 'ቅድመ እይታ:',
            'save': 'QR ኮድ አስቀምጥ',
            'copy': 'ጽሁፍ ቅዳ',
            'clear': 'አጽዳ',
            'enter_text_first': 'እባክዎ መጀመሪያ ጽሁፍ ያስገቡ',
            'no_qrcode': 'QR አመንጪ አይገኝም። qrcode ይጫኑ',
            'generating': 'QR ኮድ በማመንጨት ላይ...',
            'generated': 'QR ኮድ በተሳካ ሁኔታ ተመንጭቷል!',
            'error': 'QR ኮድ በማመንጨት ላይ ስህተት',
            'saved': 'QR ኮድ በተሳካ ሁኔታ ተቀምጧል!',
            'save_error': 'QR ኮድ በማስቀመጥ ላይ ስህተት',
            'copied': 'ጽሁፍ ወደ ክሊፕቦርድ ተቀድቷል!',
            'copy_error': 'ጽሁፍ በመቅዳት ላይ ስህተት',
            'ready': 'ዝግጁ'
        }
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
    
    def on_pre_enter(self):
        self.app = App.get_running_app()
        self.current_lang = self.app.current_lang
        self.update_ui_language()
        self.update_fonts()
        
        # Bind text input to enable/disable generate button
        self.ids.text_input.bind(text=self.on_text_change)
    
    def on_enter(self):
        self.update_ui_language()
        self.update_fonts()
    
    def update_fonts(self):
        """Update font for all widgets based on current language"""
        if not self.app:
            return
        
        font_name = 'Abyssinica' if self.app.current_lang == 'am' and self.app.FONT_REGISTERED else 'Roboto'
        
        for widget in self.walk():
            if hasattr(widget, 'font_name'):
                widget.font_name = font_name
    
    def get_string(self, key, default=''):
        return self.strings[self.current_lang].get(key, default)
    
    def update_ui_language(self):
        self.ids.title_label.text = self.get_string('qr_generator')
        self.ids.input_label.text = self.get_string('enter_text')
        self.ids.text_input.hint_text = self.get_string('hint')
        self.ids.generate_btn.text = self.get_string('generate')
        self.ids.preview_label.text = self.get_string('preview')
        self.ids.save_btn.text = self.get_string('save')
        self.ids.copy_btn.text = self.get_string('copy')
        self.ids.clear_btn.text = self.get_string('clear')
    
    def on_text_change(self, instance, value):
        """Enable/disable generate button based on text input"""
        self.can_generate = bool(value.strip())
        self.ids.generate_btn.disabled = not self.can_generate
    
    def generate_qr(self):
        """Generate QR code from input text"""
        text = self.ids.text_input.text.strip()
        
        if not text:
            self.show_popup(self.get_string('enter_text_first'))
            return
        
        if not QRCODE_AVAILABLE:
            self.show_popup(self.get_string('no_qrcode'))
            return
        
        self.status_text = self.get_string('generating')
        self.ids.generate_btn.disabled = True
        
        # Run in thread
        Thread(target=self._generate_thread, args=(text,)).start()
    
    def _generate_thread(self, text):
        """Background QR generation thread"""
        try:
            # Create QR code instance
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            
            # Add data
            qr.add_data(text)
            qr.make(fit=True)
            
            # Create image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save temporary file
            temp_path = os.path.join(self.app.get_storage_path('images'), 'temp_qr.png')
            img.save(temp_path)
            
            Clock.schedule_once(lambda dt: self._generate_complete(temp_path), 0)
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self._generate_error(str(e)), 0)
    
    def _generate_complete(self, qr_path):
        """Handle generation completion"""
        self.qr_path = qr_path
        self.ids.qr_image.source = qr_path
        self.status_text = self.get_string('generated')
        self.ids.generate_btn.disabled = False
        self.show_popup(self.get_string('generated'))
    
    def _generate_error(self, error):
        """Handle generation error"""
        self.status_text = self.get_string('error')
        self.ids.generate_btn.disabled = False
        self.show_popup(self.get_string('error'))
    
    def save_qr(self):
        """Save QR code with user-friendly message"""
        if not self.qr_path:
            return
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"qrcode_{timestamp}.png"
            save_path = os.path.join(self.app.get_storage_path('images'), filename)
            
            import shutil
            shutil.copy2(self.qr_path, save_path)
            
            friendly_message = f"✓ Saved in: eyoTools > Images\nFile: {filename}"
            self.show_popup(friendly_message)
            
        except Exception as e:
            self.show_popup(self.get_string('save_error'))
    
    def copy_text(self):
        """Copy input text to clipboard"""
        from kivy.core.clipboard import Clipboard
        
        text = self.ids.text_input.text
        if text:
            try:
                Clipboard.copy(text)
                self.show_popup(self.get_string('copied'))
            except:
                self.show_popup(self.get_string('copy_error'))
    
    def clear_all(self):
        """Clear all fields"""
        self.ids.text_input.text = ''
        self.qr_path = ''
        self.ids.qr_image.source = ''
        self.status_text = self.get_string('ready')
        self.can_generate = False
    
    def show_popup(self, message):
        """Show popup message"""
        from kivy.uix.popup import Popup
        from kivy.uix.label import Label
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        label = Label(text=message)
        if self.app.current_lang == 'am' and self.app.FONT_REGISTERED:
            label.font_name = 'Abyssinica'
        content.add_widget(label)
        
        btn = Button(text='OK', size_hint_y=0.3)
        if self.app.current_lang == 'am' and self.app.FONT_REGISTERED:
            btn.font_name = 'Abyssinica'
        content.add_widget(btn)
        
        popup = Popup(title='Message', content=content, size_hint=(0.8, 0.4))
        btn.bind(on_release=popup.dismiss)
        popup.open()
    
    def go_back(self):
        """Return to home screen"""
        self.manager.current = 'home'