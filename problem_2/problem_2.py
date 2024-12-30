import os
import logging
import csv
import numpy as np
from typing import Optional, List, Tuple
from datetime import datetime
import pydicom
import png

#instalar librerias numpy , pydicom ,pypng

class FileProcessor:
    def __init__(self, base_path: str, log_file: str):
        self.base_path = base_path
        
        # Configuración del logger
        self.logger = logging.getLogger('FileProcessor')
        self.logger.setLevel(logging.INFO)
        
        # Crear el manejador de archivo
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Crear el formato del log
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Agregar el manejador al logger
        self.logger.addHandler(file_handler)

    def list_folder_contents(self, folder_name: str, details: bool = False) -> None:
        try:
            # Verificar si la carpeta existe
            folder_path = os.path.join(self.base_path, folder_name)
            if not os.path.exists(folder_path):
                self.logger.error(f"La carpeta {folder_path} no existe")
                print(f"La carpeta {folder_path} no existe")
                return

            # Listar los elementos de la carpeta
            items = os.listdir(folder_path)
            print(f"\nCarpeta: {folder_path}")
            print(f"Número de elementos: {len(items)}")

            files = []
            folders = []

            for item in items:
                item_path = os.path.join(folder_path, item)
                if os.path.isfile(item_path):
                    if details:
                        size_mb = os.path.getsize(item_path) / (1024 * 1024)
                        modified_time = datetime.fromtimestamp(os.path.getmtime(item_path))
                        files.append(f"- {item} ({size_mb:.1f} MB, Última modificación: {modified_time})")
                    else:
                        files.append(f"- {item}")
                else:
                    if details:
                        modified_time = datetime.fromtimestamp(os.path.getmtime(item_path))
                        folders.append(f"- {item} (Última modificación: {modified_time})")
                    else:
                        folders.append(f"- {item}")

            if files:
                print("\nArchivos:")
                for f in files:
                    print(f)
            if folders:
                print("\nCarpetas:")
                for f in folders:
                    print(f)

        except Exception as e:
            self.logger.error(f"Error al listar contenido de la carpeta: {str(e)}")
            raise

    def read_csv(self, filename: str, report_path: str = None, summary: bool = False) -> None:
        try:
            file_path = os.path.join(self.base_path, filename)
            if not os.path.exists(file_path):
                self.logger.error(f"El archivo {file_path} no existe")
                print(f"El archivo {file_path} no existe")
                return

            with open(file_path, 'r') as file:
                csv_reader = csv.reader(file)
                headers = next(csv_reader)
                data = list(csv_reader)

            print("\nAnálisis CSV:")
            print(f"Columnas: {headers}")
            print(f"Filas: {len(data)}")

            # Convertir a numpy array para análisis numérico
            data_array = np.array(data)
            numeric_cols = []
            non_numeric_cols = []

            for i, col in enumerate(headers):
                try:
                    numeric_data = np.array(data_array[:, i], dtype=float)
                    avg = np.mean(numeric_data)
                    std = np.std(numeric_data)
                    numeric_cols.append((col, avg, std))
                except ValueError:
                    non_numeric_cols.append((col, data_array[:, i]))

            print("\nColumnas Numéricas:")
            for col, avg, std in numeric_cols:
                print(f"- {col}: Promedio = {avg:.1f}, Desv. Est = {std:.1f}")

            if summary and non_numeric_cols:
                print("\nResumen No Numérico:")
                for col, values in non_numeric_cols:
                    unique_values = np.unique(values)
                    print(f"- {col}: Valores Únicos = {len(unique_values)}")

            if report_path:
                os.makedirs(report_path, exist_ok=True)
                report_file = os.path.join(report_path, f"report_{filename}.txt")
                with open(report_file, 'w') as f:
                    f.write("Reporte de Análisis CSV\n\n")
                    for col, avg, std in numeric_cols:
                        f.write(f"{col}: Promedio = {avg:.1f}, Desv. Est = {std:.1f}\n")
                print(f"\nReporte guardado en {report_file}")

        except Exception as e:
            self.logger.error(f"Error al procesar archivo CSV: {str(e)}")
            raise

    def read_dicom(self, filename: str, tags: Optional[List[Tuple[int, int]]] = None, extract_image: bool = False) -> None:
        try:
            file_path = os.path.join(self.base_path, filename)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"El archivo {file_path} no existe")

            dicom = pydicom.dcmread(file_path)
            
            print("\nAnálisis DICOM:")
            print(f"Nombre del Paciente: {dicom.PatientName}")
            print(f"Fecha de Estudio: {dicom.StudyDate}")
            print(f"Modalidad: {dicom.Modality}")

            if tags:
                print("\nTags solicitados:")
                for tag in tags:
                    value = dicom[tag].value
                    print(f"Tag {tag[0]:04x}, {tag[1]:04x}: {value}")

            if extract_image:
                if hasattr(dicom, 'pixel_array'):
                    image = dicom.pixel_array
                    jpeg_file = os.path.join(self.base_path, f"{filename}.JPEG")
                    
                    # Normalizar y convertir a escala de grises si es necesario
                    if len(image.shape) > 2:
                        image = np.mean(image, axis=2)
                    
                    # Normalizar a 8 bits
                    image = ((image - image.min()) * 255.0 / (image.max() - image.min())).astype(np.uint8)
                    
                    # Guardar como PNG
                    with open(jpeg_file, 'wb') as jpeg_file:
                        writer = png.Writer(image.shape[1], image.shape[0], greyscale=True)
                        writer.write(jpeg_file, image.tolist())
                    
                    print(f"\nImagen extraída guardada como {jpeg_file}")
                else:
                    raise ValueError("El archivo DICOM no contiene datos de imagen")

        except Exception as e:
            self.logger.error(f"Error al procesar archivo DICOM: {str(e)}")
            raise

# Se define funcion main para ejecutar el programa
def main():
    try:
        # Se inicializa la opción
        op = 0

        # Se crea el procesador de archivos
        processor = FileProcessor(base_path="/home/juan/Documents/imexhs/developer_test_py_ang/solución/problem_2", log_file="file_processor.log")
        while op != 4:
            print("\nSeleccione una opción:")
            print("1. Listar archivos de la carpeta una carpeta")
            print("2. Leer archivo CSV")
            print("3. Leer archivo DICOM")
            print("4. Salir")
            op = int(input("Opción: "))

            if op == 1:
                while True:
                    # Se solicita al usuario si desea ver detalles de los archivos
                    details = input("¿Desea ver detalles de los archivos? (s/n): ")

                    #se valida que la respuesta sea s o n
                    if details.lower() not in ['s', 'n']:
                        print("Respuesta inválida")
                    else:
                        break
                #se asigna la respuesta a la variable details
                details = details.lower() == 's'

                # Se solicita el nombre de la carpeta
                folder_name = input("Ingrese el nombre de la carpeta: ")

                # Se listan los archivos de la carpeta
                processor.list_folder_contents(folder_name, details)
                input("Presione Enter para continuar...")
            elif op == 2:
                while True:
                    # Se solicita al usuario si desea ver resumen
                    summary = input("¿Desea ver resumen? (s/n): ")
                    #se valida que la respuesta sea s o n
                    if summary.lower() not in ['s', 'n']:
                        print("Respuesta inválida")
                    else:
                        break

                #se pide el nombre del archivo csv
                filename = input("Ingrese el nombre del archivo CSV: ")

                while True:
                    # Se solicita al usuario si archivo report
                    report = input("¿Desea reporte? (s/n): ")
                    #se valida que la respuesta sea s o n
                    if report.lower() not in ['s', 'n']:
                        print("Respuesta inválida")
                    else:
                        break
                if report.lower() == 's':
                    #solicta el nombre del reporte
                    report_path = input("Ingrese el nombre del reporte: ")
                else:
                    report_path = None

                summary = summary.lower() == 's'
                # Se lee el archivo CSV
                processor.read_csv(filename, report_path,summary)
                input("Presione Enter para continuar...")
            elif op == 3:
                # Se solicita el archivo DICOM
                filename = input("Ingrese el nombre del archivo DICOM: ")

                while True:
                    # Se solicita al usuario si desea ver resumen
                    extract_img = input("¿Desea guardar la imagen como JPEG? (s/n): ")
                    #se valida que la respuesta sea s o n
                    if extract_img.lower() not in ['s', 'n']:
                        print("Respuesta inválida")
                    else:
                        break
                
                #se asigna la respuesta a la variable extract_img
                extract_img = extract_img.lower() == 's'

                while True:
                    #Se solicitan números de etiquetas
                    tags = input("¿Desea ver etiquetas? (s/n): ")
                    #se valida que la respuesta sea s o n
                    if tags.lower() not in ['s', 'n']:
                        print("Respuesta inválida")
                    else:
                        break

                # Se lee el archivo DICOM
                processor.read_dicom(filename, extract_img)
                input("Presione Enter para continuar...")
            elif op == 4:
                print("Saliendo...")
            else:
                print("Opción inválida")
    except Exception as e:
        print("Error inesperado:")
        input("Presione Enter para continuar...")
        #volver a ejecutar el programa
        main()


# Se ejecuta la funcion main
if __name__ == "__main__":
    main()  