import time
import random
from collections import deque
import matplotlib.pyplot as plt

# ==============================================================================
# AYARLAR
# ==============================================================================
REAL_HARDWARE = False  # Kart takılı olduğunda True yapacaksın
COM_PORT = 'COM3'
BAUD_RATE = 115200
BUFFER_SIZE = 100      # Ekranda gösterilecek son 100 veri noktası

# Grafik için halka veri kuyruğu (Son 100 veriyi tutar, yenisi geldikçe eskisi düşer)
veri_kuyrugu = deque([0] * BUFFER_SIZE, maxlen=BUFFER_SIZE)

def dummy_serial_stream():
    """Donanım yokken canlı sinyal ve buton üreten simülatör"""
    # 0-1023 arasında dalgalanan sinyal simülasyonu
    val = random.randint(400, 700)
    btn = 1 if random.random() < 0.2 else 0 # %20 ihtimalle butona basılsın
    
    h_byte = (val >> 8) & 0xFF
    l_byte = val & 0xFF
    return bytes([0xAA, h_byte, l_byte, btn, 0x55])

def main():
    ser = None
    if REAL_HARDWARE:
        import serial
        try:
            ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=0.1)
            print(f"[BAĞLANDI] {COM_PORT} dinleniyor...")
            time.sleep(2)
        except Exception as e:
            print(f"[HATA] Porta bağlanılamadı: {e}")
            return
    else:
        print("[SİMÜLASYON MODU] Canlı osiloskop başlatılıyor...")

    # ==========================================
    # MATPLOTLIB GRAFİK PENCERESİ KURULUMU
    # ==========================================
    plt.ion()  # İnteraktif mod (pencere açıkken kod arkada akmaya devam eder)
    fig, ax = plt.subplots(figsize=(10, 5))
    
    line, = ax.plot(veri_kuyrugu, color='cyan', linewidth=2)
    ax.set_ylim(0, 1024)  # 10-bit analog veri aralığı (0 - 1023)
    ax.set_xlim(0, BUFFER_SIZE)
    ax.set_title("CANLI VERİ İSTASYONU (TELEMETRİ)", fontsize=12, fontweight='bold')
    ax.set_ylabel("Sensör Ham Değeri (ADC)")
    ax.set_xlabel("Zaman (Son 100 Örnek)")
    ax.grid(True, linestyle='--', alpha=0.6)
    
    # Koyu arayüz teması
    fig.patch.set_facecolor('#1e1e1e')
    ax.set_facecolor('#121212')
    ax.tick_params(colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color('white')

    # Canlı Döngü
    try:
        while plt.fignum_exists(fig.number):
            # 1. Bayt Oku / Header Yakala
            if REAL_HARDWARE:
                byte_in = ser.read(1)
                if not byte_in or byte_in[0] != 0xAA:
                    continue
                payload = list(ser.read(4))
                if len(payload) < 4:
                    continue
            else:
                stream = dummy_serial_stream()
                if stream[0] != 0xAA:
                    continue
                payload = list(stream[1:])

            # 2. Paketi Doğrula ve Çöz
            tail = payload[3]
            if tail == 0x55:
                high_byte = payload[0]
                low_byte = payload[1]
                button_state = payload[2]

                sensor_val = (high_byte << 8) | low_byte
                
                # Yeni veriyi kuyruğa ekle
                veri_kuyrugu.append(sensor_val)

                # 3. Grafiği Güncelle
                line.set_ydata(veri_kuyrugu)

                # Butona basıldıysa başlığı kırmızı yap ve uyar
                if button_state == 1:
                    ax.set_title(f"Sensör: {sensor_val} | [BUTON: BASILI (UYARI)]", color='#ff4444')
                    line.set_color('#ff4444')
                else:
                    ax.set_title(f"Sensör: {sensor_val} | [BUTON: NORMAL]", color='#00ffcc')
                    line.set_color('#00ffcc')

                plt.pause(0.01)  # Arayüzün çizilmesi için kısa bir nefes payı

    except KeyboardInterrupt:
        print("\n[DURDURULDU]")
    finally:
        if ser and ser.is_open:
            ser.close()

if __name__ == '__main__':
    main()