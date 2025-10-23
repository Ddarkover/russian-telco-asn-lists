# Russian Telco ASN Lists

Автоматически обновляемые списки IP-адресов российских телекоммуникационных операторов Beeline и MegaFon на основе их ASN (Autonomous System Numbers).

## 📋 Генерируемые файлы

- **`beeline.txt`** / **`beeline.json`** - IP префиксы Beeline
- **`megafon.txt`** / **`megafon.json`** - IP префиксы MegaFon  
- **`asn-list.txt`** / **`asn-list.json`** - объединенные списки обоих операторов

## 🔄 Обновление

- **Автоматически**: каждое воскресенье в 02:00 UTC
- **Вручную**: через GitHub Actions → "Run workflow"

## 🏢 Покрываемые ASN

### Beeline (PJSC "Vimpelcom")
- AS3216
- AS8350  
- AS16345
- AS205460

### MegaFon (PJSC MegaFon)
- AS25159
- AS31133
- AS31163

## 📊 Источники данных

1. **RIPE Stat API** (основной)
2. **BGPView API** (резервный)

## 📁 Формат файлов

### Plain Text (.txt)
```
# PJSC "Vimpelcom" / BeeLine Russia
# Сгенерировано: 2024-01-15 10:30:00 UTC
# Всего префиксов: 150

1.2.3.0/24
5.6.7.0/24
...
```

### JSON (.json)
```json
{
  "info": {
    "provider": "PJSC \"Vimpelcom\" / BeeLine Russia",
    "generated_at": "2024-01-15 10:30:00 UTC",
    "asn_list": ["AS3216", "AS8350", "AS16345", "AS205460"],
    "total_prefixes": 150
  },
  "prefixes": [
    "1.2.3.0/24",
    "5.6.7.0/24"
  ]
}
```

## 🛠️ Настройка

1. Создайте файл `.github/workflows/update-asn-lists.yml`
2. Создайте файл `generate_asn_lists.py` 
3. В настройках репозитория включите "Read and write permissions" для Actions
4. Запустите workflow вручную для первой генерации

## 🎯 Применение

- Настройка файрволлов и маршрутизации
- Геолокация IP-адресов  
- Анализ сетевого трафика
- Блокировка или разрешение доступа по провайдерам

## ⚙️ Кастомизация

### Изменение расписания
```yaml
schedule:
  - cron: '0 6 * * 1'  # Каждый понедельник в 06:00 UTC
```

### Добавление новых ASN
```python
ASN_CONFIG = {
    'beeline': {
        'name': 'PJSC "Vimpelcom" / BeeLine Russia',
        'asn_list': ['AS3216', 'AS8350', 'AS16345', 'AS205460', 'AS_NEW']
    }
}
```

---

*Данные обновляются автоматически и содержат актуальную информацию о сетевых префиксах операторов.*
