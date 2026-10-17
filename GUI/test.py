import cv2
import time

print("--- KAMERA TESTİ BAŞLIYOR ---")

# Bilgisayardaki 0, 1 ve 2 numaralı kameraları sırayla dener
for i in range(3):
    print(f"\n[{i}] numaralı kamera deneniyor...")
    cap = cv2.VideoCapture(i)
    
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            # Siyah ekran mı yoksa gerçek görüntü mü test ediliyor
            ortalama_renk = frame.mean()
            if ortalama_renk < 5:
                print(f"[{i}] numaralı kamera AÇILDI ama SİMSİYAH (boş) görüntü veriyor! (Sanal Kamera olabilir)")
            else:
                print(f"[{i}] numaralı kamera BAŞARIYLA GÖRÜNTÜ ALDI! Ekrana yansıtılıyor...")
                cv2.imshow(f"Kamera {i} Testi (Kapatmak icin Q'ya bas)", frame)
                
                # Q tuşuna basana kadar veya 5 saniye boyunca ekranda tut
                timeout = time.time() + 5
                while time.time() < timeout:
                    ret, frame = cap.read()
                    cv2.imshow(f"Kamera {i} Testi (Kapatmak icin Q'ya bas)", frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                cv2.destroyAllWindows()
        else:
            print(f"[{i}] numaralı kameradan kare (frame) okunamadı.")
        cap.release()
    else:
        print(f"[{i}] numaralı kamera bilgisayarda YOK veya ERİŞİM ENGELLENDİ.")

print("\n--- TEST BİTTİ ---")