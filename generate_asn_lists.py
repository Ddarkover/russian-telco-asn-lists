#!/usr/bin/env python3
"""
Скрипт для генерации списков IP-адресов по ASN для Beeline и MegaFon
"""

import requests
import json
import ipaddress
from typing import List, Dict, Set
import time
import sys

# Конфигурация ASN
ASN_CONFIG = {
    'beeline': {
        'name': 'PJSC "Vimpelcom" / BeeLine Russia',
        'asn_list': ['AS3216', 'AS8350', 'AS16345', 'AS205460']
    },
    'megafon': {
        'name': 'PJSC MegaFon',
        'asn_list': ['AS25159', 'AS31133', 'AS31163']
    }
}

def get_asn_prefixes(asn: str) -> List[str]:
    """
    Получает список префиксов для указанного ASN через REST API
    """
    prefixes = []
    
    # Убираем префикс AS если есть
    asn_number = asn.replace('AS', '')
    
    # Основной источник: RIPE Stat API
    try:
        print(f"    Пробуем RIPE Stat API для {asn}...")
        ripe_url = f"https://stat.ripe.net/data/announced-prefixes/data.json?resource={asn}"
        headers = {
            'User-Agent': 'ASN-IP-List-Generator/1.0 (GitHub Actions)'
        }
        response = requests.get(ripe_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'prefixes' in data['data']:
                for prefix_info in data['data']['prefixes']:
                    if 'prefix' in prefix_info:
                        prefixes.append(prefix_info['prefix'])
                print(f"    ✓ RIPE Stat: получено {len(prefixes)} префиксов")
        else:
            print(f"    ✗ RIPE Stat API ошибка: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"    ✗ RIPE Stat API ошибка: {e}")
    
    # Fallback: BGPView API (если RIPE не сработал или вернул мало данных)
    if len(prefixes) < 5:  # Если получили мало префиксов, пробуем второй источник
        try:
            print(f"    Пробуем BGPView API для {asn}...")
            bgpview_url = f"https://api.bgpview.io/asn/{asn_number}/prefixes"
            headers = {
                'User-Agent': 'ASN-IP-List-Generator/1.0 (GitHub Actions)'
            }
            response = requests.get(bgpview_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                bgpview_prefixes = []
                if 'data' in data:
                    if 'ipv4_prefixes' in data['data']:
                        for prefix_info in data['data']['ipv4_prefixes']:
                            if 'prefix' in prefix_info:
                                bgpview_prefixes.append(prefix_info['prefix'])
                    if 'ipv6_prefixes' in data['data']:
                        for prefix_info in data['data']['ipv6_prefixes']:
                            if 'prefix' in prefix_info:
                                bgpview_prefixes.append(prefix_info['prefix'])
                
                # Используем данные BGPView если получили больше префиксов
                if len(bgpview_prefixes) > len(prefixes):
                    prefixes = bgpview_prefixes
                    print(f"    ✓ BGPView: получено {len(prefixes)} префиксов (используем как основные)")
                else:
                    print(f"    ✓ BGPView: получено {len(bgpview_prefixes)} префиксов (оставляем RIPE)")
            else:
                print(f"    ✗ BGPView API ошибка: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"    ✗ BGPView API ошибка: {e}")
    
    # Небольшая задержка между запросами
    time.sleep(2)
    
    return prefixes

def validate_and_sort_prefixes(prefixes: List[str]) -> List[str]:
    """
    Валидирует и сортирует список префиксов
    """
    valid_prefixes = []
    
    for prefix in prefixes:
        try:
            # Проверяем валидность префикса
            network = ipaddress.ip_network(prefix, strict=False)
            valid_prefixes.append(str(network))
        except ValueError:
            print(f"    Невалидный префикс пропущен: {prefix}")
            continue
    
    # Убираем дубликаты и сортируем
    unique_prefixes = list(set(valid_prefixes))
    
    # Сортировка IPv4 и IPv6 отдельно
    ipv4_prefixes = []
    ipv6_prefixes = []
    
    for prefix in unique_prefixes:
        try:
            network = ipaddress.ip_network(prefix)
            if network.version == 4:
                ipv4_prefixes.append(prefix)
            else:
                ipv6_prefixes.append(prefix)
        except ValueError:
            continue
    
    # Сортировка
    ipv4_prefixes.sort(key=lambda x: ipaddress.ip_network(x))
    ipv6_prefixes.sort(key=lambda x: ipaddress.ip_network(x))
    
    return ipv4_prefixes + ipv6_prefixes

def generate_lists_for_provider(provider: str, config: Dict) -> List[str]:
    """
    Генерирует список IP префиксов для указанного провайдера
    """
    print(f"Обрабатываю {config['name']}...")
    all_prefixes = []
    
    for asn in config['asn_list']:
        print(f"  Получаю префиксы для {asn}...")
        prefixes = get_asn_prefixes(asn)
        all_prefixes.extend(prefixes)
        print(f"  Найдено {len(prefixes)} префиксов для {asn}")
    
    # Валидация и сортировка
    valid_prefixes = validate_and_sort_prefixes(all_prefixes)
    print(f"  Итого валидных префиксов: {len(valid_prefixes)}")
    
    return valid_prefixes

def save_txt_file(filename: str, prefixes: List[str], header_info: str):
    """
    Сохраняет префиксы в текстовый файл
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"# {header_info}\n")
        f.write(f"# Сгенерировано: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}\n")
        f.write(f"# Всего префиксов: {len(prefixes)}\n\n")
        
        for prefix in prefixes:
            f.write(f"{prefix}\n")

def save_json_file(filename: str, prefixes: List[str], header_info: str, asn_list: List[str]):
    """
    Сохраняет префиксы в JSON файл
    """
    data = {
        "info": {
            "provider": header_info,
            "generated_at": time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()),
            "asn_list": asn_list,
            "total_prefixes": len(prefixes)
        },
        "prefixes": prefixes
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    """
    Основная функция
    """
    print("Запуск генерации списков ASN IP адресов...")
    
    all_prefixes = []
    combined_info = []
    successful_providers = 0
    
    # Обработка каждого провайдера
    for provider, config in ASN_CONFIG.items():
        prefixes = generate_lists_for_provider(provider, config)
        
        if prefixes and len(prefixes) > 0:
            # Сохранение файлов для провайдера
            save_txt_file(f"{provider}.txt", prefixes, config['name'])
            save_json_file(f"{provider}.json", prefixes, config['name'], config['asn_list'])
            
            # Добавляем к общему списку
            all_prefixes.extend(prefixes)
            combined_info.append(f"{config['name']} ({', '.join(config['asn_list'])})")
            successful_providers += 1
            
            print(f"✓ Сохранены файлы для {provider}")
        else:
            print(f"✗ Не удалось получить данные для {provider}")
    
    # Проверяем, что хотя бы один провайдер обработан успешно
    if successful_providers == 0:
        print("✗ КРИТИЧЕСКАЯ ОШИБКА: Не удалось получить данные ни для одного провайдера!")
        print("Проверьте подключение к интернету и доступность API.")
        return False
    
    # Создание объединенного списка
    if all_prefixes:
        # Убираем дубликаты и сортируем
        combined_prefixes = validate_and_sort_prefixes(all_prefixes)
        combined_header = "Объединенный список: " + " + ".join(combined_info)
        
        # Получаем все ASN
        all_asn = []
        for config in ASN_CONFIG.values():
            all_asn.extend(config['asn_list'])
        
        save_txt_file("asn-list.txt", combined_prefixes, combined_header)
        save_json_file("asn-list.json", combined_prefixes, combined_header, all_asn)
        
        print(f"✓ Сохранен объединенный список (asn-list.txt/json)")
        print(f"  Всего уникальных префиксов: {len(combined_prefixes)}")
        print(f"  Успешно обработано провайдеров: {successful_providers}/{len(ASN_CONFIG)}")
    
    print("Генерация завершена!")
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)  # Завершаем с кодом ошибки если ничего не удалось получить
