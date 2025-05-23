import logging
import os
from typing import Annotated, Optional
from collections import OrderedDict

import vtk

import slicer
from slicer.i18n import tr as _
from slicer.i18n import translate
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
"""from slicer.parameterNodeWrapper import (
    parameterNodeWrapper,
    WithinRange,
)"""

import logging

from slicer import vtkMRMLScalarVolumeNode

# Check if omero-py is installed, install it if necessary
try:
    from omero.gateway import BlitzGateway
except ImportError:
    slicer.util.pip_install("omero-py")

    # Attempt to import again after installation
    try:
        from omero.gateway import BlitzGateway
    except ImportError:
        logging.error("Failed to install omero-py. Please install it manually.")


import numpy as np



#
# OMEROImporter
#


class OMEROImporter(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = _("OMEROImporter")  # TODO: make this more human readable by adding spaces
        # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.categories = [translate("qSlicerAbstractCoreModule", "OMERO")]
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["Niraj Kandpal (University of Cologne)"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        # _() function marks text as translatable to other languages
        self.parent.helpText = _("""This is an extension to read data from OMERO into 3D Slicer.""")
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = _(""" NFDI4Bioimage """)

   
#
# OMEROImporterParameterNode
#

#
# OMEROImporterWidget
#


class OMEROImporterWidget(ScriptedLoadableModuleWidget):

    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)
        
        # Load UI from .ui file
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/OMEROImporter.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)
        
        # Connections
        self.ui.connectButton.clicked.connect(self.onConnectButton)
        self.ui.importButton.clicked.connect(self.onImportButton)

    def onConnectButton(self):
        username = self.ui.usernameEdit.text
        password = self.ui.passwordEdit.text
        server = self.ui.serverEdit.text
        port = int(self.ui.portEdit.text)
        
        try:
            self.conn = BlitzGateway(username, password, host=server, port=port)
            self.conn.connect()
            if self.conn.connect() == True:
                logging.info("Connected to OMERO server")
                slicer.util.infoDisplay("Connected to OMERO server")
            else:
                logging.info("Could not connect to OMERO server")
                slicer.util.infoDisplay("Could not Connect to OMERO.")
        except Exception as e:
            logging.error(f"Failed to connect to OMERO server: {e}")
            slicer.util.errorDisplay(f"Failed to connect to OMERO server: {e}")


    def onImportButton(self):
        imageId = int(self.ui.imageIdEdit.text)
        
        try:
            # Get the image
            image = self.conn.getObject("Image", imageId)
            if not image:
                raise Exception(f"Image with ID {imageId} not found")
            
            imageName = image.getName()
            print(f"Image Name: {imageName}")
            
            # Get the imported files
            imported_files = image.getImportedImageFiles()
            if not imported_files:
                raise Exception("No imported files found for this image")
                
            # Get the first imported file (usually the original .nrrd)
            original_file = next(imported_files)
                
            # Create a temporary file path
            temp_nrrd_path = f"{imageName}"
            print(f"Temporary file path: {temp_nrrd_path}")
            
            # Download the file
            print(f"Downloading original file to {temp_nrrd_path}...")
            with open(temp_nrrd_path, 'wb') as f:
                for chunk in original_file.getFileInChunks():
                    f.write(chunk)
        
            # Load the file in Slicer
            print("Loading file in Slicer...")
            volumeNode = slicer.util.loadVolume(temp_nrrd_path)
            volumeNode.SetName(f"{imageName}")
        
            # Clean up the temporary file
            print("Cleaning up temporary file...")
            os.remove(temp_nrrd_path)
        
            print("Done!")
            return volumeNode
        
        except Exception as e:
            slicer.util.errorDisplay(f"Failed to import image: {e}")
            return

class OMEROImporterLogic(ScriptedLoadableModuleLogic):
    pass
