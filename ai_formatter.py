"""
AI Text Formatter menggunakan OpenRouter (Google Gemini 2.0 Flash)
Memformat dokumen text mentah menjadi Markdown yang terstruktur
"""

from openai import OpenAI
import os
import hashlib
import json
from pathlib import Path
from typing import Optional

class AIFormatter:
    def __init__(self, api_key: str):
        """
        Initialize AI Formatter dengan OpenRouter API (Google Gemini 2.0 Flash)
        
        Args:
            api_key: OpenRouter API key
        """
        # Initialize OpenAI client dengan OpenRouter endpoint
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
        
        # Model: Anthropic Claude 3.5 Haiku (Cepat & Reliable)
        self.model = "anthropic/claude-3.5-haiku"
        
        # Setup cache directory
        self.cache_dir = Path("cache/formatted_docs")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # System prompt untuk formatting
        self.system_prompt = """Anda adalah AI Text Formatter yang ahli dalam mengubah dokumen text mentah menjadi Markdown yang terstruktur dan mudah dibaca.

TUGAS ANDA:
1. Analisis struktur dokumen dan identifikasi:
   - Judul utama dan sub-judul
   - Paragraf dan bagian-bagian penting
   - List/enumerasi jika ada
   - Istilah penting atau definisi
   
2. Format dokumen menjadi Markdown dengan aturan:
   - Gunakan # untuk judul utama
   - Gunakan ## untuk sub-judul
   - Gunakan ### untuk sub-sub-judul
   - Gunakan **bold** untuk istilah/konsep penting
   - Gunakan *italic* untuk penekanan
   - Gunakan bullet points (-) untuk list
   - Gunakan numbered list (1., 2., 3.) untuk langkah-langkah
   - Pisahkan paragraf dengan line break yang proper
   - Tambahkan horizontal rule (---) untuk pemisah section besar

PENTING:
- JANGAN mengubah isi konten, hanya format presentasinya
- JANGAN menambah atau mengurangi informasi
- JANGAN menerjemahkan bahasa
- Pertahankan semua fakta, angka, dan data original
- Fokus pada readability dan struktur visual

Output HARUS valid Markdown tanpa penjelasan tambahan."""

    def _get_cache_key(self, text: str) -> str:
        """
        Generate cache key dari hash MD5 text
        
        Args:
            text: Text original
            
        Returns:
            MD5 hash sebagai cache key
        """
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """
        Get path file cache
        
        Args:
            cache_key: MD5 hash key
            
        Returns:
            Path object untuk cache file
        """
        return self.cache_dir / f"{cache_key}.json"
    
    def _load_from_cache(self, cache_key: str) -> Optional[str]:
        """
        Load formatted text dari cache jika ada
        
        Args:
            cache_key: MD5 hash key
            
        Returns:
            Formatted text atau None jika tidak ada di cache
        """
        cache_path = self._get_cache_path(cache_key)
        
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('formatted_text')
            except Exception as e:
                print(f"Error loading cache: {e}")
                return None
        
        return None
    
    def _save_to_cache(self, cache_key: str, original_text: str, formatted_text: str):
        """
        Save formatted text ke cache
        
        Args:
            cache_key: MD5 hash key
            original_text: Text original (untuk reference)
            formatted_text: Text yang sudah diformat AI
        """
        cache_path = self._get_cache_path(cache_key)
        
        try:
            data = {
                'cache_key': cache_key,
                'original_length': len(original_text),
                'formatted_text': formatted_text,
                'formatted_length': len(formatted_text)
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"Error saving cache: {e}")
    
    def format_text(self, text: str, use_cache: bool = True) -> dict:
        """
        Format text menggunakan OpenRouter GLM 4.7
        
        Args:
            text: Text original yang akan diformat
            use_cache: Gunakan cache jika True (default)
            
        Returns:
            Dict dengan keys:
                - formatted_text: Text hasil formatting
                - from_cache: Boolean apakah dari cache
                - original_length: Panjang text original
                - formatted_length: Panjang text hasil
        """
        # Generate cache key
        cache_key = self._get_cache_key(text)
        
        # Check cache dulu jika diaktifkan
        if use_cache:
            cached_result = self._load_from_cache(cache_key)
            if cached_result:
                return {
                    'formatted_text': cached_result,
                    'from_cache': True,
                    'original_length': len(text),
                    'formatted_length': len(cached_result),
                    'cache_key': cache_key
                }
        
        # Jika tidak ada di cache, panggil AI
        try:
            # Limit text length untuk menghindari token limit
            # GLM 4.7 support ~128k tokens, tapi kita batasi untuk safety
            max_chars = 50000  # ~12k tokens
            if len(text) > max_chars:
                text_to_format = text[:max_chars] + "\n\n[... Dokumen dipotong karena terlalu panjang ...]"
            else:
                text_to_format = text
            
            # Call OpenRouter API dengan OpenAI-compatible format
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": f"=== DOKUMEN YANG AKAN DIFORMAT ===\n\n{text_to_format}"
                    }
                ],
                temperature=0.3,  # Lower temperature untuk konsistensi formatting
                max_tokens=4000   # Limit output tokens
            )
            
            # Extract formatted text dari response
            formatted_text = response.choices[0].message.content
            
            # Save ke cache
            if use_cache:
                self._save_to_cache(cache_key, text, formatted_text)
            
            return {
                'formatted_text': formatted_text,
                'from_cache': False,
                'original_length': len(text),
                'formatted_length': len(formatted_text),
                'cache_key': cache_key
            }
            
        except Exception as e:
            # Jika error, fallback ke text original
            return {
                'formatted_text': text,  # Fallback ke original
                'from_cache': False,
                'original_length': len(text),
                'formatted_length': len(text),
                'error': str(e)
            }
    
    def clear_cache(self):
        """
        Hapus semua cache
        """
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
            return True
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False
    
    def get_cache_stats(self) -> dict:
        """
        Get statistik cache
        
        Returns:
            Dict dengan total files dan total size
        """
        cache_files = list(self.cache_dir.glob("*.json"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            'total_cached': len(cache_files),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        }
