import logging
import os
from typing import Annotated, Optional

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
        self.parent.contributors = ["Niraj Kandpal (University of)"]  # TODO: replace with "Firstname Lastname (Organization)"
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
            logging.info("Connected to OMERO server")
            slicer.util.infoDisplay("Connected to OMERO server")
        except Exception as e:
            slicer.util.errorDisplay(f"Failed to connect to OMERO server: {e}")


    def onImportButton(self):
        imageId = int(self.ui.imageIdEdit.text)
        
        try:
            image, pixels = self.fetch_image_from_omero(imageId)
            
            # Get pixel data
            size_z = image.getSizeZ()
            size_y = image.getSizeY()
            size_x = image.getSizeX()
            size_c = image.getSizeC()
            
            # Dispaly information while data is being read. Large data long waiting time.
            slicer.util.infoDisplay("Reading and downloading image. Might take some time.")
            
            z_stack = np.zeros((size_z, size_y, size_x), dtype=np.uint16)

            # For 3D image only with 0 channels and 0 time points.    
            for z in range(size_z):
                  plane = pixels.getPlane(z, 0, 0)  # z, c, t
                  z_stack[z, :, :] = plane
            
            
            # Create volume node
            volumeNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLScalarVolumeNode')
            volumeNode.SetName(f"OMEROImage_{image.getId()}")

            
            # Set image data from numpy array.
            slicer.util.updateVolumeFromArray(volumeNode, z_stack)
            
            # Set origin to center the volume in the viewer
            volumeNode.SetOrigin(0, 0, 0)
    
    	    # Set spacing
            #volumeNode.SetSpacing(1.0,1.0,1.0)
            
            # Display the volume.
            slicer.util.setSliceViewerLayers(background=volumeNode)
            

            logging.info("Imported 3D image from OMERO")
        except Exception as e:
            slicer.util.errorDisplay(f"Failed to import image: {e}")

    def fetch_image_from_omero(self, imageId):
        # Fetch image and pixels from OMERO
        image = self.conn.getObject("Image", imageId)
        pixels = image.getPrimaryPixels()
        #pixels = self.conn.getObject("Pixels", pixels.getId())
        
        return image, pixels

class OMEROImporterLogic(ScriptedLoadableModuleLogic):
    pass
