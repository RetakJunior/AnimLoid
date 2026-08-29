<h1 align="center">AnimLoid</h1>

<p align="center">
  <strong>Anime severler için güçlü, platformlar arası komut satırı aracı</strong>
</p>

<p align="center">
  <a href="https://github.com/RetakJunior/AnimLoid/releases"><img src="https://img.shields.io/github/v/release/RetakJunior/AnimLoid?style=flat-square" alt="Release"></a>
  <a href="https://github.com/RetakJunior/AnimLoid/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-CC%20BY--NC--ND%204.0-blue?style=flat-square" alt="License"></a>
  <a href="https://github.com/RetakJunior/AnimLoid/stargazers"><img src="https://img.shields.io/github/stars/RetakJunior/AnimLoid?style=flat-square" alt="Stars"></a>
  <a href="https://github.com/RetakJunior/AnimLoid/actions"><img src="https://img.shields.io/github/actions/workflow/status/RetakJunior/AnimLoid/tests.yml?style=flat-square" alt="Tests"></a>
</p>

<p align="center">
  <a href="#kurulum">Kurulum</a> •
  <a href="#özellikler">Özellikler</a> •
  <a href="#kullanım">Kullanım</a> •
  <a href="#kaynaklar">Kaynaklar</a> •
  <a href="README-EN.md">English</a>
</p>

---

## Özellikler

### Çoklu Kaynak Desteği

- **Türkçe**: Animecix, Turkanime, Anizle
- **İngilizce**: HiAnime, AllAnime

### Akıllı İzleme

- MPV entegrasyonu ile yüksek kaliteli HLS/MP4 yayınları
- Kaldığınız yerden devam etme (dakika bazında)
- İzleme geçmişi ve istatistikler
- Tamamlanan (✓) ve devam eden (●) bölüm işaretleri

### Güçlü İndirme Sistemi

- **Aria2** ile çoklu bağlantılı hızlı indirme
- **yt-dlp** ile karmaşık yayın desteği
- Kuyruk sistemi ve eşzamanlı indirme
- Yarım kalan indirmeleri devam ettirme
- Akıllı dosya isimlendirme (`Anime Adı - S1B1.mp4`)

### Yerel Kütüphane

- İndirilen animeleri otomatik tarama
- Harici disk desteği (USB, HDD)
- Çevrimdışı anime indexleme
- Tüm kaynaklarda arama

### Ek Özellikler

- SQLite veritabanı (hızlı ve güvenilir)
- İndirme tamamlandığında sistem bildirimi
- Discord RPC entegrasyonu (izlediğiniz anime Discord'da görünsün)
- Arama geçmişi
- Debug modu ve loglama
- Otomatik güncelleme kontrolü

---

## Kurulum

### PyPI (Evrensel)

```bash
pip install animloid
```

### Portable

[Releases](https://github.com/RetakJunior/AnimLoid/releases) sayfasından platformunuza uygun dosyayı indirin.

### Geliştirici Kurulumu

```bash
git clone https://github.com/RetakJunior/AnimLoid.git
cd AnimLoid
pip install -e .
```

---

## Kullanım

```bash
animloid
```

### Klavye Kontrolleri

| Tuş      | İşlev                     |
| -------- | ------------------------- |
| `↑` `↓`  | Menüde gezinme            |
| `Enter`  | Seçim yapma               |
| `s`      | Anime Ara (Ana menüde)    |
| `d`      | İndirmeler (Ana menüde)   |
| `w`      | İzlediklerim (Ana menüde) |
| `c`      | Ayarlar (Ana menüde)      |
| `q`      | Çıkış (Ana menüde)        |
| `Ctrl+C` | Geri dön / Çıkış          |

**Not:** Tüm kısayollar Ayarlar > Klavye Kısayolları menüsünden özelleştirilebilir.

---

## Kaynaklar

| Kaynak    | Dil       |
| --------- | --------- |
| Animecix  | Türkçe    |
| Turkanime | Türkçe    |
| Anizle    | Türkçe    |
| HiAnime   | İngilizce |
| AllAnime  | İngilizce |

---

## Ayarlar

Yapılandırma: `~/.animloid/animloid.db` (SQLite)

| Ayar                       | Açıklama          | Varsayılan             |
| -------------------------- | ----------------- | ---------------------- |
| `aria2_enabled`            | Aria2 kullanımı   | `true`                 |
| `max_concurrent_downloads` | Eşzamanlı indirme | `3`                    |
| `download_dir`             | İndirme klasörü   | `./animloid-downloads` |
| `discord_rpc_enabled`      | Discord RPC       | `false`                |
| `debug_mode`               | Debug loglama     | `false`                |

---

## Lisans

Bu proje [CC BY-NC-ND 4.0](LICENSE) lisansı ile lisanslanmıştır.

---

<p align="center">
  <a href="https://weeb-cli.ewgsta.me">Website</a> •
  <a href="https://github.com/RetakJunior/AnimLoid/issues">Sorun Bildir</a>
</p>
