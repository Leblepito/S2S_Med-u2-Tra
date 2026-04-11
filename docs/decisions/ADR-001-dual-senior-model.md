# ADR-001: İki Senior Geliştirici Modeli — Rol Dağılımı
Tarih: 2026-03-23
Durum: Kabul Edildi

## Bağlam
BabelFlow projesinde iki Claude Code instance paralel çalışacak. Rol dağılımı gerekiyor.

## Alternatifler
| Seçenek | Artı | Eksi |
|---------|------|------|
| İki eşit senior (paralel) | Hızlı | Deadlock, merge conflict |
| Senior + Junior | Basit | Junior hata görse susar |
| **İki senior, farklı şapka** | **Kaliteli + hızlı** | **Biraz daha fazla iletişim** |

## Karar
- **VSCode Claude Code = Senior Mimar**: Plan yazar, review eder, frontend implement eder, tie-breaker
- **Terminal Claude Code = Senior Mühendis**: Backend implement eder, TDD, mimari gözlem/itiraz hakkı var

Çünkü: VSCode instance plan dosyasına, superpowers skill'lerine, subagent'lara erişimi var — koordinasyon rolüne daha uygun. Terminal instance'a yapılandırılmış task talimatları vermek verimli.

## Sonuçlar
- İletişim: docs/plans/ + git commit'ler üzerinden
- Mimar frontend, Mühendis backend — paralel çalışma doğal bölünme
- İtiraz mekanizması: plan dosyasının "Mühendisin İtiraz Alanı" bölümü
