cmake_minimum_required(VERSION 3.22)
project(adas-sil VERSION 0.1.0 LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)

find_package(AdasInterfaces REQUIRED)
find_package(AdasDf REQUIRED)
find_package(AdasVdy REQUIRED)

add_executable(sil main.cpp)
target_link_libraries(sil PRIVATE
    AdasInterfaces::AdasInterfaces
    AdasDf::AdasDf
    AdasVdy::AdasVdy
)
