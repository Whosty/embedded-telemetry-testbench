import time
import random

# ==============================================================================
# DONANIM BAĞLANTI AYARI:
# Kartın takılı olduğunda True yapıp portunu yazacaksın.
# Şimdilik kart yanında olmadığı için False bırakıyoruz, canlı simülasyon akacak.
# ==============================================================================
REAL_HARDWARE = False
COM_PORT = 'COM3'
BAUD_RATE = 115200

def dummy_serial_stream():
    """Gerçek kart yokken USB kablosundan akan parazitli bayt akışını simüle eder."""
    # Bazen araya 0x12 gibi gürültü baytı atar, bazen doğru paket yollar
    if random.random() < 0.1:
        return bytes([0x12]) # Hat paraziti
    
    val = random.randint(200, 950) # Rastgele analog sensör verisi
    btn = random.choice([0, 1])     # Rastgele buton durumu
    
    h_byte = (val >> 8) & 0xFF
    l_byte = val & 0xFF
    
    # 5 Baytlık paketimiz
    return bytes([0xAA, h_byte, l_byte, btn, 0x55])

def main():
    ser = None
    if REAL_HARDWARE:
        import serial
        try:
            ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
            print(f"[BAĞLANDI] {COM_PORT} dinleniyor...")
            time.sleep(2) # Arduino'nun reset atmasını bekle
        except Exception as e:
            print(f"[HATA] Porta bağlanılamadı: {e}")
            return
    else:
        print("[SİMÜLASYON MODU] Sanal USB hattı dinleniyor... (Durdurmak için Ctrl+C)")

    # Canlı Dinleme Döngüsü
    try:
        while True:
            # 1. ADIM: 0xAA (Header) Avı
            if REAL_HARDWARE:
                byte_in = ser.read(1)
                if not byte_in:
                    continue
                first_byte = byte_in[0]
            else:
                # Simülasyon modunda hattan bayt akışı çekiyoruz
                time.sleep(0.05) # Saniyede 20 paket hızı
                stream = dummy_serial_stream()
                first_byte = stream[0]

            # Başlangıç damgası yakalandı mı?
            if first_byte == 0xAA:
                # 2. ADIM: Kalan 4 baytı oku
                if REAL_HARDWARE:
                    remaining = ser.read(4)
                    if len(remaining) < 4:
                        continue # Veri eksik geldiyse atla
                    payload = list(remaining)
                else:
                    if len(stream) < 5:
                        continue
                    payload = list(stream[1:])

                high_byte = payload[0]
                low_byte = payload[1]
                button_state = payload[2]
                tail = payload[3]

                # 3. ADIM: Bitiş damgası doğrulama
                if tail == 0x55:
                    sensor_val = (high_byte << 8) | low_byte
                    btn_str = "BASILI   " if button_state == 1 else "BIRAKILDI"
                    print(f"-> [PAKET OKUNDU] Sensör: {sensor_val:4d} | Buton: {btn_str}")
                else:
                    print("-> [UYARI] Bitiş damgası hatalı, paket çöpe atıldı!")

    except KeyboardInterrupt:
        print("\n[DURDURULDU] Kullanıcı programı sonlandırdı.")
        if ser and ser.is_open:
            ser.close()

if __name__ == '__main__':
    main()