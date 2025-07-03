import logging
from typing import List, Optional, Dict
import json
import re
from services.gemini_utils import gemini_service
from fuzzywuzzy import fuzz
from datetime import datetime, timezone
from models.schemas import VideoMetadata

logger = logging.getLogger(__name__)

class ViralAnalysisService:
    """
    Service untuk menganalisis potensi viral konten dengan metrik konkret berbasis data.
    """

    def __init__(self):
        pass

    def _calculate_view_velocity_score(self, metadata: VideoMetadata) -> int:
        """
        Menghitung skor berdasarkan kecepatan perolehan views.
        Skor ini memberikan bobot signifikan pada performa awal video.
        """
        if not metadata.view_count or not metadata.published_at or not metadata.subscriber_count:
            return 5 # Skor default jika data tidak lengkap

        now = datetime.now(timezone.utc)
        video_age_hours = (now - metadata.published_at).total_seconds() / 3600
        views = metadata.view_count
        subscribers = metadata.subscriber_count

        if video_age_hours <= 0:
            return 5

        # 1. Channel Kecil ke Menengah (< 500K subs)
        if subscribers < 500000:
            if video_age_hours <= 72 and views > 100000:
                return 35 # Sangat viral untuk channel kecil
            if video_age_hours <= 72 and views > 25000:
                return 30 # Performa luar biasa
            if video_age_hours <= 168 and views > 50000:
                 return 25 # Performa solid dalam seminggu

        # 2. Channel Menengah ke Besar (>= 500K subs)
        else:
            if video_age_hours <= 168 and views > 1000000:
                return 35 # Viral standar
            if video_age_hours <= 168 and views > 500000:
                return 30 # Performa luar biasa
        
        # Penilaian umum berdasarkan rasio views/subscriber dalam sebulan pertama
        if video_age_hours < 720: # Kira-kira 1 bulan
            view_sub_ratio = views / subscribers if subscribers > 0 else 0
            if view_sub_ratio > 1.5:
                return 25 # Views > 150% dari subs, sangat bagus
            if view_sub_ratio > 0.75:
                return 20 # Views > 75% dari subs, bagus
            if view_sub_ratio > 0.25:
                return 15 # Views > 25% dari subs, cukup baik

        return 10 # Skor dasar untuk performa standar

    def _calculate_engagement_score(self, metadata: VideoMetadata) -> int:
        """
        Menghitung skor berdasarkan rasio suka dan komentar.
        Ambang batas disesuaikan dengan metrik yang diminta.
        """
        if not metadata.view_count or metadata.view_count < 100:
            return 5 # Views terlalu rendah untuk dianalisis

        views = metadata.view_count
        likes = metadata.like_count or 0
        comments = metadata.comment_count or 0
        
        like_rate = (likes / views) if views > 0 else 0
        comment_rate = (comments / views) if views > 0 else 0
        
        engagement_score = 0

        # Skor dari Like Rate
        if like_rate >= 0.05: # >5% (Luar biasa)
            engagement_score += 20
        elif like_rate >= 0.04: # >4% (Sangat Baik)
            engagement_score += 15
        elif like_rate >= 0.025: # >2.5% (Baik)
            engagement_score += 10
        else:
            engagement_score += 5

        # Skor dari Comment Rate
        if comment_rate >= 0.01: # >1% (Sangat Aktif)
            engagement_score += 15
        elif comment_rate >= 0.005: # >0.5% (Aktif)
            engagement_score += 10
        else:
            engagement_score += 5
            
        return min(engagement_score, 30) # Batas atas skor engagement

    def _calculate_title_score(self, title: str) -> int:
        """Menghitung skor berdasarkan kualitas judul (clickbait vs. informatif)."""
        title_lower = title.lower()
        score = 0
        
        # Kata kunci pemicu rasa penasaran (positif)
        curiosity_keywords = [
            "rahasia", "terbongkar", "ternyata", "begini cara", "langkah demi langkah",
            "terbukti", "ampuh", "ajaib", "tanpa modal", "wajib tahu", "pemula", "expert"
        ]
        if any(re.search(r'\b' + re.escape(kw) + r'\b', title_lower) for kw in curiosity_keywords):
            score += 10

        # Penggunaan angka (misal: "7 Cara...", "Top 5...")
        if re.search(r'\d+', title_lower):
            score += 5

        # Judul yang terlalu pendek atau terlalu panjang
        if 40 <= len(title) <= 70:
            score += 5 # Panjang optimal
            
        return min(score, 15)

    def _calculate_content_quality_score(self, content: str, title: str) -> int:
        """Menganalisis kualitas dan tipe konten dari transkrip."""
        text_to_scan = (title + " " + content).lower()
        score = 0
        
        content_map = {
            "tutorial": ["how to", "guide", "tutorial", "cara membuat", "langkah"],
            "edukasi": ["penjelasan", "sejarah", "sains", "belajar", "riset"],
            "review": ["review", "ulasan", "unboxing", "vs", "impresi"],
            "storytelling": ["cerita saya", "pengalaman", "perjalanan", "kisah"],
        }
        
        detected_types = sum(1 for type_keys in content_map.values() if any(key in text_to_scan for key in type_keys))
        
        score += detected_types * 5
        
        # Panjang konten sebagai indikator kedalaman
        word_count = len(content.split())
        if word_count > 1500:
            score += 10 # Deep-dive
        elif word_count > 500:
            score += 5 # Cukup mendalam
        
        return min(score, 20)

    async def calculate_viral_score(
        self,
        content: str,
        metadata: VideoMetadata
    ) -> int:
        """
        Orkestrasi perhitungan skor viral berdasarkan metrik gabungan.
        """
        try:
            # 1. Skor Kecepatan Views (Bobot Paling Tinggi)
            velocity_score = self._calculate_view_velocity_score(metadata)

            # 2. Skor Engagement (Suka & Komentar)
            engagement_score = self._calculate_engagement_score(metadata)

            # 3. Skor Judul
            title_score = self._calculate_title_score(metadata.title)
            
            # 4. Skor Kualitas Konten
            quality_score = self._calculate_content_quality_score(content, metadata.title)

            # Penjumlahan total skor
            total_score = velocity_score + engagement_score + title_score + quality_score
            
            # Normalisasi skor akhir
            final_score = max(0, min(100, total_score))
            
            logger.info(
                f"Viral score calculated: "
                f"Velocity({velocity_score}) + Engagement({engagement_score}) + "
                f"Title({title_score}) + Quality({quality_score}) = {final_score}"
            )
            return final_score

        except Exception as e:
            logger.error(f"Error calculating final viral score: {str(e)}", exc_info=True)
            return 50 # Nilai fallback jika terjadi error