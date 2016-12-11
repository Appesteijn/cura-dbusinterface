project(cura-dbusinterface)

cmake_minimum_required(VERSION 2.8.12)

install(DIRECTORY DBusInterface DESTINATION ${CMAKE_INSTALL_PREFIX}/lib/cura/plugins)
