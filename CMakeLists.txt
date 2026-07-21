cmake_minimum_required(VERSION 3.22)
project(adas-sil VERSION 0.1.0 LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)

# Guarded (plan.md item 13, docs/build_superbuild_aggregator_plan.md §4) - see
# modules/df/CMakeLists.txt's identical guard for the full rationale; sil is
# always the aggregator's primary, so any of these three may already be
# in-tree (add_subdirectory'd) rather than a Conan package.
if(NOT TARGET AdasInterfaces::AdasInterfaces)
    find_package(AdasInterfaces REQUIRED)
endif()
if(NOT TARGET AdasDf::AdasDf)
    find_package(AdasDf REQUIRED)
endif()
if(NOT TARGET AdasVdy::AdasVdy)
    find_package(AdasVdy REQUIRED)
endif()

add_executable(sil main.cpp)
target_link_libraries(sil PRIVATE
    AdasInterfaces::AdasInterfaces
    AdasDf::AdasDf
    AdasVdy::AdasVdy
)

# Runtime DLL deployment (plan.md item 13, found while verifying the
# aggregator - docs/build_superbuild_aggregator_plan.md §8.2) - when df_sil/
# vdy_sil are packaged Conan deps, Conan's own conanrun.bat environment puts
# their .dll next to sil.exe's search path already (unchanged, existing
# behavior). When they're in-tree targets instead (aggregator
# add_subdirectory()), there is no package/conanrun.bat for them at all, so
# nothing else copies df_sil.dll/vdy_sil.dll next to sil.exe - guarded on
# TARGET so this only ever fires for the in-tree case.
if(TARGET df_sil)
    add_custom_command(TARGET sil POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different $<TARGET_FILE:df_sil> $<TARGET_FILE_DIR:sil>
    )
endif()
if(TARGET vdy_sil)
    add_custom_command(TARGET sil POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different $<TARGET_FILE:vdy_sil> $<TARGET_FILE_DIR:sil>
    )
endif()
