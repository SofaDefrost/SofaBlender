cmake_minimum_required(VERSION 3.12)
project(SOFABlender VERSION 1.0 LANGUAGES CXX)

find_package(Sofa.Config REQUIRED)
sofa_find_package(Sofa.Simulation.Core REQUIRED)
sofa_find_package(Sofa.Component.Visual REQUIRED)

# List all files
set(SOFABLENDER_SRC_DIR src/${PROJECT_NAME})
set(HEADER_FILES
    ${SOFABLENDER_SRC_DIR}/config.h.in

    ${SOFABLENDER_SRC_DIR}/BlenderClient.h
    ${SOFABLENDER_SRC_DIR}/json/json.hpp
)
set(SOURCE_FILES
    ${SOFABLENDER_SRC_DIR}/init.cpp

    ${SOFABLENDER_SRC_DIR}/BlenderClient.cpp
)
set(README_FILES
    README.md
)

sofa_find_package(Boost COMPONENTS system REQUIRED)
include_directories(${Boost_INCLUDE_DIRS})

# Create the plugin library.
add_library(${PROJECT_NAME} SHARED ${HEADER_FILES} ${SOURCE_FILES} ${README_FILES})

target_link_libraries(${PROJECT_NAME} Sofa.Simulation.Core Sofa.Component.Visual ${Boost_LIBRARIES})

# Create package Config, Version & Target files.
# Deploy the headers, resources, scenes & examples.
# Set the plugin 'relocatable' if built within SOFA.
# --> see SofaMacros.cmake
sofa_create_package_with_targets(
    PACKAGE_NAME ${PROJECT_NAME}
    PACKAGE_VERSION ${PROJECT_VERSION}
    TARGETS ${PROJECT_NAME} AUTO_SET_TARGET_PROPERTIES
    INCLUDE_SOURCE_DIR "src"
    INCLUDE_INSTALL_DIR ${PROJECT_NAME}
    RELOCATABLE "plugins"
)
