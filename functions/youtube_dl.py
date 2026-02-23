"""
YouTube Downloader Tool
Download YouTube videos with quality selection
Bilingual: English and Amharic
"""

from kivy.uix.screenmanager import Screen
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty, NumericProperty, BooleanProperty
from kivy.app import App
from kivy.utils import platform
import os
import re
from threading import Thread

# Try to import pytubefix
try:
    from pytubefix import YouTube
    from pytubefix.cli import on_progress
    PYTUBE_AVAILABLE = True
except ImportError:
    PYTUBE_AVAILABLE = False

Builder.load_string('''
<YouTubeDownloaderScreen>:
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
        
        # URL Input Section
        BoxLayout:
            size_hint_y: 0.15
            orientation: 'vertical'
            spacing: 5
            
            Label:
                id: url_label
                text: ''
                font_size: '16sp'
                color: (1, 1, 1, 1) if app.dark_mode else (0.2, 0.2, 0.2, 1)
                size_hint_y: 0.3
                text_size: self.size
                halign: 'left'
                valign: 'middle'
            
            TextInput:
                id: url_input
                size_hint_y: 0.7
                multiline: False
                text: ''
                hint_text: 'https://youtube.com/watch?v=...'
                background_color: (0.2, 0.2, 0.2, 1) if app.dark_mode else (1, 1, 1, 1)
                foreground_color: (1, 1, 1, 1) if app.dark_mode else (0, 0, 0, 1)
                hint_text_color: (0.6, 0.6, 0.6, 1) if app.dark_mode else (0.5, 0.5, 0.5, 1)
            
            Button:
                id: fetch_btn
                text: ''
                size_hint_y: 0.4
                background_normal: ''
                background_color: (0.2, 0.6, 0.8, 1)
                color: 1, 1, 1, 1
                on_release: root.fetch_video_info()
                disabled: root.is_processing
        
        # Video Info Section
        ScrollView:
            size_hint_y: 0.25
            do_scroll_x: False
            do_scroll_y: True
            
            BoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: 5
                
                Label:
                    id: video_title
                    text: ''
                    size_hint_y: None
                    height: 40
                    text_size: self.size
                    halign: 'left'
                    valign: 'middle'
                    color: (1, 1, 1, 1) if app.dark_mode else (0.2, 0.2, 0.2, 1)
                
                Label:
                    id: video_author
                    text: ''
                    size_hint_y: None
                    height: 40
                    text_size: self.size
                    halign: 'left'
                    valign: 'middle'
                    color: (1, 1, 1, 1) if app.dark_mode else (0.2, 0.2, 0.2, 1)
                
                Label:
                    id: video_duration
                    text: ''
                    size_hint_y: None
                    height: 40
                    text_size: self.size
                    halign: 'left'
                    valign: 'middle'
                    color: (1, 1, 1, 1) if app.dark_mode else (0.2, 0.2, 0.2, 1)
                
                Label:
                    id: video_views
                    text: ''
                    size_hint_y: None
                    height: 40
                    text_size: self.size
                    halign: 'left'
                    valign: 'middle'
                    color: (1, 1, 1, 1) if app.dark_mode else (0.2, 0.2, 0.2, 1)
        
        # Download Type Selection
        BoxLayout:
            size_hint_y: 0.1
            spacing: 10
            orientation: 'horizontal'
            
            ToggleButton:
                id: video_btn
                text: ''
                state: 'down' if root.download_type == 'video' else 'normal'
                group: 'download_type'
                background_color: (0.2, 0.6, 0.8, 1)
                color: 1, 1, 1, 1
                on_release: root.set_download_type('video')
            
            ToggleButton:
                id: audio_btn
                text: ''
                state: 'down' if root.download_type == 'audio' else 'normal'
                group: 'download_type'
                background_color: (0.2, 0.8, 0.2, 1)
                color: 1, 1, 1, 1
                on_release: root.set_download_type('audio')
        
        # Quality Selection
        BoxLayout:
            size_hint_y: 0.15
            orientation: 'vertical'
            spacing: 5
            
            Label:
                id: quality_label
                text: ''
                font_size: '16sp'
                color: (1, 1, 1, 1) if app.dark_mode else (0.2, 0.2, 0.2, 1)
                size_hint_y: 0.3
                text_size: self.size
                halign: 'left'
                valign: 'middle'
            
            Spinner:
                id: quality_spinner
                size_hint_y: 0.7
                text: ''
                values: root.quality_options
                background_color: (0.2, 0.2, 0.2, 1) if app.dark_mode else (1, 1, 1, 1)
                color: (1, 1, 1, 1) if app.dark_mode else (0, 0, 0, 1)
        
        # Download Button
        Button:
            id: download_btn
            text: ''
            size_hint_y: 0.1
            background_normal: ''
            background_color: (0.2, 0.8, 0.2, 1)
            color: 1, 1, 1, 1
            on_release: root.start_download()
            disabled: not root.can_download
        
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

class YouTubeDownloaderScreen(Screen):
    """YouTube Downloader Screen"""
    
    # Properties
    video_title = StringProperty('')
    video_author = StringProperty('')
    video_duration = StringProperty('')
    video_views = StringProperty('')
    quality_options = []
    can_download = BooleanProperty(False)
    is_processing = BooleanProperty(False)
    progress_value = NumericProperty(0)
    progress_text = StringProperty('')
    status_text = StringProperty('')
    current_lang = StringProperty('en')
    download_type = StringProperty('video')
    
    # Language strings dictionary
    strings = {
        'en': {
            'youtube_downloader': 'YouTube Downloader',
            'enter_url': 'Enter YouTube URL:',
            'fetch_info': 'Fetch Video Info',
            'title': 'Title:',
            'author': 'Author:',
            'duration': 'Duration:',
            'views': 'Views:',
            'select_quality': 'Select Quality:',
            'select': 'Select',
            'download': 'Download',
            'clear': 'Clear All',
            'fetching': 'Fetching video information...',
            'fetch_error': 'Error fetching video. Check URL and internet.',
            'select_quality_first': 'Please select quality first',
            'downloading': 'Downloading...',
            'download_complete': 'Download complete!',
            'download_error': 'Download failed. Please try again.',
            'no_pytube': 'YouTube downloader not available. Install pytubefix',
            'enter_url_first': 'Please enter a URL first',
            'quality': 'Quality',
            'filesize': 'File size',
            'mb': 'MB',
            'ready': 'Ready',
            'processing': 'Processing...',
            'video': 'Video',
            'audio': 'Audio',
            'select_video': 'Select Video Quality',
            'select_audio': 'Select Audio Quality',
            'audio_only': 'Audio Only',
            'kbps': 'kbps'
        },
        'am': {
            'youtube_downloader': 'ዩቲዩብ አውራጅ',
            'enter_url': 'የዩቲዩብ አድራሻ ያስገቡ:',
            'fetch_info': 'የቪዲዮ መረጃ አምጣ',
            'title': 'ርዕስ:',
            'author': 'አቅራቢ:',
            'duration': 'ቆይታ:',
            'views': 'ተመልካቾች:',
            'select_quality': 'ጥራት ይምረጡ:',
            'select': 'ምረጥ',
            'download': 'አውርድ',
            'clear': 'ሁሉንም አጽዳ',
            'fetching': 'የቪዲዮ መረጃ በማምጣት ላይ...',
            'fetch_error': 'ቪዲዮ ማምጣት አልተሳካም። አድራሻ ያረጋግጡ።',
            'select_quality_first': 'እባክዎ መጀመሪያ ጥራት ይምረጡ',
            'downloading': 'በማውረድ ላይ...',
            'download_complete': 'ማውረድ ተጠናቋል!',
            'download_error': 'ማውረድ አልተሳካም። እንደገና ይሞክሩ።',
            'no_pytube': 'ዩቲዩብ አውራጅ አይገኝም። pytubefix ይጫኑ',
            'enter_url_first': 'እባክዎ መጀመሪያ አድራሻ ያስገቡ',
            'quality': 'ጥራት',
            'filesize': 'የፋይል መጠን',
            'mb': 'ሜባ',
            'ready': 'ዝግጁ',
            'processing': 'በሂደት ላይ...',
            'video': 'ቪዲዮ',
            'audio': 'ኦዲዮ',
            'select_video': 'የቪዲዮ ጥራት ይምረጡ',
            'select_audio': 'የኦዲዮ ጥራት ይምረጡ',
            'audio_only': 'ኦዲዮ ብቻ',
            'kbps': 'kbps'
        }
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.yt = None
        self.selected_stream = None
        self.app = None
        self.video_streams = []
        self.audio_streams = []
    
    def on_pre_enter(self):
        """Called before screen enters"""
        self.app = App.get_running_app()
        self.current_lang = self.app.current_lang
        self.update_ui_language()
        self.update_fonts()
    
    def on_enter(self):
        """Called when screen enters"""
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
        """Get string in current language"""
        return self.strings[self.current_lang].get(key, default)
    
    def update_ui_language(self):
        """Update all UI text elements based on language"""
        self.ids.title_label.text = self.get_string('youtube_downloader')
        self.ids.url_label.text = self.get_string('enter_url')
        self.ids.fetch_btn.text = self.get_string('fetch_info')
        self.ids.quality_label.text = self.get_string('select_quality')
        self.ids.download_btn.text = self.get_string('download')
        self.ids.clear_btn.text = self.get_string('clear')
        self.ids.video_btn.text = self.get_string('video')
        self.ids.audio_btn.text = self.get_string('audio')
        self.ids.quality_spinner.text = self.get_string('select')
        
        # Update video info labels if they have content
        if self.video_title:
            self.ids.video_title.text = f"{self.get_string('title')} {self.video_title}"
        if self.video_author:
            self.ids.video_author.text = f"{self.get_string('author')} {self.video_author}"
        if self.video_duration:
            self.ids.video_duration.text = f"{self.get_string('duration')} {self.video_duration}"
        if self.video_views:
            self.ids.video_views.text = f"{self.get_string('views')} {self.video_views}"
    
    def set_download_type(self, dtype):
        """Set download type (video/audio)"""
        self.download_type = dtype
        self.update_quality_options()
    
    def fetch_video_info(self):
        """Fetch video information from URL"""
        url = self.ids.url_input.text.strip()
        
        if not url:
            self.show_popup(self.get_string('enter_url_first'))
            return
        
        if not PYTUBE_AVAILABLE:
            self.show_popup(self.get_string('no_pytube'))
            return
        
        self.is_processing = True
        self.ids.fetch_btn.disabled = True
        self.can_download = False
        self.status_text = self.get_string('fetching')
        self.progress_text = self.get_string('processing')
        
        # Run in thread to avoid blocking UI
        Thread(target=self._fetch_info_thread, args=(url,)).start()
    
    def _fetch_info_thread(self, url):
        """Background thread for fetching video info"""
        try:
            self.yt = YouTube(url, on_progress_callback=self.on_download_progress)
            
            # Update UI with video info
            Clock.schedule_once(lambda dt: self._update_video_info(), 0)
            
            # Get available video streams (progressive)
            self.video_streams = []
            for stream in self.yt.streams.filter(progressive=True, file_extension='mp4'):
                if stream.resolution:
                    size = stream.filesize / (1024 * 1024)  # Convert to MB
                    self.video_streams.append({
                        'stream': stream,
                        'display': f"{stream.resolution} - {size:.1f} MB"
                    })
            
            # Get available audio streams
            self.audio_streams = []
            for stream in self.yt.streams.filter(only_audio=True):
                if stream.abr:
                    size = stream.filesize / (1024 * 1024) if stream.filesize else 0
                    self.audio_streams.append({
                        'stream': stream,
                        'display': f"{stream.abr} - {size:.1f} MB"
                    })
            
            Clock.schedule_once(lambda dt: self.update_quality_options(), 0)
            
        except Exception as e:
            Clock.schedule_once(lambda dt: self._fetch_error(str(e)), 0)
    
    def _update_video_info(self):
        """Update video info display"""
        self.video_title = self.yt.title
        self.video_author = self.yt.author
        minutes = self.yt.length // 60
        seconds = self.yt.length % 60
        self.video_duration = f"{minutes}:{seconds:02d}"
        self.video_views = f"{self.yt.views:,}"
        
        # Update labels with language prefixes
        self.ids.video_title.text = f"{self.get_string('title')} {self.video_title}"
        self.ids.video_author.text = f"{self.get_string('author')} {self.video_author}"
        self.ids.video_duration.text = f"{self.get_string('duration')} {self.video_duration}"
        self.ids.video_views.text = f"{self.get_string('views')} {self.video_views}"
        
        self.status_text = self.get_string('ready')
        self.is_processing = False
        self.ids.fetch_btn.disabled = False
    
    def update_quality_options(self):
        """Update quality spinner based on download type"""
        if self.download_type == 'video':
            options = [s['display'] for s in self.video_streams]
            self.quality_options = options
        else:
            options = [s['display'] for s in self.audio_streams]
            self.quality_options = options
        
        self.ids.quality_spinner.values = self.quality_options
        self.ids.quality_spinner.text = self.get_string('select')
        self.can_download = len(self.quality_options) > 0
    
    def _fetch_error(self, error):
        """Handle fetch error"""
        print(f"Fetch error: {error}")  # For debugging
        self.status_text = self.get_string('fetch_error')
        self.is_processing = False
        self.ids.fetch_btn.disabled = False
        self.show_popup(self.get_string('fetch_error'))
    
    def on_download_progress(self, stream, chunk, bytes_remaining):
        """Update download progress"""
        total_size = stream.filesize
        if total_size:
            bytes_downloaded = total_size - bytes_remaining
            percentage = (bytes_downloaded / total_size) * 100
            Clock.schedule_once(lambda dt: self._update_progress(percentage))
    
    def _update_progress(self, percentage):
        """Update progress bar"""
        self.progress_value = percentage
        self.progress_text = f"{self.get_string('downloading')} {percentage:.1f}%"
    
    def start_download(self):
        """Start video/audio download"""
        if not self.yt:
            self.show_popup(self.get_string('fetch_info'))
            return
        
        quality_text = self.ids.quality_spinner.text
        if quality_text == self.get_string('select') or not quality_text:
            self.show_popup(self.get_string('select_quality_first'))
            return
        
        # Get selected stream
        selected_index = self.ids.quality_spinner.values.index(quality_text)
        
        if self.download_type == 'video':
            self.selected_stream = self.video_streams[selected_index]['stream']
        else:
            self.selected_stream = self.audio_streams[selected_index]['stream']
        
        self.can_download = False
        self.ids.download_btn.disabled = True
        self.progress_value = 0
        self.progress_text = self.get_string('downloading')
        self.status_text = self.get_string('downloading')
        
        # Start download in thread
        Thread(target=self._download_thread).start()
    
    def _download_thread(self):
        """Background download thread"""
        try:
            # Sanitize filename
            safe_title = re.sub(r'[^\w\s-]', '', self.yt.title)
            safe_title = re.sub(r'[-\s]+', '_', safe_title)
            
            # Set file extension based on download type
            if self.download_type == 'video':
                filename = f"{safe_title}.mp4"
            else:
                filename = f"{safe_title}.mp3"
            
            # Get download path
            download_path = self.app.get_storage_path('downloads')
            full_path = os.path.join(download_path, filename)
            
            # Download file
            self.selected_stream.download(output_path=download_path, filename=filename)
            
            Clock.schedule_once(lambda dt: self._download_complete(filename), 0)
            
        except Exception as e:
            print(f"Download error: {e}")  # For debugging
            Clock.schedule_once(lambda dt: self._download_error(str(e)), 0)
    
    def _download_complete(self, filename):
        """Handle download completion with user-friendly message"""
        self.progress_value = 100
        self.progress_text = self.get_string('download_complete')
        self.status_text = self.get_string('download_complete')
        self.can_download = True
        self.ids.download_btn.disabled = False
        
        friendly_message = f"✓ Saved in: eyoTools > Downloads\nFile: {filename}"
        self.show_popup(friendly_message)
    
    def _download_error(self, error):
        """Handle download error"""
        self.progress_text = self.get_string('download_error')
        self.status_text = self.get_string('download_error')
        self.progress_value = 0
        self.can_download = True
        self.ids.download_btn.disabled = False
        self.show_popup(self.get_string('download_error'))
    
    def clear_all(self):
        """Clear all fields"""
        self.ids.url_input.text = ''
        self.video_title = ''
        self.video_author = ''
        self.video_duration = ''
        self.video_views = ''
        self.quality_options = []
        self.video_streams = []
        self.audio_streams = []
        self.ids.quality_spinner.text = self.get_string('select')
        self.ids.quality_spinner.values = []
        self.progress_value = 0
        self.progress_text = ''
        self.status_text = ''
        self.can_download = False
        self.yt = None
        self.selected_stream = None
        self.download_type = 'video'
        self.ids.video_btn.state = 'down'
        self.ids.audio_btn.state = 'normal'
        
        # Clear info labels
        self.ids.video_title.text = ''
        self.ids.video_author.text = ''
        self.ids.video_duration.text = ''
        self.ids.video_views.text = ''
    
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