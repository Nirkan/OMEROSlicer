cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(OMEROImporter)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/OMEROImporter")
set(EXTENSION_CATEGORY "OMERO")
set(EXTENSION_CONTRIBUTORS "Niraj Kandpal (University of Cologne)")
set(EXTENSION_DESCRIPTION "This is an example of a simple extension")
set(EXTENSION_ICONURL "https://www.example.com/Slicer/Extensions/OMEROImporter.png")
set(EXTENSION_SCREENSHOTURLS "https://www.example.com/Slicer/Extensions/OMEROImporter/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(OMEROImporter)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
