import sys
import os
import shutil
import matplotlib.pyplot as plt
from PyQt5.QtGui import QPixmap
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog, QVBoxLayout, QTabWidget, QLabel, QTextEdit, QScrollArea
from pylinac import WinstonLutz
from pylinac.winston_lutz import Axis

class ImageBrowser(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Image Browser')
        self.resize(2000, 1500)

        self.tab_widget = QTabWidget(self)
        self.tab_widget.setGeometry(10, 10, 2000, 2000)

        self.tab_winston_lutz = QWidget()
        self.tab_cbct_qa = QWidget()
        self.tab_starshots = QWidget()

        self.tab_widget.addTab(self.tab_winston_lutz, 'Winston Lutz QA')
        self.tab_widget.addTab(self.tab_cbct_qa, 'CBCT QA')
        self.tab_widget.addTab(self.tab_starshots, 'Starshots')

        self.initWinstonLutzTab()
        self.initCBCTQATab()
        self.initStarshotsTab()

    def initWinstonLutzTab(self):
        self.button_wl = QPushButton('Browse', self.tab_winston_lutz)
        self.button_wl.setGeometry(100, 80, 100, 30)
        self.button_wl.clicked.connect(self.browse_folder)
        self.wl_directory = None
    
        self.analyze_button = QPushButton('Analyze', self.tab_winston_lutz)
        self.analyze_button.setGeometry(220, 80, 100, 30)
        self.analyze_button.clicked.connect(self.analyze_wl)
    
        self.selected_folder_label = QLabel('', self.tab_winston_lutz)
        self.selected_folder_label.setGeometry(50, 120, 600, 100)
    
        self.plot_widget = QWidget(self.tab_winston_lutz)
        self.plot_widget.setGeometry(100, 160, 100, 100)
        self.plot_layout = QVBoxLayout(self.plot_widget)
        self.canvas = FigureCanvas(plt.Figure(figsize=(50, 50)))
        self.plot_layout.addWidget(self.canvas)
    
        # Create the label for displaying the image
        self.label = QLabel(self.tab_winston_lutz)
        self.label.setGeometry(100, 110, 1500, 800)

        # Create the label for displaying the second image
        self.label_iso = QLabel(self.tab_winston_lutz)
        self.label_iso.setGeometry(100, 900, 500, 300)
        
        # Create text box for results
        self.text_edit = QTextEdit(self.tab_winston_lutz)
        self.text_edit.setGeometry(1300, 200, 400, 800)
        self.text_edit.setPlainText('Results will display here:')

    def initCBCTQATab(self):
        # Similar setup for CBCT QA tab
        pass

    def initStarshotsTab(self):
        # Similar setup for Starshots tab
        pass

    def browse_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Select Folder', '.')
        if folder_path:
            self.wl_directory = folder_path
            self.selected_folder_label.setText('Selected Folder: ' + folder_path)
            print('Selected Folder:', folder_path)
            
    def analyze_wl(self):
        if self.wl_directory:
            try:
                wl = WinstonLutz(self.wl_directory)
                wl.analyze()
                results_dict = wl.results_data(as_dict=True)
                
                def format_float_values(dictionary):
                    formatted_dict = {}
                    for key, value in dictionary.items():
                        if isinstance(value, float):
                            formatted_value = "{:.2f}".format(value)
                            formatted_dict[key] = formatted_value
                        else:
                            formatted_dict[key] = value
                    return formatted_dict
                
                formatted_results = format_float_values(results_dict)
                print('Analysis completed.')
                
                
    
                temp_folder = os.path.join(os.getcwd(), 'temp_images')  # Create a temporary folder
                os.makedirs(temp_folder, exist_ok=True)
                temp_analysis_path = os.path.join(temp_folder, 'analysis_image.png')
                temp_iso_path = os.path.join(temp_folder, 'iso_image.png')
    
                # Save the images to the temporary folder
                wl.save_images(temp_analysis_path, axis=Axis.GBP_COMBO)
                fig1 = plt.figure()
                wl.plot_location()
                fig1.savefig(temp_iso_path)
    
                # Load the saved image into the GUI
                pixmap = QPixmap(temp_analysis_path)
                pixmap_width, pixmap_height = pixmap.width(), pixmap.height()
                
                # Load and display the second image
                pixmap_iso = QPixmap(temp_iso_path)
                pixmap_iso_scaled = pixmap_iso.scaledToWidth(800)
                pixmap_iso_scaled_width, pixmap_iso_scaled_height = pixmap_iso_scaled.width(), pixmap_iso_scaled.height()
                
                # Set the geometry of the QLabel widgets based on the pixel sizes of the images
                self.label.setGeometry(100, 200, pixmap_width, pixmap_height)
                self.label_iso.setGeometry(100, pixmap_height+200, pixmap_iso_scaled_width, pixmap_iso_scaled_height)
                
                self.label.setPixmap(pixmap)  # Update the existing label with the new pixmap
                self.label_iso.setPixmap(pixmap_iso_scaled)
                self.label.setScaledContents(True)
                
                self.text_edit.setGeometry(pixmap_width + 120, 200, 400, 800)

                text = f"Results:\n"
                text += f"Max 2D CAX to BB Distance: {formatted_results['max_2d_cax_to_bb_mm']} mm\n"
                text += f"Collimator 2D ISO Diameter: {formatted_results['coll_2d_iso_diameter_mm']} mm\n"
                text += f"Couch 2D ISO Diameter: {formatted_results['couch_2d_iso_diameter_mm']} mm\n"
                text += f"Gantry 3D ISO Diameter: {formatted_results['gantry_3d_iso_diameter_mm']} mm\n"
                text += f"Max 2D CAX to EPID Distance: {formatted_results['max_2d_cax_to_epid_mm']} mm\n"
                text += f"Max Couch RMS Deviation: {formatted_results['max_couch_rms_deviation_mm']} mm\n"
                
                self.text_edit.setPlainText(text)
    
                # Clean up: Delete the temporary folder and file after displaying the image
                self.cleanup_temp_files(temp_folder)
                
                

            except Exception as e:
                print('Error during analysis:', e)
        else:
            print('Please select a folder first.')

    def cleanup_temp_files(self, temp_folder):
        # Delete the temporary folder and its contents
        try:
            shutil.rmtree(temp_folder)
        except OSError as e:
            print('Error deleting temporary files:', e)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageBrowser()
    window.show()
    sys.exit(app.exec_())


