"""
PDF Tools Module
PDF to Text Extractor and PDF to Audio Converter (Offline Android TTS)
Bilingual: English and Amharic
"""

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.app import App
from kivy.utils import platform
from threading import Thread
import os
from datetime import datetime

# PDF to Text imports
try:
    import pypdf
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

# Android TTS via Pyjnius
if platform == 'android':
    try:
        from jnius import autoclass, cast
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Context = autoclass('android.content.Context')
        TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
        Locale = autoclass('java.util.Locale')
        JNI_AVAILABLE = True
    except:
        JNI_AVAILABLE = False
else:
    JNI_AVAILABLE = False

Builder.load_string('''
<PDFExtractorScreen>:
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
        
        # PDF Selection
        BoxLayout:
            size_hint_y: 0.15
            orientation: 'vertical'
            spacing: 5
            
            Label:
                id: select_label
                text: ''
                font_size: '16sp'
                color: (1, 1, 1, 1) if app.dark_mode else (0.2, 0.2, 0.2, 1)
                size_hint_y: 0.3
                text_size: self.size
                halign: 'left'
                valign: 'middle'
            
            Button:
                id: select_btn
                text: ''
                size_hint_y: 0.7
                background_normal: ''
                background_color: (0.2, 0.6, 0.8, 1)
                color: 1, 1, 1, 1
                on_release: root.choose_pdf()
        
        # PDF Info
        BoxLayout:
            size_hint_y: 0.1
            orientation: 'vertical'
            
            Label:
                id: pdf_info
                text: root.pdf_info
                text_size: self.size
                halign: 'left'
                valign: 'middle'
                color: (1, 1, 1, 1) if app.dark_mode else (0.2, 0.2, 0.2, 1)
        
        # Extract Button
        Button:
            id: extract_btn
            text: ''
            size_hint_y: 0.1
            background_normal: ''
            background_color: (0.2, 0.8, 0.2, 1)
            color: 1, 1, 1, 1
            on_release: root.extract_text()
            disabled: not root.pdf_path or root.is_processing
        
        # Progress Section
        BoxLayout:
            size_hint_y: 0.15
            orientation: 'vertical'
            spacing: 5
            
            Label:
                id: progress_label
                text: root.progress_text
                size_hint_y: 0.3
                color: (1, 1, 1, 1) if app.dark_mode else (0.2, 0.2, 0.2, 1)
            
            ProgressBar:
                id: progress_bar
                value: root.progress_value
                max: 100
                size_hint_y: 0.4
            
            Label:
                id: status_label
                text: root.status_text
                size_hint_y: 0.3
                color: (0.7, 0.7, 0.7, 1) if app.dark_mode else (0.4, 0.4, 0.4, 1)
        
        # Text Preview
        BoxLayout:
            size_hint_y: 0.3
            orientation: 'vertical'
            spacing: 5
            
            Label:
                id: preview_label
                text: ''
                font_size: '16sp'
                color: (1, 1, 1, 1) if app.dark_mode else (0.2, 0.2, 0.2, 1)
                size_hint_y: 0.1
            
            TextInput:
                id: text_preview
                text: root.extracted_text
                readonly: True
                background_color: (0.2, 0.2, 0.2, 1) if app.dark_mode else (1, 1, 1, 1)
                foreground_color: (1, 1, 1, 1) if app.dark_mode else (0, 0, 0, 1)
                size_hint_y: 0.9
        
        # Action Buttons
        BoxLayout:
            size_hint_y: 0.1
            spacing: 10
            
            Button:
                id: save_btn
                text: ''
                background_normal: ''
                background_color: (0.4, 0.4, 0.8, 1)
                color: 1, 1, 1, 1
                on_release: root.save_text()
                disabled: not root.extracted_text
            
            Button:
                id: copy_btn
                text: ''
                background_normal: ''
                background_color: (0.6, 0.6, 0.6, 1)
                color: 1, 1, 1, 1
                on_release: root.copy_text()
                disabled: not root.extracted_text
        
        # Clear Button
        Button:
            id: clear_btn
            text: ''
            size_hint_y: 0.05
            background_normal: ''
            background_color: (0.6, 0.6, 0.6, 1)
            color: 1, 1, 1, 1
            on_release: root.clear_all()

<PDFToAudioScreen>:
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
        
        # PDF Selection
        BoxLayout:
            size_hint_y: 0.12
            orientation: 'vertical'
            spacing: 5
            
            Label:
                id: select_label
                text: ''
                font_size: '16sp'
                color: (1, 1, 1, 1) if app.dark_mode else (0.2, 0.2, 0.2, 1)
                size_hint_y: 0.3
            
            Button:
                id: select_btn
                text: ''
                size_hint_y: 0.7
                background_normal: ''
                background_color: (0.2, 0.6, 0.8, 1)
                color: 1, 1, 1, 1
                on_release: root.choose_pdf()
        
        # Language Selection
        BoxLayout:
            size_hint_y: 0.12
            orientation: 'vertical'
            spacing: 5
            
            Label:
                id: lang_label
                text: ''
                font_size: '16sp'
                color: (1, 1, 1, 1) if app.dark_mode else (0.2, 0.2, 0.2, 1)
                size_hint_y: 0.3
            
            Spinner:
                id: lang_spinner
                size_hint_y: 0.7
                text: 'English'
                values: ['English', 'አማርኛ']
                on_text: root.on_language_select(self.text)
                background_color: (0.2, 0.2, 0.2, 1) if app.dark_mode else (1, 1, 1, 1)
                color: (1, 1, 1, 1) if app.dark_mode else (0, 0, 0, 1)
        
        # PDF Info
        BoxLayout:
            size_hint_y: 0.1
            orientation: 'vertical'
            
            Label:
                id: pdf_info
                text: root.pdf_info
                text_size: self.size
                halign: 'left'
                valign: 'middle'
                color: (1, 1, 1, 1) if app.dark_mode else (0.2, 0.2, 0.2, 1)
        
        # Extract Text Button
        Button:
            id: extract_btn
            text: ''
            size_hint_y: 0.1
            background_normal: ''
            background_color: (0.2, 0.6, 0.8, 1)
            color: 1, 1, 1, 1
            on_release: root.extract_text_for_tts()
            disabled: not root.pdf_path or root.is_processing
        
        # Progress Section
        BoxLayout:
            size_hint_y: 0.15
            orientation: 'vertical'
            spacing: 5
            
            Label:
                id: progress_label
                text: root.progress_text
                size_hint_y: 0.3
                color: (1, 1, 1, 1) if app.dark_mode else (0.2, 0.2, 0.2, 1)
            
            ProgressBar:
                id: progress_bar
                value: root.progress_value
                max: 100
                size_hint_y: 0.4
            
            Label:
                id: status_label
                text: root.status_text
                size_hint_y: 0.3
                color: (0.7, 0.7, 0.7, 1) if app.dark_mode else (0.4, 0.4, 0.4, 1)
        
        # Text Preview
        BoxLayout:
            size_hint_y: 0.2
            orientation: 'vertical'
            spacing: 5
            
            Label:
                id: preview_label
                text: ''
                font_size: '16sp'
                color: (1, 1, 1, 1) if app.dark_mode else (0.2, 0.2, 0.2, 1)
                size_hint_y: 0.2
            
            TextInput:
                id: text_preview
                text: root.extracted_text_preview
                readonly: True
                background_color: (0.2, 0.2, 0.2, 1) if app.dark_mode else (1, 1, 1, 1)
                foreground_color: (1, 1, 1, 1) if app.dark_mode else (0, 0, 0, 1)
                size_hint_y: 0.8
        
        # TTS Controls
        BoxLayout:
            size_hint_y: 0.15
            spacing: 10
            
            Button:
                id: play_btn
                text: ''
                background_normal: ''
                background_color: (0.2, 0.8, 0.2, 1)
                color: 1, 1, 1, 1
                on_release: root.speak_text()
                disabled: not root.extracted_text or root.is_speaking
            
            Button:
                id: stop_btn
                text: ''
                background_normal: ''
                background_color: (0.8, 0.2, 0.2, 1)
                color: 1, 1, 1, 1
                on_release: root.stop_speaking()
                disabled: not root.is_speaking
        
        # Clear Button
        Button:
            id: clear_btn
            text: ''
            size_hint_y: 0.05
            background_normal: ''
            background_color: (0.6, 0.6, 0.6, 1)
            color: 1, 1, 1, 1
            on_release: root.clear_all()
''')

class PDFExtractorScreen(Screen):
    """PDF to Text Extractor Screen"""
    
    pdf_path = StringProperty('')
    pdf_info = StringProperty('')
    extracted_text = StringProperty('')
    is_processing = False
    progress_value = NumericProperty(0)
    progress_text = StringProperty('')
    status_text = StringProperty('')
    current_lang = StringProperty('en')
    
    strings = {
        'en': {
            'pdf_to_text': 'PDF to Text',
            'select_pdf': 'Select PDF:',
            'choose_pdf': 'Choose PDF',
            'extract': 'Extract Text',
            'preview': 'Preview:',
            'save': 'Save as TXT',
            'copy': 'Copy',
            'clear': 'Clear',
            'select_pdf_first': 'Please select a PDF first',
            'no_pypdf2': 'PDF extractor not available. Install PyPDF2',
            'extracting': 'Extracting text...',
            'page': 'Page',
            'of': 'of',
            'complete': 'Text extraction complete!',
            'error': 'Error extracting text',
            'saved': 'Text saved successfully!',
            'save_error': 'Error saving text',
            'copied': 'Text copied to clipboard!',
            'copy_error': 'Error copying text',
            'pages': 'Pages',
            'ready': 'Ready'
        },
        'am': {
            'pdf_to_text': 'PDF ወደ ጽሁፍ',
            'select_pdf': 'PDF ይምረጡ:',
            'choose_pdf': 'PDF ምረጥ',
            'extract': 'ጽሁፍ አውጣ',
            'preview': 'ቅድመ እይታ:',
            'save': 'እንደ TXT አስቀምጥ',
            'copy': 'ቅዳ',
            'clear': 'አጽዳ',
            'select_pdf_first': 'እባክዎ መጀመሪያ PDF ይምረጡ',
            'no_pypdf2': 'PDF አውጪ አይገኝም። PyPDF2 ይጫኑ',
            'extracting': 'ጽሁፍ በማውጣት ላይ...',
            'page': 'ገጽ',
            'of': 'ከ',
            'complete': 'ጽሁፍ ማውጣት ተጠናቋል!',
            'error': 'ጽሁፍ በማውጣት ላይ ስህተት',
            'saved': 'ጽሁፍ በተሳካ ሁኔታ ተቀምጧል!',
            'save_error': 'ጽሁፍ በማስቀመጥ ላይ ስህተት',
            'copied': 'ጽሁፍ ወደ ክሊፕቦርድ ተቀድቷል!',
            'copy_error': 'ጽሁፍ በመቅዳት ላይ ስህተት',
            'pages': 'ገጾች',
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
        self.ids.title_label.text = self.get_string('pdf_to_text')
        self.ids.select_label.text = self.get_string('select_pdf')
        self.ids.select_btn.text = self.get_string('choose_pdf')
        self.ids.extract_btn.text = self.get_string('extract')
        self.ids.preview_label.text = self.get_string('preview')
        self.ids.save_btn.text = self.get_string('save')
        self.ids.copy_btn.text = self.get_string('copy')
        self.ids.clear_btn.text = self.get_string('clear')
    
    def choose_pdf(self):
        from kivy.uix.filechooser import FileChooserListView
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical')
        filechooser = FileChooserListView(path=os.path.expanduser('~'), filters=['*.pdf'])
        content.add_widget(filechooser)
        
        btn_layout = BoxLayout(size_hint_y=0.1, spacing=10)
        select_btn = Button(text=self.get_string('choose_pdf'))
        cancel_btn = Button(text='Cancel' if self.app.current_lang == 'en' else 'ሰርዝ')
        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(title=self.get_string('select_pdf'), content=content, size_hint=(0.9, 0.9))
        
        def on_select(instance):
            if filechooser.selection:
                self.pdf_path = filechooser.selection[0]
                self.get_pdf_info()
            popup.dismiss()
        
        select_btn.bind(on_release=on_select)
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()
    
    def get_pdf_info(self):
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                self.pdf_info = f"{self.get_string('pages')}: {num_pages}"
        except:
            self.pdf_info = self.get_string('error')
    
    def extract_text(self):
        if not self.pdf_path:
            self.show_popup(self.get_string('select_pdf_first'))
            return
        
        if not PYPDF2_AVAILABLE:
            self.show_popup(self.get_string('no_pypdf2'))
            return
        
        self.is_processing = True
        self.ids.extract_btn.disabled = True
        self.progress_value = 0
        self.progress_text = self.get_string('extracting')
        
        Thread(target=self._extract_thread).start()
    
    def _extract_thread(self):
        try:
            text = ""
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                for i, page in enumerate(pdf_reader.pages):
                    text += page.extract_text()
                    progress = ((i + 1) / total_pages) * 100
                    Clock.schedule_once(lambda dt, p=progress, i=i: self._update_progress(p, 
                        f"{self.get_string('page')} {i+1} {self.get_string('of')} {total_pages}"), 0)
            
            Clock.schedule_once(lambda dt: self._extract_complete(text), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: self._extract_error(str(e)), 0)
    
    def _update_progress(self, value, text):
        self.progress_value = value
        self.status_text = text
    
    def _extract_complete(self, text):
        self.extracted_text = text[:5000] + ("..." if len(text) > 5000 else "")
        self.ids.text_preview.text = self.extracted_text
        self.progress_value = 100
        self.progress_text = self.get_string('complete')
        self.status_text = self.get_string('complete')
        self.is_processing = False
        self.ids.extract_btn.disabled = False
    
    def _extract_error(self, error):
        self.progress_text = self.get_string('error')
        self.status_text = self.get_string('error')
        self.is_processing = False
        self.ids.extract_btn.disabled = False
        self.show_popup(self.get_string('error'))
    
    def save_text(self):
        """Save extracted text with user-friendly message"""
        if not self.extracted_text:
            return
        
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"extracted_{timestamp}.txt"
            save_path = os.path.join(self.app.get_storage_path('downloads'), filename)
            
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(self.extracted_text)
            
            friendly_message = f"✓ Saved in: eyoTools > Downloads\nFile: {filename}"
            self.show_popup(friendly_message)
        except:
            self.show_popup(self.get_string('save_error'))
    
    def copy_text(self):
        from kivy.core.clipboard import Clipboard
        try:
            Clipboard.copy(self.extracted_text)
            self.show_popup(self.get_string('copied'))
        except:
            self.show_popup(self.get_string('copy_error'))
    
    def clear_all(self):
        self.pdf_path = ''
        self.pdf_info = ''
        self.extracted_text = ''
        self.ids.text_preview.text = ''
        self.progress_value = 0
        self.progress_text = ''
        self.status_text = ''
    
    def show_popup(self, message):
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
        self.manager.current = 'home'

class PDFToAudioScreen(Screen):
    """PDF to Audio Converter Screen using Android Native TTS"""
    
    pdf_path = StringProperty('')
    pdf_info = StringProperty('')
    extracted_text = StringProperty('')
    extracted_text_preview = StringProperty('')
    is_processing = False
    is_speaking = BooleanProperty(False)
    progress_value = NumericProperty(0)
    progress_text = StringProperty('')
    status_text = StringProperty('')
    current_lang = StringProperty('en')
    selected_lang = 'en'
    
    strings = {
        'en': {
            'pdf_to_audio': 'PDF to Audio',
            'select_pdf': 'Select PDF:',
            'choose_pdf': 'Choose PDF',
            'select_lang': 'Select Language:',
            'extract': 'Extract Text',
            'play': 'Play',
            'stop': 'Stop',
            'clear': 'Clear',
            'select_pdf_first': 'Please select a PDF first',
            'no_pypdf2': 'PDF reader not available',
            'no_tts': 'Text to speech not available on this device',
            'extracting': 'Extracting text from PDF...',
            'page': 'Page',
            'of': 'of',
            'complete': 'Text extraction complete!',
            'error': 'Error during extraction',
            'speaking': 'Speaking...',
            'stopped': 'Stopped',
            'ready': 'Ready',
            'preview': 'Preview:'
        },
        'am': {
            'pdf_to_audio': 'PDF ወደ ድምጽ',
            'select_pdf': 'PDF ይምረጡ:',
            'choose_pdf': 'PDF ምረጥ',
            'select_lang': 'ቋንቋ ይምረጡ:',
            'extract': 'ጽሁፍ አውጣ',
            'play': 'አጫውት',
            'stop': 'አቁም',
            'clear': 'አጽዳ',
            'select_pdf_first': 'እባክዎ መጀመሪያ PDF ይምረጡ',
            'no_pypdf2': 'PDF አንባቢ አይገኝም',
            'no_tts': 'ጽሁፍ ወደ ድምጽ መቀየሪያ በዚህ መሳሪያ አይገኝም',
            'extracting': 'ጽሁፍ ከ PDF በማውጣት ላይ...',
            'page': 'ገጽ',
            'of': 'ከ',
            'complete': 'ጽሁፍ ማውጣት ተጠናቋል!',
            'error': 'በማውጣት ላይ ስህተት',
            'speaking': 'በማንበብ ላይ...',
            'stopped': 'ቆሟል',
            'ready': 'ዝግጁ',
            'preview': 'ቅድመ እይታ:'
        }
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.tts = None
        self._init_tts()
    
    def _init_tts(self):
        """Initialize Android TTS if on Android"""
        if platform == 'android' and JNI_AVAILABLE:
            try:
                self.tts = TextToSpeech(PythonActivity.mActivity, None)
            except Exception as e:
                print(f"TTS init error: {e}")
                self.tts = None
    
    def on_pre_enter(self):
        self.app = App.get_running_app()
        self.current_lang = self.app.current_lang
        self.update_ui_language()
        self.update_fonts()
    
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
        self.ids.title_label.text = self.get_string('pdf_to_audio')
        self.ids.select_label.text = self.get_string('select_pdf')
        self.ids.select_btn.text = self.get_string('choose_pdf')
        self.ids.lang_label.text = self.get_string('select_lang')
        self.ids.extract_btn.text = self.get_string('extract')
        self.ids.play_btn.text = self.get_string('play')
        self.ids.stop_btn.text = self.get_string('stop')
        self.ids.clear_btn.text = self.get_string('clear')
        self.ids.preview_label.text = self.get_string('preview')
    
    def on_language_select(self, text):
        if text == 'አማርኛ':
            self.selected_lang = 'am'
        else:
            self.selected_lang = 'en'
    
    def choose_pdf(self):
        from kivy.uix.filechooser import FileChooserListView
        from kivy.uix.popup import Popup
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        
        content = BoxLayout(orientation='vertical')
        filechooser = FileChooserListView(path=os.path.expanduser('~'), filters=['*.pdf'])
        content.add_widget(filechooser)
        
        btn_layout = BoxLayout(size_hint_y=0.1, spacing=10)
        select_btn = Button(text=self.get_string('choose_pdf'))
        cancel_btn = Button(text='Cancel' if self.app.current_lang == 'en' else 'ሰርዝ')
        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)
        
        popup = Popup(title=self.get_string('select_pdf'), content=content, size_hint=(0.9, 0.9))
        
        def on_select(instance):
            if filechooser.selection:
                self.pdf_path = filechooser.selection[0]
                self.get_pdf_info()
            popup.dismiss()
        
        select_btn.bind(on_release=on_select)
        cancel_btn.bind(on_release=popup.dismiss)
        popup.open()
    
    def get_pdf_info(self):
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                self.pdf_info = f"{self.get_string('pages')}: {num_pages}"
        except:
            self.pdf_info = self.get_string('error')
    
    def extract_text_for_tts(self):
        if not self.pdf_path:
            self.show_popup(self.get_string('select_pdf_first'))
            return
        
        if not PYPDF2_AVAILABLE:
            self.show_popup(self.get_string('no_pypdf2'))
            return
        
        self.is_processing = True
        self.ids.extract_btn.disabled = True
        self.progress_value = 0
        self.progress_text = self.get_string('extracting')
        
        Thread(target=self._extract_thread).start()
    
    def _extract_thread(self):
        try:
            text = ""
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                for i, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text += page_text + " "
                    progress = ((i + 1) / total_pages) * 100
                    Clock.schedule_once(lambda dt, p=progress, i=i: self._update_progress(p, 
                        f"{self.get_string('page')} {i+1} {self.get_string('of')} {total_pages}"), 0)
            
            Clock.schedule_once(lambda dt: self._extract_complete(text), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: self._extract_error(str(e)), 0)
    
    def _update_progress(self, value, text):
        self.progress_value = value
        self.status_text = text
    
    def _extract_complete(self, text):
        self.extracted_text = text
        self.extracted_text_preview = text[:500] + ("..." if len(text) > 500 else "")
        self.ids.text_preview.text = self.extracted_text_preview
        self.progress_value = 100
        self.progress_text = self.get_string('complete')
        self.status_text = self.get_string('complete')
        self.is_processing = False
        self.ids.extract_btn.disabled = False
    
    def _extract_error(self, error):
        self.progress_text = self.get_string('error')
        self.status_text = self.get_string('error')
        self.is_processing = False
        self.ids.extract_btn.disabled = False
        self.show_popup(self.get_string('error'))
    
    def speak_text(self):
        """Speak the extracted text using Android TTS"""
        if not self.extracted_text:
            return
        
        if platform != 'android' or not JNI_AVAILABLE or self.tts is None:
            self.show_popup(self.get_string('no_tts'))
            return
        
        try:
            # Set language
            if self.selected_lang == 'am':
                locale = Locale.forLanguageTag("am")
            else:
                locale = Locale.US
            
            self.tts.setLanguage(locale)
            
            # Speak the text
            self.tts.speak(self.extracted_text, TextToSpeech.QUEUE_FLUSH, None, None)
            self.is_speaking = True
            self.ids.play_btn.disabled = True
            self.ids.stop_btn.disabled = False
            self.status_text = self.get_string('speaking')
            
        except Exception as e:
            print(f"TTS speak error: {e}")
            self.show_popup(self.get_string('error'))
    
    def stop_speaking(self):
        """Stop TTS"""
        if platform == 'android' and JNI_AVAILABLE and self.tts is not None:
            try:
                self.tts.stop()
            except:
                pass
        
        self.is_speaking = False
        self.ids.play_btn.disabled = False
        self.ids.stop_btn.disabled = True
        self.status_text = self.get_string('stopped')
    
    def clear_all(self):
        """Clear all fields and stop TTS"""
        self.stop_speaking()
        self.pdf_path = ''
        self.pdf_info = ''
        self.extracted_text = ''
        self.extracted_text_preview = ''
        self.ids.text_preview.text = ''
        self.progress_value = 0
        self.progress_text = ''
        self.status_text = ''
    
    def show_popup(self, message):
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
        self.stop_speaking()
        self.manager.current = 'home'