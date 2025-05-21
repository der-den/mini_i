#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Skript zum Testen verschiedener Prüfziffernalgorithmen für Barcodes
"""

def test_mod10(barcode_without_check, check_digit):
    """Test für Modulo-10-Prüfziffer (Standard für viele Barcodes)"""
    digits = [int(d) for d in barcode_without_check]
    # Gewichtung von rechts nach links mit 3,1,3,1,...
    weights = [3, 1] * (len(digits) // 2 + 1)
    # Schneide auf die richtige Länge
    weights = weights[:len(digits)]
    # Drehe um, da wir von rechts nach links arbeiten
    digits.reverse()
    weights = weights[:len(digits)]
    
    # Berechne die gewichtete Summe
    weighted_sum = sum(d * w for d, w in zip(digits, weights))
    
    # Berechne die Prüfziffer
    calculated_check = (10 - (weighted_sum % 10)) % 10
    
    return {
        'name': 'Modulo-10 (3,1 Gewichtung)',
        'match': calculated_check == check_digit,
        'calculated': calculated_check,
        'expected': check_digit
    }

def test_mod10_alternate(barcode_without_check, check_digit):
    """Test für alternative Modulo-10-Prüfziffer (1,3 Gewichtung)"""
    digits = [int(d) for d in barcode_without_check]
    # Gewichtung von rechts nach links mit 1,3,1,3,...
    weights = [1, 3] * (len(digits) // 2 + 1)
    # Schneide auf die richtige Länge
    weights = weights[:len(digits)]
    # Drehe um, da wir von rechts nach links arbeiten
    digits.reverse()
    weights = weights[:len(digits)]
    
    # Berechne die gewichtete Summe
    weighted_sum = sum(d * w for d, w in zip(digits, weights))
    
    # Berechne die Prüfziffer
    calculated_check = (10 - (weighted_sum % 10)) % 10
    
    return {
        'name': 'Modulo-10 (1,3 Gewichtung)',
        'match': calculated_check == check_digit,
        'calculated': calculated_check,
        'expected': check_digit
    }

def test_luhn(barcode_without_check, check_digit):
    """Test für Luhn-Algorithmus (Modulo 10 Double Add Double)"""
    digits = [int(d) for d in barcode_without_check]
    # Drehe um, da wir von rechts nach links arbeiten
    digits.reverse()
    
    # Verdopple jede zweite Ziffer
    for i in range(1, len(digits), 2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9
    
    # Berechne die Summe
    total = sum(digits)
    
    # Berechne die Prüfziffer
    calculated_check = (10 - (total % 10)) % 10
    
    return {
        'name': 'Luhn-Algorithmus',
        'match': calculated_check == check_digit,
        'calculated': calculated_check,
        'expected': check_digit
    }

def test_mod11(barcode_without_check, check_digit):
    """Test für Modulo-11-Prüfziffer"""
    digits = [int(d) for d in barcode_without_check]
    # Gewichtung von rechts nach links mit 2,3,4,5,6,7,2,3,...
    weights = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
    # Schneide auf die richtige Länge
    weights = weights[:len(digits)]
    # Drehe um, da wir von rechts nach links arbeiten
    digits.reverse()
    weights = weights[:len(digits)]
    
    # Berechne die gewichtete Summe
    weighted_sum = sum(d * w for d, w in zip(digits, weights))
    
    # Berechne die Prüfziffer
    mod = weighted_sum % 11
    if mod == 0:
        calculated_check = 0
    elif mod == 1:
        calculated_check = 'X'  # Manchmal wird X für 10 verwendet
    else:
        calculated_check = 11 - mod
    
    # Konvertiere zu int für den Vergleich, wenn möglich
    if calculated_check != 'X':
        calculated_check = int(calculated_check)
    
    return {
        'name': 'Modulo-11',
        'match': calculated_check == check_digit,
        'calculated': calculated_check,
        'expected': check_digit
    }

def test_simple_sum(barcode_without_check, check_digit):
    """Test für einfache Quersumme modulo 10"""
    digits = [int(d) for d in barcode_without_check]
    total = sum(digits)
    calculated_check = total % 10
    
    return {
        'name': 'Einfache Quersumme (mod 10)',
        'match': calculated_check == check_digit,
        'calculated': calculated_check,
        'expected': check_digit
    }

def test_weighted_sum(barcode_without_check, check_digit):
    """Test für gewichtete Quersumme (Position als Gewicht)"""
    digits = [int(d) for d in barcode_without_check]
    weighted_sum = sum((i+1) * d for i, d in enumerate(digits))
    calculated_check = weighted_sum % 10
    
    return {
        'name': 'Gewichtete Quersumme (Position als Gewicht, mod 10)',
        'match': calculated_check == check_digit,
        'calculated': calculated_check,
        'expected': check_digit
    }

def main():
    # Beispiel aus der Anfrage
    barcode_with_check = "000292565683"
    barcode_without_check = barcode_with_check[:-1]  # Alles außer der letzten Ziffer
    check_digit = int(barcode_with_check[-1])        # Letzte Ziffer
    
    # Entferne führende Nullen für die Anzeige
    barcode_db = barcode_without_check.lstrip('0')
    
    print(f"Barcode mit Prüfziffer: {barcode_with_check}")
    print(f"Barcode ohne Prüfziffer: {barcode_without_check}")
    print(f"Prüfziffer: {check_digit}")
    print(f"In der Datenbank gespeichert als: {barcode_db}")
    print("\nTeste verschiedene Prüfziffernalgorithmen:")
    print("-" * 50)
    
    # Teste verschiedene Algorithmen
    algorithms = [
        test_mod10,
        test_mod10_alternate,
        test_luhn,
        test_mod11,
        test_simple_sum,
        test_weighted_sum
    ]
    
    for algorithm in algorithms:
        result = algorithm(barcode_without_check, check_digit)
        match_str = "✓" if result['match'] else "✗"
        print(f"{match_str} {result['name']}: Berechnet {result['calculated']}, Erwartet {result['expected']}")
    
    print("\nFalls Sie weitere Beispiele testen möchten, fügen Sie diese im Code hinzu.")

if __name__ == "__main__":
    main()
