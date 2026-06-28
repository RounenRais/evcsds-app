from ultralytics import YOLO
import cv2
import os

def predict_images(image_folder):
    model = YOLO(r"C:\EASIOS\runs\detect\runs\electric_meter_detection3\weights\best.pt")
    
    images = [f for f in os.listdir(image_folder) if f.endswith(('.jpg', '.jpeg', '.png'))]
    
    for img_name in images:
        img_path = os.path.join(image_folder, img_name)
        results = model.predict(img_path, conf=0.5)
        
        for result in results:
            img = cv2.imread(img_path)
            
            if len(result.boxes) == 0:
                print(f"{img_name}: ❌ Sayaç bulunamadı")
                cv2.putText(img, "Sayac YOK", (20, 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            else:
                for box in result.boxes:
                    conf = float(box.conf[0])
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    print(f"{img_name}: ✅ Sayaç bulundu! Güven: {conf:.2f} | Konum: ({x1},{y1}) - ({x2},{y2})")
                    
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
                    cv2.putText(img, f"Sayac {conf:.2f}", (x1, y1 - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            
            # Kaydet
            output_path = os.path.join(image_folder, f"result_{img_name}")
            cv2.imwrite(output_path, img)
            
            # Göster - pencere başlığı resim adı olsun
            cv2.imshow(img_name, img)
            print(f"Devam etmek için herhangi bir tuşa bas...")
            cv2.waitKey(0)  # Tuşa basana kadar bekle
            cv2.destroyAllWindows()
        
        print("-" * 50)

predict_images(r"C:\EASIOS\test_images")