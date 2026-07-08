cmake_minimum_required(VERSION 3.22)
project(adas-sil VERSION 0.1.0 LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)

find_package(AdasInterfaces REQUIRED)

# plan.md item 2 - walking skeleton only: this links directly against the
# already-built Release artifacts of perception-core and df (their own
# build.bat must be run first) instead of rebuilding either from source or
# packaging them as real Conan dependencies. Not yet wired into build.py's
# automatic component ordering - see docs/sil_integration_host.md for why, and
# what upgrading this to a real dependency would take.
set(PCORE_BUILD_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../perception-core/build-sil-vs2026/src")
set(DF_SIL_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../df/build-sil-vs2026/src/platform/df_sil")

if(NOT EXISTS "${PCORE_BUILD_DIR}/platform/sil/Release/perception_core_sil.lib")
    message(FATAL_ERROR "perception-core hasn't been built yet - run: modules\\perception-core\\build.bat base sil vs2026")
endif()
if(NOT EXISTS "${DF_SIL_DIR}/Release/df_sil.dll")
    message(FATAL_ERROR "df hasn't been built yet - run: modules\\df\\build.bat base sil vs2026")
endif()

add_library(perception_core_imported STATIC IMPORTED)
set_target_properties(perception_core_imported PROPERTIES
    IMPORTED_LOCATION "${PCORE_BUILD_DIR}/component/Release/perception_core.lib"
)

add_library(perception_core_sil_imported STATIC IMPORTED)
set_target_properties(perception_core_sil_imported PROPERTIES
    IMPORTED_LOCATION "${PCORE_BUILD_DIR}/platform/sil/Release/perception_core_sil.lib"
)

add_library(df_sil_imported SHARED IMPORTED)
set_target_properties(df_sil_imported PROPERTIES
    IMPORTED_LOCATION "${DF_SIL_DIR}/Release/df_sil.dll"
    IMPORTED_IMPLIB "${DF_SIL_DIR}/Release/df_sil.lib"
)
target_include_directories(df_sil_imported INTERFACE
    "${CMAKE_CURRENT_SOURCE_DIR}/../df/src/platform/df_sil"
)

add_executable(sil main.cpp)
target_link_libraries(sil PRIVATE
    perception_core_sil_imported
    perception_core_imported
    df_sil_imported
    AdasInterfaces::AdasInterfaces
)

# Windows only searches the exe's own directory + PATH for a DLL - same fix
# already used for df_tests.exe (modules/df/tests/CMakeLists.txt).
add_custom_command(TARGET sil POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "${DF_SIL_DIR}/Release/df_sil.dll"
        "$<TARGET_FILE_DIR:sil>"
)
